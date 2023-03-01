#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095028.001, TC0095028.002

import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_lte
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_functions import dstl_send_sms_message


class Test(BaseTest):
    """TC0095028.001 / TC0095028.002   TpSmsViaNasSignaling
    To check if it is possible to send/receive SMS via NAS Signaling (not via IMS)
    1.    Send SMS from DUT to 1st Remote not connected to IMS
    2.    Send SMS from 1st Remote not connected to IMS to DUT
    3.    Send SMS from DUT to 2nd Remote connected to IMS
    4.    Send SMS from 2nd Remote connected to IMS to DUT

    Precondition:
    3 Devices needed for test (DUT + 2xRemote):
    -    1 DUT connected to LTE network but not to IMS
    -    1st Remote connected to LTE network but not to IMS
    -    2nd Remote connected to LTE and to IMS
    SMS Service Centre address set on DUT and on 1st Remote
    Network supports SMS over NAS signaling

    Available test scenarios below:
    1. If Test Network supports LTE SMS over IMS and over NAS
    a) DUT can be connected to Test Network and use SMS over NAS
    b1) As remote one device connected to Test Network can be used which supports SMS over NAS and over IMS
    (eg. Miami Step 4 - there is a possibility to choose how SMS should be handle in LTE - at^scfg configuration)
    or
    b2) As remote 2 separate devices connected to Test Network can be used - one which supports SMS over NAS
    (eg another DUT) and one which supports SMS over IMS (Miami, Zurich)
    2. If Test Network supports LTE SMS only over NAS
    a) DUT can be connected to the network and use SMS over NAS
    b)  As remote 2 separate devices can be used
    ->  one in Test Network which supports SMS over NAS (eg another DUT)
    ->  one in another network which supports SMS over IMS (Miami, Zurich)

    Automated test scenarios below:
    Precondition:
    Remote MIAMI ALAS3_E or compatible with SMS via IMS and via CSPS (NAS)
    Remote SIM CARD with IMS capability and SMS vis IMS feature

    Description:
    1. Send 3x SMS from DUT to 1st Remote not connected to IMS
    2. Send 3x SMS from 1st Remote not connected to IMS to DUT
    3. Send 3x SMS from DUT to 2nd Remote connected to IMS
    4. Send 3x SMS from 2nd Remote connected to IMS to DUT
    """

    def setup(test):
        test.get_information(test.dut, "===== Start preparation for DUT module =====")
        test.ims_support_dut = test.check_ims_support(test.dut,
                               "===== Check IMS for SMS settings and perform DUT restart if necessary =====")
        test.sms_domain_support_dut = test.check_sms_domain_support(test.dut)
        test.restart_after_changing_scfg_settings(test.dut, test.ims_support_dut, test.sms_domain_support_dut)

        test.get_information(test.r1, "===== Start preparation for 1st REMOTE module =====")
        test.ims_support_rmt_1 = test.check_ims_support(test.r1,
                               "===== Check IMS for SMS settings and perform DUT restart if necessary =====")
        test.sms_domain_support_rmt_1 = test.check_sms_domain_support(test.r1)
        test.restart_after_changing_scfg_settings(test.r1, test.ims_support_rmt_1, test.sms_domain_support_rmt_1)

        test.get_information(test.r2, "===== Start preparation for 2nd REMOTE module =====")
        test.ims_support_rmt_2 = test.check_ims_support(test.r2,
                               "===== Check IMS for SMS settings and perform DUT restart if necessary =====")
        test.sms_domain_support_rmt_2 = test.check_sms_domain_support(test.r2)
        test.restart_after_changing_scfg_settings(test.r2, test.ims_support_rmt_2, test.sms_domain_support_rmt_2)

        test.log.info("===== Check IMS / NAS settings and attach DUT and 2 REMOTES to LTE =====")
        test.check_ims_for_sms_settings(test.dut, test.ims_support_dut, test.sms_domain_support_dut)
        test.check_attach_to_lte(test.dut)
        test.check_ims_for_sms_settings(test.r1, test.ims_support_rmt_1, test.sms_domain_support_rmt_1)
        test.check_attach_to_lte(test.r1)
        test.check_ims_for_sms_settings(test.r2, test.ims_support_rmt_2, test.sms_domain_support_rmt_2)
        test.check_attach_to_lte(test.r2)

        test.prepare_module(test.dut, "===== Additional settings for DUT module =====")
        test.prepare_module(test.r1, "===== Additional settings for 1st REMOTE module =====")
        test.prepare_module(test.r2, "===== Additional settings for 2nd REMOTE module =====")

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0095028.002 TpSmsViaNasSignaling")
        else:
            test.log.h2("Starting TP TC0095028.001 TpSmsViaNasSignaling")

        test.log.step("Step 1. Send 3x SMS from DUT to 1st Remote not connected to IMS")
        test.send_and_receive_sms(test.dut, test.r1, "SMS from DUT to 1st Remote - nr: ")

        test.log.step("Step 2. Send 3x SMS from 1st Remote not connected to IMS to DUT")
        test.send_and_receive_sms(test.r1, test.dut, "SMS from 1st Remote to DUT - nr: ")

        test.log.step("Step 3. Send 3x SMS from DUT to 2nd Remote connected to IMS")
        test.send_and_receive_sms(test.dut, test.r2, "SMS from DUT to 2nd Remote - nr: ")

        test.log.step("Step 4. Send 3x SMS from 2nd Remote connected to IMS to DUT")
        test.send_and_receive_sms(test.r2, test.dut, "SMS from 2nd Remote to DUT - nr: ")

    def cleanup(test):
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.restore_values(test.dut, test.ims_support_dut, test.sms_domain_support_dut)
        test.expect(dstl_delete_all_sms_messages(test.r1))
        test.restore_values(test.r1, test.ims_support_rmt_1, test.sms_domain_support_rmt_1)
        test.expect(dstl_delete_all_sms_messages(test.r2))
        test.restore_values(test.r2, test.ims_support_rmt_2, test.sms_domain_support_rmt_2)

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
            if module != test.r2:
                test.log.info("*** IMS setting supported by module - IMS enabled - must be disabled ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', ".*OK.*"))
            else:
                test.log.info("*** IMS setting supported by module - IMS enabled ***")
            test.ims_value = ims[1]
            ims_support = True
        elif ims and ims[1] == "0":
            if module != test.r2:
                test.log.info("*** IMS setting supported by module - IMS disabled ***")
            else:
                test.log.info("*** IMS setting supported by module - IMS disabled - must be enabled ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"', ".*OK.*"))
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
            if module != test.r2:
                test.log.info("*** SMS/4GPref setting supported by module - IMS is set - CSPS must be set ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref","CSPS"', ".*OK.*"))
            else:
                test.log.info("*** SMS/4GPref setting supported by module - IMS is set ***")
            test.sms_domain_value = sms_domain[1]
            sms_domain_support = True
        elif sms_domain and sms_domain[1] == "CSPS":
            if module != test.r2:
                test.log.info("*** SMS/4GPref setting supported by module - IMS is NOT set ***")
            else:
                test.log.info("*** SMS/4GPref setting supported by module - IMS is NOT set - IMS must be set ***")
                test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref","IMS"', ".*OK.*"))
            test.sms_domain_value = sms_domain[1]
            sms_domain_support = True
        else:
            test.log.info("*** SMS/4GPref setting NOT supported by module ***")
            sms_domain_support = False
        return sms_domain_support

    def restart_after_changing_scfg_settings(test, module, ims_support, sms_domain_support):
        if ((ims_support and test.ims_value == "1") or (sms_domain_support and test.sms_domain_value == "IMS"))\
                and module != test.r2:
            test.log.info("===== SCFG settings have been changed - module restart is needed =====")
            test.expect(dstl_restart(module))
            test.sleep(15)  # waiting for module to get ready
        elif ((ims_support and test.ims_value == "0") or (sms_domain_support and test.sms_domain_value == "CSPS")) \
                and module == test.r2:
            test.log.info("===== SCFG settings have been changed - module restart is needed =====")
            test.expect(dstl_restart(module))
            test.sleep(15)  # waiting for module to get ready
        else:
            test.log.info("===== Restart NOT needed - SCFG settings NOT changed =====")
        test.log.info("===== Register module to the network =====")
        test.expect(dstl_register_to_network(module))

    def check_ims_for_sms_settings(test, module, ims_support, sms_domain_support):
        test.log.info("===== Check SCFG settings - IMS for SMS =====")
        if ims_support:
            test.log.info("*** Check IMS settings ***")
            if module != test.r2:
                test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', '.*"MEopMode/IMS","0".*OK.*'))
            else:
                test.expect(module.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', '.*"MEopMode/IMS","1".*OK.*'))
        else:
            test.log.info("*** IMS setting NOT supported by module ***")
        if sms_domain_support:
            test.log.info("*** Check SMS/4GPref settings ***")
            if module != test.r2:
                test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref"', '.*"SMS/4GPref","CSPS".*OK.*'))
            else:
                test.expect(module.at1.send_and_verify('AT^SCFG="SMS/4GPref"', '.*"SMS/4GPref","IMS".*OK.*'))
        else:
            test.log.info("*** SMS/4GPref setting NOT supported by module ***")

    def check_attach_to_lte(test, module):
        test.log.info("===== Check if module is registered to LTE =====")
        if module == test.r2:
            test.connection = dstl_get_connection_setup_object(module, device_interface="at1")
            test.log.info("*** Additional check for 2nd Remote: USIM card, CGDCONT-CID for IMS and CAVIMS command ***")
            test.expect(module.at1.send_and_verify("ATI2", ".*UICC Application Identification 0x0[23].*OK.*"),
                        critical=True)
            test.expect(module.at1.send_and_verify("AT+CGDCONT?", ".*OK.*"))
            if re.search(".*,\".*\",\"ims\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\",0,0,0,0,1,0", module.at1.last_response):
                test.log.info("===== IMS APN set correctly ======")
                test.expect(True)
            else:
                test.log.info("===== IMS APN NOT set correctly - must be set =====")
                test.expect(test.connection.dstl_detach_from_packet_domain())
                test.expect(module.at1.send_and_verify(
                    "AT+CGDCONT=2,\"IPV4V6\",\"ims\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\",0,0,0,0,1,0", ".*OK.*"))
                test.expect(module.at1.send_and_verify("AT+CGDCONT?",
                            ".*,\".*\",\"ims\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\",0,0,0,0,1,0.*OK.*"), critical=True)
                test.log.info("===== CGDCONT CID settings have been changed - module restart is needed =====")
                test.expect(dstl_restart(module))
                test.sleep(15)  # waiting for module to get ready
                test.expect(dstl_register_to_lte(module))
                test.sleep(15)  # waiting for module to get ready
            test.expect(module.at1.send_and_verify("AT+CAVIMS?", ".*CAVIMS: 1.*OK.*"), critical=True)

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

    def send_and_receive_sms(test, sender, receiver, text):
        for i in range(1, 4):
            test.log.info("===== SMS nr: {} =====".format(i))
            test.send_sms(sender, receiver, "{}{}".format(text, i))
            test.read_sms(receiver, text)


if "__main__" == __name__:
    unicorn.main()