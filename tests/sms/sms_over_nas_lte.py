#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0104299.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_lte
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0104299.001    SmsOverNasLte
    The goal of this TC is to check if MO and MT SMS works correctly over NAS in LTE.

    Precondition:
    Equipment:
    a) DUT
    b) REM
    c) 2 Sim Cards supporting SMS over NAS in LTE
    Configuration:
    d) If supported set text mode on DUT and REM (at+cmgf=1)
    e) If supported Enable URC presentation on DUT and REM (at+cnmi=2,1)

    Description:
    1. Attach DUT and REM to LTE (not to IMS for SMS)
    2. Send SMS from DUT to REM
    3. Check SMS on REM
    4. Send SMS from REM to DUT
    5. Check SMS on DUT
    """

    def setup(test):
        test.get_information(test.dut, "===== Start preparation for DUT module =====")
        test.ims_support_dut = test.check_ims_support(test.dut,
                               "===== Check IMS for SMS settings and perform DUT restart if necessary =====")
        test.sms_domain_support_dut = test.check_sms_domain_support(test.dut)
        test.restart_after_changing_scfg_settings(test.dut, test.ims_support_dut, test.sms_domain_support_dut)
        test.prepare_module(test.dut, "===== Additional settings for DUT module =====")
        test.get_information(test.r1, "===== Start preparation for REMOTE module =====")
        test.ims_support_rmt = test.check_ims_support(test.r1,
                               "===== Check IMS for SMS settings and perform DUT restart if necessary =====")
        test.sms_domain_support_rmt = test.check_sms_domain_support(test.r1)
        test.restart_after_changing_scfg_settings(test.r1, test.ims_support_rmt, test.sms_domain_support_rmt)
        test.prepare_module(test.r1, "===== Additional settings for REMOTE module =====")

    def run(test):
        test.log.h2("Starting TC0104299.001 SmsOverNasLte")
        test.log.step("Step 1. Attach DUT and REM to LTE (not to IMS for SMS)")
        test.check_ims_for_sms_and_attach_to_lte(test.dut, test.ims_support_dut, test.sms_domain_support_dut)
        test.check_ims_for_sms_and_attach_to_lte(test.r1, test.ims_support_rmt, test.sms_domain_support_rmt)

        test.log.step("Step 2. Send SMS from DUT to REM")
        test.send_sms(test.dut, test.r1, "SMS step 2 from DUT to REM")

        test.log.step("Step 3. Check SMS on REM")
        test.read_sms(test.r1, "SMS step 2 from DUT to REM")

        test.log.step("Step 4. Send SMS from REM to DUT")
        test.send_sms(test.r1, test.dut, "SMS step 4 from REM to DUT")

        test.log.step("Step 5. Check SMS on DUT")
        test.read_sms(test.dut, "SMS step 4 from REM to DUT")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.restore_values(test.dut, test.ims_support_dut, test.sms_domain_support_dut)
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.restore_values(test.r1, test.ims_support_rmt, test.sms_domain_support_rmt)

    def get_information(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        dstl_set_scfg_urc_dst_ifc(module)

    def prepare_module(test, module, text):
        test.log.info(text)
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/AutoAck",0', ".*O.*"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))
        test.expect(dstl_select_sms_message_format(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", "OK"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))

    def restore_values(test, module, ims_support, sms_domain_support):
        test.log.info("===== Restore IMS for SMS settings and if necessary perform module restart =====")
        if ims_support:
            if test.ims_value == "1":
                test.log.info("*** Restore IMS settings ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS","{}"'.format(test.ims_value), ".*OK.*"))
            else:
                test.log.info("*** IMS settings were disabled at the start of the test - NO restore is needed ***")
        else:
            test.log.info("*** IMS setting NOT supported by module ***")
        if sms_domain_support:
            if test.sms_domain_value == "IMS":
                test.log.info("*** Restore SMS/4GPref settings ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref","{}"'.format(test.sms_domain_value),
                                                       ".*OK.*"))
            else:
                test.log.info("***  SMS/4GPref settings were disabled at the start of the test "
                              "- NO restore is needed ***")
        else:
            test.log.info("*** SMS/4GPref setting NOT supported by module ***")
        if (ims_support and test.ims_value == "1") or (sms_domain_support and test.sms_domain_value == "IMS"):
            test.expect(dstl_restart(module))
            test.sleep(15)  # waiting for module to get ready
            test.expect(dstl_register_to_network(module))
        else:
            test.log.info("*** Additional restart NOT needed ***")
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))

    def check_ims_support(test, module, text):
        test.log.info(text)
        test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', ".*O.*"))
        ims = re.search(r'.*"MEopMode/IMS","(\d)".*', module.at1.last_response)
        if ims and ims[1] == "1":
            test.log.info("*** IMS setting supported by module - IMS enabled - must be disabled ***")
            test.ims_value = ims[1]
            test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', ".*OK.*"))
            ims_support = True
        elif ims and ims[1] == "0":
            test.log.info("*** IMS setting supported by module - IMS disabled ***")
            test.ims_value = ims[1]
            ims_support = True
        else:
            test.log.info("*** IMS setting NOT supported by module ***")
            ims_support = False
        return ims_support

    def check_sms_domain_support(test, module):
        test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref"', ".*O.*"))
        sms_domain = re.search(r'.*"SMS/4GPref","(.*)".*', module.at1.last_response)
        if sms_domain and sms_domain[1] == "IMS":
            test.log.info("*** SMS/4GPref setting supported by module - IMS is set - CSPS must be set ***")
            test.sms_domain_value = sms_domain[1]
            test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref","CSPS"', ".*OK.*"))
            sms_domain_support = True
        elif sms_domain and sms_domain[1] == "CSPS":
            test.log.info("*** SMS/4GPref setting supported by module - IMS is NOT set ***")
            test.sms_domain_value = sms_domain[1]
            sms_domain_support = True
        else:
            test.log.info("*** SMS/4GPref setting NOT supported by module ***")
            sms_domain_support = False
        return sms_domain_support

    def restart_after_changing_scfg_settings(test, module, ims_support, sms_domain_support):
        if (ims_support and test.ims_value == "1") or (sms_domain_support and test.sms_domain_value == "IMS"):
            test.log.info("===== SCFG settings have been changed - module restart is needed =====")
            test.expect(dstl_restart(module))
            test.sleep(15)  # waiting for module to get ready
            test.expect(dstl_register_to_network(module))
        else:
            test.log.info("===== Restart NOT needed =====")

    def check_ims_for_sms_and_attach_to_lte(test, module, ims_support, sms_domain_support):
        test.log.info("===== Check SCFG settings - IMS for SMS =====")
        if ims_support:
            test.log.info("*** Check IMS settings ***")
            test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', '.*"MEopMode/IMS","0".*OK.*'))
        else:
            test.log.info("*** IMS setting NOT supported by module ***")
        if sms_domain_support:
            test.log.info("*** Check SMS/4GPref settings ***")
            test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref"', '.*"SMS/4GPref","CSPS".*OK.*'))
        else:
            test.log.info("*** SMS/4GPref setting NOT supported by module ***")
        test.log.info("===== Check if module is registered to LTE =====")
        test.expect(module.at1.send_and_verify("AT+COPS?", ".*OK.*"))
        if re.search(r".*COPS:.*,.*,.*,(7|9).*", module.at1.last_response):
            test.log.info("*** Module registered to LTE ***")
        else:
            test.log.info("*** Register module to LTE ***")
            test.expect(dstl_register_to_lte(module))

    def send_sms(test, sender, receiver, text):
        test.expect(dstl_send_sms_message(sender, receiver.sim.int_voice_nr, text))
        test.expect(re.search(".*CMGS.*", sender.at1.last_response))

    def read_sms(test, receiver, text):
        test.expect(dstl_check_urc(receiver, ".*CMTI.*", timeout=360))
        sms_received_remote = re.search(r"CMTI:\s*\"ME\",\s*(\d{1,3})", receiver.at1.last_response)
        if sms_received_remote:
            test.expect(dstl_read_sms_message(receiver, sms_received_remote[1]))
            test.log.info("Expected REGEX: .*[\n\r]{}.*".format(text))
            test.expect(re.search(r".*[\n\r]{}.*".format(text), receiver.at1.last_response))
        else:
            test.expect(False, msg="Message was not received")


if "__main__" == __name__:
    unicorn.main()