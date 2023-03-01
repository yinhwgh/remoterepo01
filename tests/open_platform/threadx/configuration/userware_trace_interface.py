# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107099.001
# jira: SRV04-147, SRV04-93
# feature:
# docu: https://confluence.gemalto.com/display/IWIKI/Serval4.0+New+AT+Commands

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import dstl.embedded_system.embedded_system_configuration
from dstl.auxiliary.restart_module import dstl_restart
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo
from os.path import realpath, dirname, join, isfile


class Test(BaseTest):
    """
    TS checks if trace interface shows trace output for EP-apps on all available interfaces.
    EP-app: logging.bin
    Four AT-Interfaces have to be connected:
    AT1 as main interface to control everything
    AT2 as trace interface to check if output appears correct
    AT3+AT4 as 2nd trace interfaces to check if output appears correct too
    There is no specific restriction for AT1-4 as ASC0 or USB port!
    """

    appname = ''

    def setup(test):
        global appname
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')

        # if test.dut.log is not None:
        #    test.dut.log.open()     # channel for debug output

        # check, if all serial ports are available:
        if test.dut.at3 is None:
            test.log.error("step3 uses AT3, but it is not valid, please configure!")
            test.expect(False, critical=True)
        if test.dut.at4 is None:
            test.log.error("step4 uses AT4, but it is not valid, please configure!")
            test.expect(False, critical=True)

        test.dut.dstl_detect()
        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        appname = 'logging.bin'
        ret, err_msg = test.dut.dstl_install_app(appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        # test.dut.at3.close()    # workaround for IPIS100333553
        # test.log.warning("please check for a fix of DSTL_Restart() issue, reported under: IPIS100333553")
        test.dut.dstl_restart()
        # test.dut.at3.open()     # workaround for IPIS100333553

        # switch to +CMEE:1 to see the numeric error code and store setting:
        test.expect(test.dut.at1.send_and_verify("at+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("at&w"))
        # test.expect(test.dut.at1.send_and_verify("at+cpin=9999;+creg=2"))

        # set and check settings before all starts
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/URC,OFF'))     # not necessary for this test
        test.expect(test.dut.at1.send_and_verify("AT^SCFG?"))

    def run(test):
        """
        Intention:
        Check for AT^SCFG=Userware/Trace/Interface  in combination with AT^SCFG=Userware/Trace/Level
        Prerequisites: a simple user ware/app, i.E. logging.bin (for autostart it is renamed to oem_app.bin)
        """
        global appname

        # ________
        loglevel = "0"
        test.log.step('\n_______Step 1: check outputs with Trace interface AT1, loglevel '+loglevel)
        # set output channel to different one than current (Serval needs this):
        # test.dut.dstl_set_uw_trace_interface()  # does not work on it's own IF number!
        ret, ifnum = test.dut.dstl_get_sqport("at1")
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at2"))
        test.expect(test.dut.at2.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))

        test.dut.dstl_start_app(appname, device_interface="at2")
        # receive: 00:00:07:986 CRIT:logging.c,103: _txm_module_preamble: 0x4d4f4455
        # 00:00:07:986 CRIT:logging.c,148: [1] Critical message 0
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
        time.sleep(15)
        resp1 = test.dut.at1.last_response
        resp2 = test.dut.at1.read()

        test.dut.dstl_stop_running_app(appname, device_interface="at2")
        test.expect(test.dut.at1.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2"))

        print("last_resp of AT1:", resp1)
        print("read_resp of AT1:", resp2)
        if "Error message" in resp1 or "Error message" in resp2:
            test.log.error("step1: module shows Error message in output, but should not: FAILED!")

        # ________
        loglevel = "1"
        test.log.step(f'\n_______Step 2: check outputs with Trace interface AT2 ({test.dut_at2.name}), loglevel 1')
        ret, ifnum = test.dut.dstl_get_sqport("at2")
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at1"))
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))
        test.dut.dstl_start_app(appname, device_interface="at1")
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
        time.sleep(17)
        resp1 = test.dut.at2.last_response
        resp2 = test.dut.at2.read()

        test.dut.dstl_stop_running_app(appname, device_interface="at1")
        test.expect(test.dut.at2.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1"))

        print("last_resp of AT2:", resp1)
        print("read_resp of AT2:", resp2)
        if "High message" in resp1 or "High message" in resp2:
            test.log.error("step2: module shows High message in output, but should not: FAILED!")

        # ________
        loglevel = "2"
        test.log.step('\n_______Step 3: check outputs with Trace interface AT3, loglevel {}'.format(loglevel))
        if test.dut.at3 is None:
            test.log.error("step3 uses AT3, but it is not valid, overjumping step3!")
            test.expect(False, critical=True)
        else:
            ret, ifnum = test.dut.dstl_get_sqport("at3")
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at1"))
            test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))
            test.dut.dstl_start_app(appname, device_interface="at1")
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} HIGH:logging.c,\d{2,3}: \[[123]\] High message 2.*', timeout=8))
            time.sleep(17)
            resp1 = test.dut.at3.last_response
            resp2 = test.dut.at3.read()

            test.dut.dstl_stop_running_app(appname, device_interface="at1")
            test.expect(test.dut.at3.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1"))

            print("last_resp of AT3:", resp1)
            print("read_resp of AT3:", resp2)
            if "Info message" in resp1 or "Info message" in resp2:
                test.log.error("step3: module shows Info message in output, but should not: FAILED!")

        # ________
        loglevel = "3"  # Info
        test.log.step('\n_______Step 4: check outputs with Trace interface AT4, loglevel {}'.format(loglevel))
        if test.dut.at4 is None:
            test.log.error("step4 uses AT4, but it is invalid under Win7, overjumping step4!")
            test.expect(False, critical=True)
        else:
            ret, ifnum = test.dut.dstl_get_sqport("at4")
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at1"))
            test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))
            test.dut.dstl_start_app(appname, device_interface="at1")
            test.expect(test.dut.at4.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
            test.expect(test.dut.at4.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
            test.expect(test.dut.at4.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} HIGH:logging.c,\d{2,3}: \[[123]\] High message 2.*', timeout=8))
            test.expect(test.dut.at4.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} INFO:logging.c,\d{2,3}: \[[123]\] Info message 3.*', timeout=8))
            time.sleep(17)
            resp1 = test.dut.at4.last_response
            resp2 = test.dut.at4.read()

            test.dut.dstl_stop_running_app(appname, device_interface="at1")
            test.expect(test.dut.at4.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1"))

            print("last_resp of AT4:", resp1)
            print("read_resp of AT4:", resp2)
            if "Low message" in resp1 or "Low message" in resp2:
                test.log.error("step4: module shows Low message in output, but should not: FAILED!")

        # ________
        loglevel = "4"  # Low
        test.log.step('\n_______Step 5: check outputs with Trace interface AT1, loglevel '+loglevel)
        # set output channel to different one than current (Serval needs this):
        # test.dut.dstl_set_uw_trace_interface()  # does not work on it's own IF number!
        ret, ifnum = test.dut.dstl_get_sqport("at1")
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at2"))
        test.expect(test.dut.at2.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))

        test.dut.dstl_start_app(appname, device_interface="at2")
        # receive: 00:00:07:986 CRIT:logging.c,103: _txm_module_preamble: 0x4d4f4455
        # 00:00:07:986 CRIT:logging.c,148: [1] Critical message 0
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} HIGH:logging.c,\d{2,3}: \[[123]\] High message 2.*', timeout=8))
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} INFO:logging.c,\d{2,3}: \[[123]\] Info message 3.*', timeout=8))
        test.expect(test.dut.at1.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} LOW :logging.c,\d{2,3}: \[[123]\] Low message 4.*', timeout=8))
        time.sleep(15)
        resp1 = test.dut.at1.last_response
        resp2 = test.dut.at1.read()

        test.dut.dstl_stop_running_app(appname, device_interface="at2")
        test.expect(test.dut.at1.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2"))

        print("last_resp of AT1:", resp1)
        print("read_resp of AT1:", resp2)
        if "DBG message" in resp1 or "DBG message" in resp2:
            test.log.error("step5: module shows DBG output, but should not: FAILED!")

        # ________
        loglevel = "5"  # Debug
        test.log.step(f'\n_______Step 6: check outputs with Trace interface AT2 ({test.dut_at2.name}), loglevel 1')
        ret, ifnum = test.dut.dstl_get_sqport("at2")
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at1"))
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))
        test.dut.dstl_start_app(appname, device_interface="at1")
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} HIGH:logging.c,\d{2,3}: \[[123]\] High message 2.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} INFO:logging.c,\d{2,3}: \[[123]\] Info message 3.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} LOW :logging.c,\d{2,3}: \[[123]\] Low message 4.*', timeout=8))
        test.expect(test.dut.at2.wait_for_strict(
            '.*\d{2}:\d{2}:\d{2}:\d{3} DBG :logging.c,\d{2,3}: \[[123]\] DBG message 5.*', timeout=8))
        time.sleep(17)

        test.dut.dstl_stop_running_app(appname, device_interface="at1")
        test.expect(test.dut.at2.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1"))

        # ________
        loglevel = "6"  # ALL
        test.log.step('\n_______Step 7: check outputs with Trace interface AT3, loglevel {}'.format(loglevel))
        if test.dut.at3 is None:
            test.log.error("step7 uses AT3, but it is not valid, overjumping step7!")
            test.expect(False, critical=True)
        else:
            ret, ifnum = test.dut.dstl_get_sqport("at3")
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at1"))
            test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level,{}'.format(loglevel)))
            test.dut.dstl_start_app(appname, device_interface="at1")
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} CRIT:logging.c,\d{2,3}: \[[123]\] Critical message 0.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} ERR :logging.c,\d{2,3}: \[[123]\] Error message 1.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} HIGH:logging.c,\d{2,3}: \[[123]\] High message 2.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} INFO:logging.c,\d{2,3}: \[[123]\] Info message 3.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} LOW :logging.c,\d{2,3}: \[[123]\] Low message 4.*', timeout=8))
            test.expect(test.dut.at3.wait_for_strict(
                '.*\d{2}:\d{2}:\d{2}:\d{3} DBG :logging.c,\d{2,3}: \[[123]\] DBG message 5.*', timeout=8))
            time.sleep(17)
            resp1 = test.dut.at3.last_response
            resp2 = test.dut.at3.read()

            test.dut.dstl_stop_running_app(appname, device_interface="at1")
            test.expect(test.dut.at3.wait_for('.*CRIT:logging.c,\d+: cleanup: MY CLEANUP.*', 5))
            test.expect(test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1"))

            print("last_resp of AT3:", resp1)
            print("read_resp of AT3:", resp2)

        # ________
        # loglevel = "6"  # ALL
        test.log.step(f'\n_______Step 8: check outputs with Trace interface OFF and ALL loglevels enabled ({loglevel})')
        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/level'))
        test.dut.dstl_start_app(appname, device_interface="at1")
        time.sleep(17)

        test.dut.dstl_stop_running_app(appname, device_interface="at1")

        resp1 = test.dut.at1.last_response
        resp2 = test.dut.at1.read()

        if "message" in resp1 or "message" in resp2:
            test.log.error("step8: trace interface disabled, but output found: FAILED!")
        pass

    def cleanup(test):
        """Cleanup method.
        disable Userware/Autostart otherwise bad influence to following tests
        """

        ret = test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1")
        if not ret:
            ret = test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2")
        elif not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at3")

        # switch back to default user profile settings:
        test.expect(test.dut.at1.send_and_verify("at&f"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        # set back to disabled autostart and disabled output interface
        test.expect(test.dut.dstl_set_uw_autostart_state(state='0'))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number='0'))

        # enable ECHO function on McTest:
        test.dut.dstl_switch_on_at_echo(serial_ifc=0)

        test.dut.at3.close()    # workaround for IPIS100333553
        test.log.warning("please check for a fix of DSTL_Restart() issue, reported under: IPIS100333553")
        test.dut.dstl_restart()
        test.dut.at3.open()     # workaround for IPIS100333553

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
