#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC 0102185.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.select_sms_format import dstl_select_sms_message_format


class Test(BaseTest):
    """responsible: Dariusz Drozdek, dariusz.drozdek@globallogic.com
    Wroclaw

    TC 0102185.001    SmsDcsAll

    Check if it is possible to set all dcs values in at+csmp

    1. Set at+cmgf=1
    2. Try to set dcs without other parameters (e.g. at+csmp=,,,4)
    3. Set dcs value in at+csmp to 0 (e.g. at+csmp=17,167,0,0)
    4. Check at+csmp value (at+csmp?)
    5. Repeat steps 3-4 with all possible dcs values
    6. Set dcs value in at+csmp to value above max supported value (e.g. at+csmp=17,167,0,248)
    7. Check at+csmp value (at+csmp?)
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        dstl_enter_pin(test.dut)
        test.sleep(5)

    def run(test):
        test.log.step("1. Set at+cmgf=1")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.log.step("2. Try to set dcs without other parameters (e.g. at+csmp=,,,4)")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=,,,4", ".*ERROR.*"))
        dcs = 0
        while dcs < 248:
            test.log.info("DCS value: " + str(dcs))
            test.log.step("3. Set dcs value in at+csmp to {} (e.g. at+csmp=17,167,0,{})".format(str(dcs), str(dcs)))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,{}".format(str(dcs)), ".*OK.*"))
            test.log.step(" 4. Check at+csmp value (at+csmp?)")
            test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*CSMP: 17,167,0,{}[\r\n].*OK".format(str(dcs))))
            if dcs < 247:
                test.log.step("5. Repeat steps 3-4 with all possible dcs values")
            dcs += 1
        test.log.step("6. Set dcs value in at+csmp to value above max supported value (e.g. at+csmp=17,167,0,248)")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,248", ".*ERROR.*"))
        test.log.step("7. Check at+csmp value (at+csmp?)")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*CSMP: 17,167,0,247[\r\n].*OK"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
