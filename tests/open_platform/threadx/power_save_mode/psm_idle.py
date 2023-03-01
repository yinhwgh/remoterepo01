# author: christoph.dehm@thalesgroup.com
# responsible: christoph.dehm@thalesgroup.com
# location: Berlin
# TC0107176.001
# jira: SRV04-191
# feature: LM0007906.001, CR02155 Introduction of Embedded Processing
# docu: see HID and powerpoint from Jacques
# prerequisite: USB has to be disabled, so use ASC0+1 as interfaces in the device.cfg only!

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
import dstl.embedded_system.embedded_system_configuration
import dstl.network_service.register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.miscellaneous.access_ffs_by_at_command import dstl_open_file, dstl_write_file, dstl_close_file
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo, dstl_switch_on_at_echo, \
    dstl_turn_module_usb_off_via_dev_board
from os.path import realpath, dirname, join, isfile


class Test(BaseTest):
    appname = ''
    pwr_save_periode = 0  # 52 by default (in 100ms steps)
    pwr_save_awake = 0  # 50 by default (in 100ms steps)
    pwr_save_timeout = 0

    def extract_average_current_consumption(test):
        '''
            ToDo:
            - move single functions to devboard/devboard.py as a helper function
            - add additional calculating cylce with parameter <time> to collect
            full output from McTest over given time (i.E 1 minute) and sum up
            all received values within CTS-low phase and give back the average of that

        :return:
            average value [as float in mA], number of measurement values
        '''

        # temp = test.dut.devboard.last_response
        dummy = test.dut.devboard.read()
        # test.expect(test.dut.devboard.wait_for_strict('.*CTS0: 1.*', timeout=test.pwr_save_timeout))
        # test.expect(test.dut.devboard.wait_for_strict('.*CTS0: 0.*', timeout=test.pwr_save_timeout
        # , append=True))
        test.expect(test.dut.devboard.wait_for_strict('CTS0: 1', timeout=12))
        test.expect(test.dut.devboard.wait_for_strict('.*CTS0: 0.*', timeout=12))

        resp0 = test.dut.devboard.last_response

        if 'CTS1: 1' in resp0:
            resp1 = resp0.partition('CTS1: 1')
            resp2 = resp1[2]
        else:
            resp2 = resp0

        if 'CTS0: 0' in resp2:
            resp3 = resp2.rpartition('CTS0: 0')
            resp4 = resp3[0]
        else:
            resp4 = resp2

        current_list = re.findall(r"I= +[0-9]+.[0-9]+mA", resp4)
        # for listentry in current_list:
        #    listentry = listentry.replace("I= ", "")
        #    listentry = listentry.replace("mA", "")
        # print("list: ", current_list)

        if len(current_list) <= 1:
            test.log.error("no current values found within output of McTest")
            test.dut.devboard.send_and_verify("mc:ccmeter=off")
            return 0.0, 0

        float_temp = 0.0
        # lets ignore 1st value, mostly it is the value from last state before - so too high for us!
        for i in range(1, len(current_list), 1):
            listentry = current_list[i]
            listentry = listentry.replace("I= ", "")
            listentry = listentry.replace("mA", "")
            float_temp += float(listentry)

        float_average = float_temp / len(current_list)
        return float_average, len(current_list)-1

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')

        test.pwr_save_periode = 82  # 52 by default (in 100ms steps)
        test.pwr_save_awake = 10  # 50 by default (in 100ms steps)
        test.pwr_save_timeout = (test.pwr_save_periode + test.pwr_save_awake) / 10 + 5  # in seconds!

        test.expect(test.dut.at1.send_and_verify("at^scfg=meopmode/pwrsave,disabled,{},{}"
                                                 .format(test.pwr_save_periode, test.pwr_save_awake)))
        test.dut.devboard.send_and_verify("mc:vusb?")
        test.dut.devboard.last_response
        # if "VUSB: ON" in resp:
        #    test.dut.dstl_turn_module_usb_off_via_dev_board()
        # restart necessary in case USB was connected before - otherwise module would never go to sleep
        #    test.dut.dstl_restart()
        #    test.dut.log.open()     # channel for debug output

        test.dut.dstl_detect()
        ret, ifnum = test.dut.dstl_get_sqport("at1")
        if int(ifnum) >= 3:
            test.expect(False, critical=True, msg="at1 is USB or MUX interface - TC has to run on ASC only - abort!")
        ret, ifnum = test.dut.dstl_get_sqport("at2")
        if int(ifnum) >= 3:
            test.expect(False, critical=True, msg="at2 is USB or MUX interface - TC has to run on ASC only - abort!")

        if test.dut.log is not None:
            test.dut.log.open()     # channel for debug output

        # disabling ECHO function on McTest to have a better readable log file:
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)
        test.dut.dstl_switch_off_at_echo(serial_ifc=1)

        test.appname = 'psm_idle.bin'
        ret, err_msg = test.dut.dstl_install_app(test.appname)
        if not ret:
            test.expect(False, critical=True, msg=err_msg)

        # enable McT URCs for serial signals:
        test.dut.devboard.send_and_verify("mc:urc=SER")

        # check for initial settings:
        test.expect(test.dut.at1.send_and_verify("at^scfg?"))

    def run(test):
        """
        Intention:
        - register module
        - start app psm_idle.bin
        - check for outputs, wait for module is in sleep mode
        - measure power consumption with McTv4 CCMeter
        """
        result_text = "\tAverage Current Consumption for SDK Demo App '{}' for networks:\n"\
            .format(test.appname)

        step_list = {"GSM", "CatM", "CatNB"}
        # result_list = {0.0, 0.0, 0.0}

        i = 0
        for step in step_list:
            i += 1
            test.log.step('\n_______Step {}.1: register to network: {}'.format(i, step))

            if "GSM" in step:
                test.dut.dstl_register_to_gsm()
            elif "CatM" in step:
                test.dut.dstl_register_to_lte()
            elif "CatNB" in step:
                test.dut.dstl_register_to_nbiot()

            test.log.step('\n_______Step {}.2: start app and wait for switch to power save mode [{}]'.format(i, step))
            test.expect(test.dut.at1.send_and_verify("at^scfg=Userware/Trace/Urc,on"))

            # ret, ifnum = test.dut.dstl_get_sqport("at1")
            # test.expect(test.dut.dstl_set_uw_trace_interface(interface_number=ifnum, device_interface="at2"))
            ret = test.dut.dstl_start_app(test.appname, device_interface="at2")
            test.dut.devboard.send_and_verify("mc:ccmeter=auto")
            if not ret:
                test.dut.at1.send_and_verify("at^sfsa=ls,A:/")
                test.dut.at1.send_and_verify("at^susrw=5")
                test.expect(False, critical=True, msg="App could not be started - abort")

            test.expect(test.dut.at2.wait_for_strict('.*PSM THREAD: ENTER PSM MODE REQ.*', timeout=90))
            # '.*PSM THREAD: Wait for psm complete event.*', timeout=60))
            time.sleep(15)

            test.log.step('\n_______Step {}.3: measure current consumption [{}]'.format(i, step))
            test.dut.devboard.send_and_verify("mc:ccmeter=auto")
            time.sleep(5)

            float_average, num_values = test.extract_average_current_consumption()
            result_text += "\t{}\t:\t{:.2f} mA  (over {} values)\n".format(step, float_average, num_values)
            test.log.info("\n ==> average current in sleep phase for network {}: {:.2f} mA of {} values \n"
                          .format(step, float_average, num_values))

            test.dut.devboard.send_and_verify("mc:ccmeter=off")

            # wait for active serial interface:
            test.expect(test.dut.devboard.wait_for('.*CTS0: 0.*', timeout=test.pwr_save_timeout))
            test.dut.dstl_stop_running_app(test.appname, device_interface="at2")
            test.expect(test.dut.at1.send_and_verify("at^scfg=meopmode/pwrsave,disabled"))

        test.log.info(" ======================================================================")
        test.log.info(result_text)
        pass

    def cleanup(test):
        # disable ccmeter at once, otherwise output of ccmeter has bad influence to other McT action!
        test.dut.devboard.send_and_verify("mc:ccmeter=off")

        # wait for active serial interface:
        test.dut.devboard.wait_for('.*CTS0: 0.*', timeout=test.pwr_save_timeout)
        test.expect(test.dut.at1.send_and_verify("at^scfg=meopmode/pwrsave,disabled"))
        test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/PowerMgmt/Suspend","0","0"'))

        test.dut.dstl_stop_running_app(test.appname, device_interface="at2")

        ret = test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at1")
        if not ret:
            test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at2")
        # elif not ret:
        #    test.dut.dstl_set_uw_trace_interface(interface_number="0", device_interface="at3")

        # set back to disabled autostart and disabled output interface
        test.expect(test.dut.dstl_set_uw_autostart_state(state='0'))
        test.expect(test.dut.dstl_set_uw_trace_interface(interface_number='0'))
        test.expect(test.dut.at1.send_and_verify("at^scfg=Userware/Trace/Urc,off"))

        test.expect(test.dut.at1.send_and_verify("at^scfg?"))

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
