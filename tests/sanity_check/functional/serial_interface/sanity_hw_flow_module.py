# author: christoph.dehm@thalesgroup.com
# responsible:
# location: Berlin
#
# jira: xxx
# feature:
#
# INTENTION:
# check the HW-flow control of Unicorn of the module side
# this check works only over the serial interface
# it runs also over USB, but then it does not check the hw flow control!
# if QCT-Module: USB has to be disabled (by McTv4) or unplugged totally to let the module go into sleep mode
# if Jakarta:
#   it is not recommended to use JAKARTA for this test, reason:
#   the timing of the sleep cycle depends on th network timer of the base station controller.
#   it may vary between 0.64 and 2.12 seconds. So it may work and may not work with Unicorn 5.1.0 !!!!!!

import unicorn
from dstl.network_service.register_to_network import dstl_enter_pin
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_part_number import dstl_check_or_read_part_number
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_hwid import dstl_get_hwid
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_identification import dstl_get_defined_ati_parameters
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.devboard.devboard import dstl_turn_module_usb_off_via_dev_board, dstl_turn_module_usb_on_via_dev_board\
    , dstl_check_if_urc_set, dstl_set_urc, dstl_get_dev_board_version

import re
import time

class Test(BaseTest):

    def enable_cyclic_sleep_standard(test):
        if re.search(test.dut.project, 'MIAMI|BOBCAT|VIPER|SERVAL'):
            test.dut.at1.send_and_verify('AT^SCFG="MeopMode/PwrSave",enabled,"52","50"')

        elif re.search(test.dut.project, 'JAKARTA'):
            # AT^SPOW= <mode>,<timeout> , (time range of <awake>)
            # 3 ... 65535 		In SLEEP mode (<mode>=2), time in milliseconds the ME remains awake after the last sent character.
            # Minimum value: 3 ms, recommended 1000 ms. <timeout> values below 3 are denied with ERROR.
            # 3 ... 255 		In SLEEP mode (<mode>=2), active period of CTS0/CTS1 in milliseconds when ME is listening
            # to paging messages from the base station
            test.dut.at1.send_and_verify('AT^SPOW=2,100,20')
        pass

    def disable_cyclic_sleep(test):
        if re.search(test.dut.project, 'MIAMI|BOBCAT|VIPER|SERVAL'):
            test.dut.at1.send_and_verify('AT^SCFG="MeopMode/PwrSave",disabled')

        elif re.search(test.dut.project, 'JAKARTA'):
            # AT^SPOW= <mode>,<timeout> , (time range of <awake>)
            # 3 ... 65535 		In SLEEP mode (<mode>=2), time in milliseconds the ME remains awake after the last sent character.
            # Minimum value: 3 ms, recommended 1000 ms. <timeout> values below 3 are denied with ERROR.
            # 3 ... 255 		In SLEEP mode (<mode>=2), active period of CTS0/CTS1 in milliseconds when ME is listening
            # to paging messages from the base station

            ret = False
            while not ret:
                test.dut.at1.send('AT^SPOW=1,0,0', timeout=3)
                ret = test.dut.at1.wait_for("OK", timeout=1)
        pass

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        print(test.dut.at1.settings)
        print(test.dut.at1.name)

        if 'asc' not in test.dut.at1.name:
            test.log.error('')
            test.log.critical('serial interface is USB and not ASC - please change - ABORT!')
            test.log.error('')
            test.expect(False, critical=True)


        serial_settings = test.dut.at1.settings
        hw_flow = serial_settings['rtscts']
        if not hw_flow:
            test.log.error('')
            test.log.error('serial interface is not configured to HW-flow! - we will change this now!')
            test.log.error('')
            test.dut.at1.reconfigure({"rtscts": True})
            print(test.dut.at1.settings)



        test.dut.dstl_detect()

        mct_ver = test.dut.dstl_get_dev_board_version()
        if "MC-Test3" in mct_ver:
            test.log.error('')
            test.log.error('if MCTv3 is in use, then please unplug modules USB cable otherwise sleep mode is not reached!')
            test.log.error('')
            time.sleep(12)

        test.log.step('Step 3: disable USB to reach power sleep modes of the module')
        test.dut.dstl_turn_module_usb_off_via_dev_board()
        test.dut.dstl_switch_off_at_echo(serial_ifc=0)

        # module can sleep only in case USB is OFF during restart !!!
        test.dut.dstl_restart()

    def run(test):
        test.log.info("Turn on flow control of the interface setting")
        # equivalent notation in local.cfg
        # dut_asc_0 = COM3,115200,8,N,1,1,no,yes,no
        test.dut.at1.reconfigure({
            #"baudrate":115200,
            "rtscts": True
        })
        # is it possible to READ the at1-interface configuration ?
        # it would be nice to have such method to check if the setting is really correct.


        test.log.info("Activate hw flow and power save settings of the module")
        test.dut.at1.send_and_verify('at\q3')

        test.log.info("check module settings and interface")
        test.dut.at1.send_and_verify('AT&V')

        test.log.info("enable URCs of McTest to see that the module goes into power sleep")
        test.dut.devboard.send_and_verify('mc:urc=SER')

        # run 1st check only with QCT products:
        if re.search(test.dut.project, 'MIAMI|BOBCAT|VIPER|SERVAL'):
            test.dut.at1.send_and_verify('AT^SCFG="MeopMode/PwrSave"')
            test.dut.at1.send_and_verify('AT^SQPORT?', 'O')  # only with Serval, maybe with Viper

            test.log.info("1. we use short timing of 900ms sleep periode - this is working with Unicorn 5.1.0")
            test.dut.at1.send_and_verify('AT^SCFG="MeopMode/PwrSave",enabled,"9","10"')
            test.dut.at1.send_and_verify('AT^SCFG="MeopMode/PwrSave"')

            ret = test.dut.devboard.wait_for_strict('CTS0: 1', timeout=6)
            if not ret:
                test.log.error("CTS0 did not change to inactive, it seems power save mode was not reached!")
                test.fail()

            for i in range(10):
                test.log.info("  ---       1st loop {}:  ---".format(i))
                test.expect(test.dut.at1.send_and_verify("at+cgmm"))
                test.sleep(6)
                test.expect(test.dut.at1.send_and_verify("at+cgmi"))
                test.sleep(7)

        elif re.search(test.dut.project, 'JAKARTA'):
            test.dut.dstl_register_to_network()
            test.sleep(7)

        # run 2nd check with QCT and JAKARTA:

        # in case of Jakarta: Cyclic Sleep works only with network!

        test.log.info("2. we use default value from AT-Spec of 5200ms sleep periode - this fails with Unicorn 5.1.0")
        test.enable_cyclic_sleep_standard()  # "MeopMode/PwrSave",enabled,"52","50" or SPOW for Jakarta
        test.sleep(7)
        ret = test.dut.devboard.wait_for_strict('CTS0: 1', timeout=6)
        if not ret:
            test.log.error("CTS0 did not change to inactive, it seems power save mode was not reached!")
            test.fail()

        for i in range(100):
            test.log.info("  ---       2nd loop {}: ---".format(i))
            test.dut.at1.send_and_verify("at+cgmm")
            test.sleep(6.1)
            test.dut.at1.send_and_verify("at+cgmi")
            test.sleep(7.2)
            test.dut.at1.send_and_verify("at+cgmr")
            test.sleep(7.3)



    def cleanup(test):
        """ Cleanup method.
        """
        dstl_turn_module_usb_on_via_dev_board(test.dut)
        test.dut.devboard.send_and_verify('mc:urc=OFF')

        time.sleep(1)

        test.disable_cyclic_sleep()
        test.dut.at1.send_and_verify('ati1')

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')
        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')


if "__main__" == __name__:
    unicorn.main()
