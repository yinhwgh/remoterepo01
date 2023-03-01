# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107287.001
# jira: SRV04-147, SRV04-93
# issues: SRV03-3008 (IPIS100340724)
# feature: LM0007906.001 (dummy, correct features have to be assigned after reviewing CR02238)
# docu: https://confluence.gemalto.com/display/IWIKI/Serval4.0+New+AT+Commands

import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
import dstl.embedded_system.embedded_system_configuration
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file, dstl_list_directory
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo
from os.path import realpath, dirname, join, isfile

class Test(BaseTest):

    # appname = 'location.bin'   # former app used, now change to exception.bin due to IPIS100340724
    appname = 'exception.bin'   # this app leads to another crash without EXIT output
    if 'location' in appname:
        regexpr_end_msg = '\^SUSRW: 2,"Wait For Tracking Callback Signal..."'
    elif 'exception' in appname:
        regexpr_end_msg = '\^SUSRW: 2,"\(Exc1.*\) Too much APP exceptions - hold and unload APP completely"'

    summary_msg = ''
    resp1 = ''
    resp2 = ''
    # resp3 = ''

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.at2.open()     # channel for userware output
        # test.dut.log.open()     # channel for debug output
        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        # switch to +CMEE:1 to see the numeric error code and store setting:
        test.expect(test.dut.at1.send_and_verify("at+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/URC,ON'))     # not necessary for this test
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?"))

        ret, err_msg = test.dut.dstl_install_app(test.appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        pass

    def run(test):
        """
        Test Intention:
        start and stop an application lot of times in a loop
        """

        LOOP_MAX = 100
        loop_nr = 0

        while loop_nr < LOOP_MAX:
            loop_nr += 1

            test.log.info("\n       *****   loop: " + str(loop_nr) + "    *****")
            ret = test.dut.dstl_start_app(test.appname, device_interface="at1")
            test.expect(test.dut.at1.verify_or_wait_for(
                test.regexpr_end_msg, timeout=15))
            time.sleep(2)
            test.resp1 = test.dut.at1.last_response
            test.resp2 = test.dut.at2.last_response
            # test.resp3 = test.dut.log.last_response
            test.expect(test.dut.at1.send_and_verify("at^susrw=5"))

            rest = loop_nr % 10
            if not rest:
                # check each 10th loop to start already running app again:
                # based on issue SRV03-2754 / IPIS100340085
                ret = test.dut.dstl_start_app(test.appname, device_interface="at1")
                test.expect(test.dut.at1.send_and_verify("at^susrw=5"))
                time.sleep(2)

            test.dut.dstl_stop_running_app(test.appname, device_interface="at1")
            time.sleep(2)
            test.expect(test.dut.at1.send_and_verify("at^susrw=5", ".*susrw=5\r\r\nOK.*"))

        #test.log.step('_______Step 4: SUMMARY: ')
        #test.log.step(test.summary_msg)


    def cleanup(test):
        if "APPS Fatal" in test.resp1 or "APPS Fatal" in test.resp2:  # or "APPS Fatal" in test.resp3:
            test.expect(False, critical=False,
                        msg="EXIT found, please check known issue SRV03-2754 / IPIS100340085")
            test.dut.dstl_turn_off_vbatt_via_dev_board()
            test.dut.dstl_turn_on_vbatt_via_dev_board()
            test.dut.dstl_turn_on_igt_via_dev_board(time_to_sleep=2)
            time.sleep(5)

        # switch back to default user profile settings:
        test.expect(test.dut.at1.send_and_verify("at&f"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        test.dut.dstl_switch_on_at_echo(serial_ifc=0)

        # set back to disabled autostart and disabled output interface
        test.expect(test.dut.dstl_set_uw_autostart_state(state='0'))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number='0'))
        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
