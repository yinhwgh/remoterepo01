#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0104357.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """TC0104357.001    PersistentContextsCgdcont

    Basic test for persistent contexts.

    1. Define parameters of +CGDCONT
    2. Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)
    2.1. Restart module and check values
    2.2. Set to factory default and check values
    2.3. Set new parameters and check new values
    2.4. Restart module and check values
    2.5. Store parameters to user profile and check values
    2.6. Restore parameters from profile and check values
    2.7. Set to factory default and check values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)

    def run(test):
        cgdcont_regex_1 = r".*\+CGDCONT: 3,\"IP\",\"Internet3\",\"0(.0){3}\",1,1.*OK.*"
        cgdcont_regex_2 = r".*\+CGDCONT: 3,\"IPV6\",\"Internet4\",\"0(.0){15}\",2,2.*OK.*"

        test.log.step("1. Define parameters of +CGDCONT")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=3,\"IP\",\"Internet3\",\"0.0.0.0\",1,1", ".*OK.*"))
        test.log.step("2. Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)")
        test.log.step("2.1. Restart module and check values")
        test.expect(dstl_restart(test.dut))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_1))
        test.log.step("2.2. Set to factory default and check values")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_1))
        test.log.step("2.3. Set new parameters and check new values")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=3,\"IPV6\",\"Internet4\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"
                                                 "\",2,2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_2))
        test.log.step("2.4. Restart module and check values")
        test.expect(dstl_restart(test.dut))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_2))
        test.log.step("2.5. Store parameters to user profile and check values")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_2))
        test.log.step("2.6. Restore parameters from profile and check values")
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("ATZ", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_2))
        test.log.step("2.7. Set to factory default and check values")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", cgdcont_regex_2))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=3", ".*OK.*"))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")


if "__main__" == __name__:
    unicorn.main()
