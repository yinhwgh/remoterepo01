# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107215.001 uw_panic_output
# jira: SRV04-222, SRV04-42
# feature:
# docu: https://confluence.gemalto.com/display/IWIKI/Serval4.0+New+AT+Commands

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import dstl.embedded_system.embedded_system_configuration
from dstl.auxiliary.restart_module import dstl_restart
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board, dstl_switch_off_at_echo, \
    dstl_switch_on_at_echo


class Test(BaseTest):
    appname = ''

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')

        # Workaround for missing dut_log interface - now it is prerequisite for validation PCs
        # if test.dut.log is not None:
        # test.dut.log.open()     # channel for debug output

        test.dut.dstl_detect()
        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        test.appname = 'panicworld.bin'
        ret, err_msg = test.dut.dstl_install_app(test.appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        # restart not needed here: test.dut.dstl_restart()

        # switch to +CMEE:1 to see the numeric error code and store setting:
        test.expect(test.dut.at1.send_and_verify("at+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("at&w"))
        test.dut.at2.send("AT")     # only to

        # set and check settings before all starts
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/URC,OFF'))  # necessary for this test
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?"))

    def run(test):
        """
        Intention:
        Check SDK Example panicworld.bin. Here on ASC some specific output should appear in case a kernel panic appears.
        Prerequisites: the app panicworld.bin from SDK examples
        """

        # loglevel = "0"
        test.log.step('\n_______Step 1: Start app and check both UART interfaces for correct output')
        # set output channel to different one than current (Serval needs this):
        # test.dut.dstl_set_uw_trace_interface()  # does not work on it's own IF number!
        # ret, ifnum = test.dut.dstl_get_sqport("at1")
        # test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at2"))
        # test.expect(test.dut.at2.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))

        test.expect(test.dut.at2.send_and_verify("AT^SFSA=LS,A:/"))

        test.dut.dstl_start_app(test.appname, device_interface="at2")
        # special handling in case AT1 is an USB port. At least AT2 has to be ASC!
        if 'usb' in test.dut.at1.name:
            test.dut.at1.close()

        # check PANIC output on ASC0 and ASC1:
        if 'usb' not in test.dut.at1.name:
            test.expect(test.dut.at1.wait_for_strict(
                '.*GINA Panic:.*I\'m in Panic! 42 times.*panicworld.c, line \d{2,3}.*',
                timeout=5))
        test.expect(test.dut.at2.wait_for_strict(
            '.*GINA Panic:.*I\'m in Panic! 42 times.*panicworld.c, line \d{2,3}.*',
            timeout=5))

        test.sleep(5)
        # Module is in CrashDump mode - nearly off, check if it is really off:
        test.expect(test.dut.devboard.send_and_verify("MC:ASC0?",
                                                      ". *RTS0: 0.*CTS0: 0.*DSR0: 0.*DCD0: 0.*RING0:0.*OK.*",
                                                      append=True))
        test.dut.dstl_turn_off_vbatt_via_dev_board()
        test.dut.dstl_turn_on_vbatt_via_dev_board()
        test.dut.dstl_turn_on_igt_via_dev_board(time_to_sleep=2)
        time.sleep(15)
        if 'usb' in test.dut.at1.name:
            test.dut.at1.open()

        state, running_app = test.dut.dstl_get_running_app()
        if running_app is not "":
            test.expect(False, msg="running app found, but there should not be a running app anymore!")

        # test.dut.dstl_stop_running_app(test.appname, device_interface="at1")
        pass

    def cleanup(test):
        """ Cleanup method.
            disable Userware/Autostart otherwise bad influence to following tests
        """
        ret = test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1")
        if not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2")
        elif not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at3")

        # switch back to default user profile settings:
        test.expect(test.dut.at1.send_and_verify("at&f"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        # set back to disabled autostart and disabled output interface
        test.expect(test.dut.dstl_set_uw_autostart_state(state='0'))

        # enable ECHO function on McTest:
        test.dut.dstl_switch_on_at_echo(serial_ifc=0)

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
