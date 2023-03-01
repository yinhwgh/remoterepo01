# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107098.001
# jira: SRV04-147, SRV04-93
# feature: LM0008370.001 (viper2)
# docu: https://confluence.gemalto.com/display/IWIKI/Serval4.0+New+AT+Commands
#       https://confluence.gemalto.com/display/IWIKI/Serval+Embedded+-+LM0008370.001+Serval+EP%3A+Securing+DAM


import time
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
import dstl.embedded_system.embedded_system_configuration
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file, \
    dstl_list_directory
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo
from os.path import realpath, dirname, join, isfile


class Test(BaseTest):
    appname = 'logging.bin'
    second_appname = 'helloworld.bin'
    summary_msg = ''

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()

        test.dut.at2.open()  # channel for userware output
        test.dut.log.open()  # channel for debug output

        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        # switch to +CMEE:1 to see the numeric error code and store setting:
        test.expect(test.dut.at1.send_and_verify("at+CMEE=1"))
        test.expect(test.dut.at1.send_and_verify("at&w"))

        test.expect(test.dut.at1.send_and_verify('at^scfg=userware/trace/URC,OFF'))     # not necessary for this test

        # if autostart is enabled, then disable it and restart - new state is active after restart only!
        # otherwise the autostart-app can not be renewed/changed
        res, state = test.dut.dstl_get_uw_autostart_state()
        if state == '1':
            test.log.info('\n_______Step 1: check current states')
            test.dut.dstl_set_uw_autostart_state(state="Off")
            test.dut.dstl_restart()

        ret, err_msg = test.dut.dstl_install_app(test.appname, to_secure_area=False)
        # test._install_app(test.appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        ret, msg = test.dut.dstl_install_app(test.second_appname)
        # test._install_app(test.second_appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        dirlist = test.dut.dstl_list_directory('A:/')
        if "oem_app.bin" in dirlist:
            # delete oem_app and copy logging.bin to oem_app to be sure correct autostart app is used
            test.expect(test.dut.at1.send_and_verify("at^SFSA=remove,A:/oem_app.bin", "OK"))

        if not test.expect(test.dut.at1.send_and_verify(f"at^SFSA=copy,A:/{test.appname},A:/oem_app.bin", "OK")):
            dirlist = test.dut.dstl_list_directory('A:/')  # list_flag='')
            if "oem_app.bin" not in dirlist:
                test.expect(False, critical=True, msg=" Important app oem_app.bin is NOT in the modules FFS. "
                                                      "Necessary for this TC - ABORT")

        # now do it also for SERVAL - with sw048E of Serval it supports also the hidden FFS
        # if test.dut.project is 'VIPER':
            # register 'logging.bin' into hidden FFS
            # ret, msg = test.dut.uw_dstl_register_app(test.appname)
            # if not ret:
            #     test.expect(False, critical=True, msg=err_msg)

            # register 'oem_app.bin' into hidden FFS
        ret, msg = test.dut.dstl_uw_register_app("oem_app.bin")
        if not ret:
            test.expect(False, critical=True, msg=err_msg)
        '''
        else:
            if test.second_appname not in dirlist:
                test.expect(False, critical=True,
                            msg=" Important second app is NOT in the modules FFS. Necessary for this TC, step 5 -ABORT")
        '''
        pass

    def run(test):
        """
        Intention:
        Check for Userware/Autostart and verify default and user defined timing
        Prerequisites: a simple user ware/app, i.E. helloworld.bin which is called oem_app.bin
        """
        # ________________________________________________________________________________
        test.log.step('\n_______Step 1: check current states')
        res, state = test.dut.dstl_get_uw_autostart_state()
        test.log.info("Userware/Autostart: {}".format(state))

        res, delay = test.dut.dstl_get_uw_autostart_delay()
        test.log.info("Userware/Autostart/Delay: {}".format(delay))
        res, autostart_appname = test.dut.dstl_get_uw_autostart_appname()
        test.log.info("Userware/Autostart/AppName: {}".format(autostart_appname))

        # ________________________________________________________________________________
        test.log.step('\n_______Step 2: check autostart settings')
        test.dut.dstl_set_uw_autostart_state(state="On")
        test.expect(test.dut.dstl_set_uw_autostart_delay(delay="4040"))

        test.expect(test.dut.dstl_set_uw_autostart_state(state="1"))
        state = test.expect(test.dut.dstl_get_uw_autostart_state())
        print("Userware/Autostart: ", state)
        delay = test.expect(test.dut.dstl_get_uw_autostart_delay())

        # ________________________________________________________________________________
        test.log.step('\n_______Step 3: check autostart for illegal delays')
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,0", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,30001", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,99999", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,2010030", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,-a", "+CME ERROR: 21"))
        test.expect(test.dut.at1.send_and_verify("at^SCFG=Userware/autoStart/delay,-5000", "+CME ERROR: 21"))

        # ________________________________________________________________________________
        test.log.step('\n_______Step 4: check autostart enabled for different delays on helloworld.bin')
        # set output channel to different one than current (Serval needs this):
        # test.dut.dstl_set_uw_trace_interface()  # does not work on it's own IF number!
        ret, ifnum = test.dut.dstl_get_sqport("at2")
        print("sqport: ", ifnum)
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum))

        ret = test.dut.dstl_is_uw_app_installed("oem_app.bin")
        offset = 5.40  # estimated with Serval3_048
        if ret:
            delays = [2500, 3000, 3500, 4500, 5000, 11200, 30000, 2000]
            # delays = [2500, 3000, 3500, 4500, 5000, 11200, 30000, 2000]
