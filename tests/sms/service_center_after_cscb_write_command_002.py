#responsible: kamil.kedron@globallogic.com
#location: Wroclaw
#TC0095052.002

import unicorn

from core.basetest import BaseTest

from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.sms_center_address import dstl_set_sms_center_address


class Test(BaseTest):
    """
    INTENTION
    Intention of this TC is to check whether module is resilient to specific commands combination,
    which could lead to hang up of the DUT. TC has been created to cover:
    IPIS100108710 - CTest: module hangs up/AT-interface blocked by using the SMS AT commands AT+CSCB, AT+CSCA

    PRECONDITION
    One module, logged on to the network.
    """
    def setup(test):
        test.time_value = 10
        test.disable_operation = 0
        test.enable_operation = 1
        test.wrong_operation = 2
        test.message_id = "0-65535"
        test.service_center_address = "1234"

        test.log.step('PRECONDITION: Preparation module for test')
        test.set_precondition(test.dut)

    def run(test):
        for counter in range(1, 11):
            test.log.info(f"EXECUTION OF LOOP: {str(counter)}")
            test.execute_test_steps()

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=test.time_value))

    def set_precondition(test, interface):
        dstl_detect(interface)
        test.expect(dstl_get_imei(interface))
        test.expect(dstl_get_bootloader(interface))
        test.expect(dstl_lock_sim(interface))
        test.expect(dstl_register_to_network(interface))

    def set_operation(test, operation_value, message_id_value):
        return test.dut.at1.send_and_verify(f'AT+CSCB={operation_value},"{message_id_value}"', ".*OK.*", timeout=test.time_value)

    def execute_test_steps(test):
        test.log.step('1. Set at+cscb command with correct parameters (e.g. at+cscb=0,"0-65535")')
        test.expect(test.set_operation(test.disable_operation, test.message_id))

        test.log.step('2. Check at+csca? command')
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", ".*OK.*", timeout=test.time_value))

        test.log.step('3. Set at+cscb command with correct parameters (e.g. at+cscb=1,"0-65535")')
        test.expect(test.set_operation(test.enable_operation, test.message_id))

        test.log.step('4. Check at+csca=? command')
        test.expect(test.dut.at1.send_and_verify("AT+CSCA=?", ".*OK.*", timeout=test.time_value))

        test.log.step('5. Set at+cscb command with correct parameters (e.g. at+cscb= 0,"0-65535")')
        test.expect(test.set_operation(test.disable_operation, test.message_id))

        test.log.step('6. Set at+csca="1234"')
        test.expect(test.dut.at1.send_and_verify(f'AT+CSCA="{test.service_center_address}"',
                                                 ".*OK.*", timeout=test.time_value))

        test.log.step('7. Set at+cscb command with correct parameters (e.g. at+cscb=1,"0-65535")')
        test.expect(test.set_operation(test.enable_operation, test.message_id))

        test.log.step('8. Check at+csca? command')
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", ".*OK.*", timeout=test.time_value))

        test.log.step('9. Set at+cscb command with correct parameters (e.g. at+cscb=0,"0-65535")')
        test.expect(test.set_operation(test.disable_operation, test.message_id))

        test.log.step('10. Set valid Service Center Address number for used sim card')
        test.expect(dstl_set_sms_center_address(test.dut))

        test.log.step('11. Set at+cscb command with incorrect parameters (e.g. at+cscb=2)')
        test.expect(test.dut.at1.send_and_verify(f"AT+CSCB={test.wrong_operation}",
                                                 ".*ERROR.*", timeout=test.time_value))

        test.log.step('12. Check at+csca? command')
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", ".*OK.*", timeout=test.time_value))

        test.log.step('13. Set at+cscb command with correct parameters (e.g. at+cscb=1,"0-65535")')
        test.expect(test.set_operation(test.enable_operation, test.message_id))


if "__main__" == __name__:
    unicorn.main()