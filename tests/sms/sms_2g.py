#responsible: dariusz.drozdek@globallogic.com, renata.bryla@globallogic.com
#location: Wroclaw
#TC0104298.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_gsm, dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0104298.001    Sms2G

    The goal of this TC is to check if MO and MT SMS works correctly in 2G

    1. Attach DUT and REM to 2G
    2. Send SMS from DUT to REM
    3. Check SMS on REM
    4. Send SMS from REM to DUT
    5. Check SMS on DUT
    """

    def setup(test):
        test.prepare_module(test.dut)
        test.prepare_module(test.r1)

    def run(test):
        test.log.step("1. Attach DUT and REM to 2G")
        test.expect(dstl_register_to_gsm(test.dut))
        test.expect(dstl_register_to_gsm(test.r1))

        test.log.step("2. Send SMS from DUT to REM")
        test.send_sms(test.dut, test.r1, "SMS from DUT to REMOTE")

        test.log.step("3. Check SMS on REM")
        test.read_sms(test.r1, "SMS from DUT to REMOTE")

        test.log.step("4. Send SMS from REM to DUT")
        test.send_sms(test.r1, test.dut, "SMS from REM to DUT")

        test.log.step("5. Check SMS on DUT")
        test.read_sms(test.dut, "SMS from REM to DUT")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def prepare_module(test, module):
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_enter_pin(module))
        test.sleep(10)  # timeout for SIM
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))

    def send_sms(test, sender, receiver, text):
        test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, text))

    def read_sms(test, receiver, text):
        if test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=120)):
            sms_received_remote = re.search(r"CMTI:.*\",\s*(\d{1,3})", receiver.at1.last_response)
            if sms_received_remote is not None:
                test.expect(dstl_read_sms_message(receiver, sms_received_remote[1]))
                test.expect(re.search(".*{}.*".format(text), receiver.at1.last_response))
            else:
                test.expect(False, msg="Message index not found")
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()