#            delays = [2500, 3500, 5000]
            for current_delay in delays:
                test.log.step(' -- sub step4: set autostart delay to {} and check timing --'.format(current_delay))
                test.expect(test.dut.dstl_set_uw_autostart_delay(delay=current_delay))
                # waitfor:  ^SUSRW: 2,"[1] Critical message 0"

                time1 = time.perf_counter()

                if 'dut_asc_' in test.dut.at2.name:
                    # wait for SYSSTART and begin timer with this URC
                    test.dut.at1.send_and_verify('at+CFUN=1,1')
                    ret = test.dut.at2.verify_or_wait_for('.*CONNECT USERWARE TRACE.*', timeout=45)
                    if ret:
                        offset = 0  # we do not need and offset, we can mesaure very accurate now
                        time1 = time.perf_counter()
                else:
                    test.dut.dstl_restart()

                ret = test.expect(
                    test.dut.at2.verify_or_wait_for('.*\[1\] Critical message 0.*', timeout=32))
                time2 = time.perf_counter()
                current_delay_insec = current_delay / 1000
                if not ret:
                    test.dut.at1.send_and_verify("at^SUSRW=5", "OK")
                    resultmsg = "UW Autostart Delay with configured delay of {:.1f} sec. FAILED on {}. "\
                        .format(current_delay_insec, test.dut.at2.name)
                    test.log.error(resultmsg)
                    test.summary_msg += ' delay: {} failed, begin of output of app not found on port {}\n'\
                        .format(current_delay_insec, test.dut.at1.name)
                    time.sleep(8)
                else:
                    duration = time2 - time1 - offset    # -5.40 sec. from AT+CFUN=1,1 to SYSSTART
                    allowed_range = 200
                    low_border = (current_delay-allowed_range)/1000
                    high_border = (current_delay+allowed_range)/1000
                    print("min/max", low_border, high_border)
                    if (duration >= low_border) and (duration <= high_border):
                        resultmsg = "UW Autostart Delay measured delay of: {:.1f} sec. within configured delay " \
                                    "of {:.1f} sec. +-{:.1f} ms"\
                            .format(duration, current_delay_insec, allowed_range/1000)
                        test.expect(True, msg=resultmsg)
                        test.summary_msg += '\n delay: {} passed with correct timing'.format(current_delay_insec)
                    else:
                        resultmsg = "UW Autostart Delay measured delay of: {:.1f} sec. is out of configured delay " \
                                    "of {:.1f} sec. +-{:.1f} "\
                            .format(duration, current_delay_insec, allowed_range/1000)
                        test.expect(False, msg=resultmsg)
                        test.summary_msg += '\n check delay: {} passed with wrong timing {}'.format(
                            current_delay_insec, duration)

                test.expect(test.dut.dstl_stop_running_app())
                tmp = test.dut.at2.read(append=False)

        test.log.step('_______Step 4: SUMMARY: ')
        test.log.step(test.summary_msg)

        # ________________________________________________________________________________
        test.log.step('\n_______Step 5: start 2nd app while autostart app is running and check CME output')
        test.dut.dstl_restart()

        test.dut.dstl_uw_register_app("logging.bin")

        ok, autostart_appname = test.dut.dstl_get_running_app()
        print("Autostart app found:", autostart_appname)
        time.sleep(4)
        ok, autostart_appname = test.dut.dstl_get_running_app()
        print("Autostart app found:", autostart_appname)
        if not ok or ('oem_app.bin' not in autostart_appname):
            if 'oem_app.bin' in autostart_appname:
                test.expect(True,
                            msg="After reboot with autostart: correct app is not running, "
                                "dstl_get_running_app returned with FAILED!")
            else:
                test.expect(False,
                            msg=f"After reboot with autostart: no or wrong app ({autostart_appname}) is running "
                                f"- FAILED!")
            test.expect(False,
                        msg=f"After reboot with autostart: no or wrong app ({autostart_appname}) is running - FAILED!")
        elif 'oem_app.bin' in autostart_appname:
            test.expect(True, msg="running app found, now we will stop it.")

        if test.dut.project is 'SERVAL' and _get_sw_version_number(test.dut) <= '048D':
            # SERVAL supports only one running app at one time
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=1,A:/" + test.second_appname, ".*CME ERROR: .*"))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=5"))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=2,A:/" + test.second_appname, ".*CME ERROR: .*"))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=1,A:/" + test.appname, ".*CME ERROR: .*"))
        else:
            # VIPER now supports apps running in parallel
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=1,A:/" + test.second_appname))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=5", ".*\^SUSRW: a:/.*bin.*\^SUSRW: a:/.*bin.*OK.*"))
            test.log.info(test.dut.dstl_uw_get_susrw_error_text(''))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=1,A:/" + test.second_appname, ".*\^SUSRW: 9.*ERROR.*"))
            test.log.info(test.dut.dstl_uw_get_susrw_error_text(''))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=2,A:/" + test.second_appname))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=5", ".*\^SUSRW: a:/.*bin.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=2,A:/" + test.appname, '.*\^SUSRW: 19'))
            test.log.info(test.dut.dstl_uw_get_susrw_error_text(''))
            # test.expect(test.dut.at1.send_and_verify("at^SUSRW=2,A:/oem_app.bin"))
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=5", ".*\^SUSRW: .*OK.*"))

        # ________________________________________________________________________________
        test.log.step('\n_______Step 6: removing current running app')
        if test.dut.project is 'SERVAL':
            test.log.info(" not possible with Serval - we overjump this step")
        else:
            test.expect(test.dut.at1.send_and_verify("at^SUSRW=3,A:/oem_app.bin", ".*\^SUSRW: 9.*ERROR.*"))
            test.log.info(test.dut.dstl_uw_get_susrw_error_text(''))

        # ________________________________________________________________________________
        test.log.step('\n_______Step 7: check stopping of autostarted app')
        # do a restart again with delay setting from previous step
        test.dut.dstl_restart()
        time.sleep(15)
        ok, autostart_appname = test.dut.dstl_get_running_app()
        autostart_appname = autostart_appname.replace('a:/', '')
        #
        #    test.expect(True, msg="After reboot with autostart: correct app () is running")
        if ok and not autostart_appname:
            test.log.info('no autostart app found, maybe autostart delay has not triggered so far, waiting...')
            time.sleep(5)
            ok, autostart_appname = test.dut.dstl_get_running_app()

        if not ok or (autostart_appname != 'oem_app.bin'):
            if autostart_appname == 'oem_app.bin':
                test.expect(True,
                            msg="After reboot with autostart: correct app is not running, "
                                "dstl_get_running_app returned with FAILED!")
            else:
                test.expect(False,
                            msg=f"After reboot with autostart: no or wrong app ({autostart_appname}) is running "
                                f"- FAILED!")
            test.expect(False,
                        msg=f"After reboot with autostart: no or wrong app ({autostart_appname}) is running - FAILED!")
        elif autostart_appname == 'oem_app.bin':
            msg = f"running app {autostart_appname} found, now we will stop it."
            test.expect(True, msg)

        test.expect(test.dut.at1.send_and_verify("at^SUSRW=2,a:/{}".format(autostart_appname)))
        ok, autostart_appname = test.dut.dstl_get_running_app()
        if ok and (autostart_appname is not ''):
            test.expect(False, msg="After stopping app module still shows a runnung app: {} - FAILED!".format(
                autostart_appname))

        res, state = test.dut.dstl_get_uw_autostart_state()
        test.dut.at1.send_and_verify('at^scfg="Userware/Trace/Interface"')

        # ________________________________________________________________________________
        test.log.step('\n_______Step 8: disable autostart and check if it stays off')
        test.dut.dstl_set_uw_autostart_state(state="0")
        test.dut.dstl_restart()
        time.sleep(3)
        resp = test.dut.at1.last_response
        if 'CONNECT USERWARE TRACE' in resp or 'Hello World!' in resp:
            test.expect(False, "running app {} found - should not, or some other problem found.".format({}))
        resp2 = test.dut.at2.last_response
        if 'CONNECT USERWARE TRACE' in resp or 'Hello World!' in resp:
            test.expect(False, "running app {} found - should not, or some other problem found.".format({}))

        ok, autostart_appname = test.expect(test.dut.dstl_get_running_app())
        if not ok or autostart_appname is not '':
            test.expect(False, "running app {} found - should not, or some other problem found.".format({}))

        pass

    def cleanup(test):
        """Cleanup method.
        disable Userware/Autostart otherwise bad influence to following tests
        remove all installed files
        """
        # disable all running apps:
        ok, running_appname = test.dut.dstl_get_running_app()
        while running_appname is not '':
            test.expect(test.dut.at1.send_and_verify(f"at^SUSRW=2,{running_appname}"))
            ok, running_appname = test.dut.dstl_get_running_app()

        # uninstall all apps from hidden ffs area:
        ok, dict_list = test.dut.dstl_uw_get_installed_app()
        for k in dict_list.keys():
            test.expect(test.dut.dstl_uw_deinstall_app(k))

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
        pass

def _get_sw_version_number(device):
    print('sw:', device.software)
    print('sw nr:', device.software_number)

    real_sw_vers_nr = 0
    sw_vers_post_characters = ""
    swversionidx = device.software_number.rfind('_')

    if swversionidx:
        sw_number = device.software_number[swversionidx + 1:]
        return sw_number
        """
        m1 = re.search(r"\d{1,3}", sw_number)
        real_sw_vers = m1.group(0)

        m2 = re.search(r"[A-Z]+", sw_number)  # \D+
        if m2 is not None:
            sw_vers_post_characters = m2.group(0)

        real_sw_vers_nr = int(real_sw_vers)  # int(device.software_number[swversionidx+1:])
        """
    return '999'

if "__main__" == __name__:
    unicorn.main()
