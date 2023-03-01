#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0010336.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0010336.002    TpSmsoFlash500

    Check if the command AT^SMSO is available and work properly.

    1. Set CNMI = 2,1 and save it to user profile
    2. Send test command AT^SMSO=?
    3. Switch off module via AT^SMSO
    4. Send test command AT^SMSO=? immediately after power off and see reaction
    5. Wait 10 seconds
    6. Switch on the device with MC:IGT=5000
    7. Send AT twice
    8. Connect module to the network
    9. Send SMS Class 0 to itself and wait for incoming SMS (+CMT URC)
    10. Repeat step 2 to 10, 500 times
    11. Reset AT Command Settings to Factory Default Values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_enter_pin(test.dut)
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', "OK")
        test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*")
        dstl_set_preferred_sms_memory(test.dut, "ME")

    def run(test):
        test.log.step("1. Set CNMI = 2,1 and save it to user profile")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

        test.log.step("2. Send test command AT^SMSO=?")
        test.expect(test.dut.at1.send_and_verify("AT^SMSO=?", ".*OK.*"))
        loop = 1
        while loop < 501:
            test.log.info('Loop: {}'.format(loop))
            test.log.step("3. Switch off module via AT^SMSO")
            test.dut.at1.send_and_verify("AT^SMSO", ".*OK.*")
            test.log.step("4. Send test command AT^SMSO=? immediately after power of and see reaction")
            test.dut.at1.send("AT^SMSO=?")
            test.log.step("5. Wait 10 seconds")
            test.sleep(10)
            test.log.step("6. Switch on the device with MC:IGT=5000")
            test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
            test.sleep(20)
            test.log.step("7. Send AT twice")
            test.dut.at1.send_and_verify("AT", "OK")
            test.dut.at1.send_and_verify("AT", "OK")
            test.log.step("8. Connect module to the network")
            test.expect(dstl_register_to_network(test.dut))
            test.sleep(2)
            test.log.step("9. Send SMS Class 0 to itself and wait for incoming SMS (+CMT URC)")
            dstl_delete_all_sms_messages(test.dut)
            test.expect(dstl_send_sms_message(test.dut, test.dut.sim.int_voice_nr))

            #test.expect(test.dut.at1.send_and_verify('AT+CMGS=19', '.*>.*', wait_for=".*>.*"))
            #test.expect(test.dut.at1.send_and_verify('{}1100{}0010FF05C8329BFD06'.
            #                                         format(test.dut.sim.sca_pdu, test.dut.sim.pdu), end="\u001A",
            #                                         expect=".*OK.*", wait_for=r".*CMT.*\n.*5C8329BFD06\n.*",
            #                                        timeout=120))
            test.sleep(2)

            test.log.step("10. Repeat step 2 to 11, 500 times")
            loop = loop + 1

        test.log.step("11. Reset AT Command Settings to Factory Default Values")
        dstl_delete_all_sms_messages(test.dut)
        test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"', "OK")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
