#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0103429.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """
    TC0103429.001    ModuleSmsBufferCnmi

    Check functionality of <bfr> parameter of AT+CNMI command.

    1. Register both modules to network and prepare them for test
    <bfr> parameter is set to clearing  buffer mode (named as <bfr_clear>):
    2. Set AT+CNMI=0,1,0,0,<bfr_clear> on DUT
    3. Send SMS Class 0 from RMT to DUT
    4. Wait ~1 minute - URC should NOT appear
    5. Set AT+CNMI=1,1,0,0,<bfr_clear>  on DUT
    6. Wait ~1 minute - URC should NOT appear
    7. Set AT+CNMI=0,1,0,0,<bfr_clear> on DUT
    8. Send SMS Class 0 from RMT to DUT
    9. Wait ~1 minute - URC should NOT appear
    10. Set AT+CNMI=2,1,0,0,<bfr_clear>  on DUT
    11. Wait ~1 minute - URC should NOT appear
    12. Set AT+CNMI=2,1,0,0,<bfr_clear>  on DUT
    13. Send SMS Class 0 from RMT to DUT
    14. Wait ~1 minute - URC should appear

    If supported: <bfr> parameter is set to flushing buffer to the TE mode (named as <bfr_flushed>):
    15. Set AT+CNMI=0,1,0,0,<bfr_flushed> on DUT
    16. Send SMS Class 0 from RMT to DUT
    17. Wait ~1 minute - URC should NOT appear
    18. Set AT+CNMI=1,1,0,0,<bfr_flushed> on DUT
    19. Wait ~1 minute - URC should appear
    20. Set AT+CNMI=0,1,0,0,<bfr_flushed> on DUT
    21. Send SMS Class 0 from RMT to DUT
    22. Wait ~1 minute - URC should NOT appear
    23. Set AT+CNMI=2,1,0,0,<bfr_flushed> on DUT
    24. Wait ~1 minute - URC should appear
    """

    def setup(test):
        test.prepare_module(test.dut, "PREPARING DUT")
        test.prepare_module(test.r1, "PREPARING REMOTE")
        test.sms_timeout = 120
        test.urc_timeout = 60
        test.mode_0 = 0
        test.mode_1 = 1
        test.mode_2 = 2


    def run(test):
        test.log.step("Step 1. Register both modules to network and prepare them for test"
                      "<bfr> parameter is set to clearing  buffer mode (named as <bfr_clear>):")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))
        project = test.dut.project.upper()
        if project == "VIPER" or project == "SERVAL":
            test.log.info("according to ATC <bfr> parameter is set to clearing buffer mode - CNMI - <bfr> = 1")
            test.bfr_clear = 1
        else:
            test.expect(False, critical=True, msg="Test procedure NOT implemented for product {}.".format(project))

        test.log.step("Step 2. Set AT+CNMI=0,1,0,0,<bfr_clear> on DUT")
        test.set_cnmi_parameters(test.mode_0, test.bfr_clear)

        test.log.step("Step 3. Send SMS Class 0 from RMT to DUT")
        test.send_sms("sms step 3")

        test.log.step("Step 4. Wait ~1 minute - URC should NOT appear")
        test.sleep(test.urc_timeout)
        test.expect(not re.search(".*CMT:.*", test.dut.at1.last_response))

        test.log.step("Step 5. Set AT+CNMI=1,1,0,0,<bfr_clear> on DUT")
        test.set_cnmi_parameters(test.mode_1, test.bfr_clear)

        test.log.step("Step 6. Wait ~1 minute - URC should NOT appear")
        test.sleep(test.urc_timeout)
        test.expect(not re.search(".*CMT:.*", test.dut.at1.last_response))

        test.log.step("Step 7. Set AT+CNMI=0,1,0,0,<bfr_clear> on DUT")
        test.set_cnmi_parameters(test.mode_0, test.bfr_clear)

        test.log.step("Step 8. Send SMS Class 0 from RMT to DUT")
        test.send_sms("sms step 8")

        test.log.step("Step 9. Wait ~1 minute - URC should NOT appear")
        test.sleep(test.urc_timeout)
        test.expect(not re.search(".*CMT:.*", test.dut.at1.last_response))

        test.log.step("Step 10. Set AT+CNMI=2,1,0,0,<bfr_clear> on DUT")
        test.set_cnmi_parameters(test.mode_2, test.bfr_clear)

        test.log.step("Step 11. Wait ~1 minute - URC should NOT appear")
        test.sleep(test.urc_timeout)
        test.expect(not re.search(".*CMT:.*", test.dut.at1.last_response))

        test.log.step("Step 12. Set AT+CNMI=2,1,0,0,<bfr_clear> on DUT")
        test.set_cnmi_parameters(test.mode_2, test.bfr_clear)

        test.log.step("Step 13. Send SMS Class 0 from RMT to DUT")
        test.send_sms("sms step 13")

        test.log.step("Step 14. Wait ~1 minute - URC should appear")
        test.expect(dstl_check_urc(test.dut, ".*CMT:.*sms step 13.*", timeout=test.sms_timeout))

        test.log.step("If supported: <bfr> parameter is set to flushing buffer to the TE mode (named as <bfr_flushed>)")
        if project == "VIPER" or project == "SERVAL":
            test.log.info("For project {}, according to ATC no exist possibility use <bfr> parameter "
                          "to flushing buffer to the TE mode."
                          "Steps 15-24 will be omitted.".format(project))

    def cleanup(test):
        test.delete_sms_from_memory(test.dut)
        test.restore_values(test.dut)
        test.restore_values(test.r1)

    def prepare_module(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        test.expect(dstl_get_imei(module))
        test.expect(dstl_get_bootloader(module))
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.delete_sms_from_memory(module)

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def set_cnmi_parameters(test, mode, bfr):
        test.expect(test.dut.at1.send_and_verify("AT+CNMI={},1,0,0,{}".format(mode, bfr), ".*OK.*"))

    def send_sms(test, text):
        test.expect(test.r1.at1.send_and_verify("AT+CSMP=17,167,0,240", ".*OK.*"))
        test.expect(dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr, text))

    def restore_values(test, module):
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()