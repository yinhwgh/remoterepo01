# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107958.001

import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
    Intention:
    To check if it is possible to set the "is_cert" parameter in SIND command

    Detailed description:
    1. Set "Error Message Format" to 2 with AT+CMEE=2 command.
    2. Enable URC presentation using AT^SIND="is_cert",1 command.
    3. Check URC status using AT^SIND="is_cert",2 command.
    4. Disable URC presentation using AT^SIND="is_cert",0 command.
    5. Check URC status using AT^SIND="is_cert",2 command.
    6. Try to set invalid value using AT^SIND="is_cert",3 command.
    7. Check URC status using AT^SIND="is_cert",2 command.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.sind_iscert = "AT^SIND=\"is_cert\",{}"
        test.error = "+CME ERROR:"
        test.value_enable = "^SIND: is_cert,1,0,"
        test.value_disable = "^SIND: is_cert,0,0,"


    def run(test):
        test.log.info("TC0107958.001 SindIsCert_BasicCheck")
        test.log.step("1. Set \"Error Message Format\" to 2 with AT+CMEE=2 command.")
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step("2. Enable URC presentation using AT^SIND=\"is_cert\",1 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(1), test.value_enable))

        test.log.step("3. Check URC status using AT^SIND=\"is_cert\",2 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(2), test.value_enable))

        test.log.step("4. Disable URC presentation using AT^SIND=\"is_cert\",0 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(0), test.value_disable))

        test.log.step("5. Check URC status using AT^SIND=\"is_cert\",2 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(2), test.value_disable))

        test.log.step("6. Try to set invalid value using AT^SIND=\"is_cert\",3 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(3), test.error))

        test.log.step("7. Check URC status using AT^SIND=\"is_cert\",2 command.")
        test.expect(test.dut.at1.send_and_verify(test.sind_iscert.format(2), test.value_disable))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
