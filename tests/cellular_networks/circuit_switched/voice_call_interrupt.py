#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0091959.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import check_urc
from dstl.configuration import network_registration_status
from dstl.status_control import extended_indicator_control
from dstl.configuration import shutdown_smso
from dstl.auxiliary.devboard import devboard

import re

class Test(BaseTest):
    '''
    TC0091959.001 - VoiceCallInterrupt
    Intention: Check behaviour when voice call is interrupted by shut-down.
    Subscriber: 3， dut, remote and MCTest on dut
    '''
    def setup(test):
        test.log.info("********** Set DUT be ready for call ************")
        test.dut.dstl_detect()

        test.log.info("********** Set remote module be ready for call ************")
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())

        test.log.info("********** Detect if Module supports AT+CPAS command ************")
        test.dut.at1.send_and_verify("AT+CPAS", "OK|ERROR")
        if 'OK' in test.dut.at1.last_response:
            test.cpas_check = True
        else:
            test.cpas_check = False

    def run(test):
        loop_num = 20
        test.log.info(f"Loop for {loop_num} times")
        for loop in range(1, loop_num + 1):

            test.log.step(f"Loop {loop}/{loop_num} 1. Enable URC to report status of network registration")
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.dut.dstl_set_common_network_registration_urc())

            test.log.step(f"Loop {loop}/{loop_num} 2. Enables the presentation of following specific URC: \"signal\", \"message\", \"call\", \"rssi\", \"psinfo\".")
            sind_params = test.dut.dstl_get_all_indicators()
            urc_params = ["signal", "message", "call", "rssi", "psinfo"]
            for urc_param in urc_params:
                if urc_param in sind_params:
                    test.expect(test.dut.dstl_enable_one_indicator(urc_param))
                else:
                    test.log.warning(f"URC parameter {urc_param} is not supported by DUT's SIND command.")

            test.log.step(f"Loop {loop}/{loop_num}: 3. Make voice call from DUT to remote.")
            test.dut.at1.send_and_verify(f"ATD{test.r1.sim.int_voice_nr};")
            test.expect(test.r1.at1.wait_for("RING"))

            test.log.step(f"Loop {loop}/{loop_num}: 4. Answer call on remote.")
            test.expect(test.r1.at1.send_and_verify("ATA", "OK"))

            test.log.step(f"Loop {loop}/{loop_num}: 5. Disconnect DUT power supply or shut down DUT while voice call is active.")
            test.expect(test.dut.dstl_shutdown_smso())
            test.sleep(5)

            test.log.step(f"Loop {loop}/{loop_num}: 6. Connect power supply and turn on DUT.")
            test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
            test.expect(test.dut.dstl_check_urc("SYSSTART"))
            test.sleep(2)

        
    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CHUP"))

if "__main__" == __name__:
    unicorn.main()

