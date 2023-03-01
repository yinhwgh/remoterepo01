#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0011213.001, TC0011213.002

import unicorn
import re
import time
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory

class Test(BaseTest):
    """
    TC0011213.001 / TC0011213.002 - SmsStatusReportPDU

    Different values of <ds>=0,1,2 are set with at+cnmi on first module, then from first module smses are sent
    in PDU mode, an appropriate return message should be returned by second module.

    <ds>=0: status report must be saved in memory without indication
    <ds>=1: status report should be send directly to TE with acknowledgement
    <ds>=2: status report should be saved on SIM card, indication shows index in the memory

    On Quinn only two first cases exists, but in case 0 no indication is shown, and no status report is saved.
    In 3GPP2 devices/networks some values may not be supported.
    In CDMA2k only Verizon network supports status reports!
    """

    SMS_TIMEOUT = 120
    MSG_MR = ""
    CDSI_INDEX = ""

    def setup(test):
        test.prepare_module(test.dut, "PREPARING DUT")
        test.prepare_module(test.r1, "PREPARING REMOTE")
        test.log.info("===== Check number of SMS in SR memory on DUT =====")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        test.sr_sms_number_start = int(test.expect(dstl_get_sms_count_from_memory(test.dut))[0])
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME"))

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0011213.002 - SmsStatusReportPDU")
        else:
            test.log.h2("Starting TP TC0011213.001 - SmsStatusReportPDU")
        test.log.info("TC Scenario will be realized for available <mode> with omitting the <mode>=0")
        test.log.info("===== Check available <mode> and <ds> value for at+cnmi: <mode>, <mt>, <bm>, <ds>, <bfr> =====")
        test.mode_list = test.check_available_cnmi_parameters("mode")
        test.ds_list = test.check_available_cnmi_parameters("ds")
        for mode in test.mode_list:
            for ds in test.ds_list:
                test.log.step("Step for <mode> {} and <ds> {}".format(mode, ds))
                test.set_and_check_cnmi_parameters(mode, ds)
                test.MSG_MR = test.send_sms_pdu()
                test.expect(dstl_check_urc(test.r1, ".*CMTI.*", timeout=test.SMS_TIMEOUT))
                test.expect(test.r1.at1.send_and_verify("AT+CPMS?", "OK"))
                if "2" in ds:
                    if test.dut.platform.upper() == "QCT":
                        test.log.info("===== <ds>=2 NOT supported =====")
                    else:
                        test.log.info("===== STATUS-REPORT should be saved in memory SR. Waiting for +CDSI =====")
                        test.expect(dstl_check_urc(test.dut, ".*CDSI.*", timeout=test.SMS_TIMEOUT))
                        test.check_sr_memory(ds)
                elif "1" in ds:
                    test.log.info("===== STATUS-REPORT must be showed immediately - waiting for +CDS =====")
                    test.check_cds_status_report()
                    test.check_sr_memory(ds)
                else:
                    test.log.info("===== No SMS-STATUS-REPORTs are routed to the TE - No +CDSI and +CDS =====")
                    test.expect(test.check_no_urc(".*CDS.*", test.SMS_TIMEOUT))
                    test.check_sr_memory(ds)

    def cleanup(test):
        test.delete_sms_from_memory(test.dut)
        test.restore_values(test.dut)
        test.delete_sms_from_memory(test.r1)
        test.restore_values(test.r1)

    def send_sms_pdu(test):
        sms_pdu = "{}3100{}000001{}".format(test.dut.sim.sca_pdu, test.r1.sim.pdu, "04F4F29C0E")
        test.log.info("SMS PDU: {}".format(sms_pdu))
        test.dut.at1.send_and_verify("AT+CMGS={}".format(_calculate_pdu_length(sms_pdu)), expect=">")
        test.expect(test.dut.at1.send_and_verify(sms_pdu, end="\u001A", expect=".*OK.*|.*ERROR.*",
                                                 timeout=test.SMS_TIMEOUT))
        response_content = test.expect(re.search(r".*CMGS:\s*(\d{1,3}).*", test.dut.at1.last_response))
        if response_content:
            msg_index = response_content.group(1)
            test.log.info("Index for the CMGS is: {}".format(msg_index))
            return int(msg_index)
        else:
            return test.log.error("Fail to get value of CMGS")

    def check_available_cnmi_parameters(test, parameter):
        test.log.info("===== Check available value of <{}> parameter".format(parameter))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=?", ".*OK.*"))
        if "mode" in parameter:
            response_content = test.expect(re.search(".*CNMI:\s*\(0,(.*)\),\(.*\),\(.*\),\(.*\),\(.*\).*".format(),
                                                     test.dut.at1.last_response))
        else:
            response_content = test.expect(re.search(".*CNMI:\s*\(.*\),\(.*\),\(.*\),\((.*)\),\(.*\).*".format(),
                                                     test.dut.at1.last_response))
        if response_content:
            parameter_value = response_content.group(1).replace(",", "")
            parameter_value_list = list(parameter_value)
            if "mode" in parameter:
                test.log.info("Available values of parameter <mode> with omitted the <mode>= 0: {}".format(
                    parameter_value_list))
            else:
                test.log.info("Available values of parameter <ds>: {}".format(parameter_value_list))
            return parameter_value_list
        else:
            return test.log.error("Fail to get values for parameter {}".format(parameter))

    def set_and_check_cnmi_parameters(test, mode, ds):
        test.log.info("===== Set CNMI=<mode>={},<mt>,<bm>,<ds>={}".format(mode, ds))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI={},1,0,{}".format(mode, ds), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI?", "CNMI:\s{},1,0,{},\d.*OK.*".format(mode, ds)))

    def check_no_urc(test, urc, timeout):
        elapsed_seconds = 0
        start_time = time.time()
        result = True
        while elapsed_seconds < timeout:
            if re.search(urc, test.dut.at1.last_response):
                result = False
                break
            elapsed_seconds = time.time() - start_time
        return result

    def check_cds_status_report(test):
        if test.MSG_MR:
            mr_hex = str(hex(test.MSG_MR))[2:].upper()
            if len(mr_hex) == 1:
                mr_hex = "0" + mr_hex
            cds = test.expect(dstl_check_urc(test.dut, ".*CDS:\s*\d{{1,3}}\s*[\n\r].*{}{}.*".
                                             format(mr_hex, test.r1.sim.pdu), timeout=test.SMS_TIMEOUT))
            if cds:
                test.log.info("===== CDS message should be confirm by CNMA =====")
                test.expect(test.dut.at1.send_and_verify("AT+CNMA", "OK"))
        else:
            test.log.error("Message was NOT sent")

    def check_sr_memory(test, ds):
        test.log.info("===== Check SR memory =====")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SR", 1))
        test.sr_sms_number = int(test.expect(dstl_get_sms_count_from_memory(test.dut))[0])
        if "2" in ds:
            test.log.info("===== STATUS-REPORT should be saved in memory SR =====")
            if test.expect(test.sr_sms_number is not None and test.sr_sms_number_start is not None and
                           test.sr_sms_number - 1 == test.sr_sms_number_start):
                test.log.info("STATUS-REPORT stored correctly in Memory")
            else:
                test.log.error("STATUS-REPORT not stored in Memory")
        elif "1" in ds:
            test.log.info("===== STATUS-REPORT will NOT be saved in memory =====")
            if test.expect(test.sr_sms_number is not None and test.sr_sms_number_start is not None and
                           test.sr_sms_number == test.sr_sms_number_start):
                test.log.info("STATUS-REPORT not stored in module memory as expected")
            else:
                test.log.error("STATUS-REPORT stored in memory")
        else:
            if test.dut.platform.upper() == "QCT":
                test.log.info("===== STATUS-REPORT should NOT be saved in memory SR =====")
                test.log.info("According to ATC: Received status reports are not stored by the module")
                if test.expect(test.sr_sms_number is not None and test.sr_sms_number_start is not None and
                               test.sr_sms_number == test.sr_sms_number_start):
                    test.log.info("No new STATUS-REPORT not stored in module memory")
                else:
                    test.log.error("STATUS-REPORT stored in memory")
            else:
                if test.expect(test.sr_sms_number is not None and test.sr_sms_number_start is not None and
                               test.sr_sms_number != test.sr_sms_number_start):
                    test.log.info("STATUS-REPORT stored correctly in Memory")
                else:
                    test.log.error("STATUS-REPORT not stored in Memory")
        test.expect(dstl_set_preferred_sms_memory(test.dut, "ME", 1))

    def prepare_module(test, module, text):
        test.log.info(text)
        dstl_detect(module)
        dstl_get_imei(module)
        dstl_get_bootloader(module)
        test.expect(dstl_register_to_network(module))
        test.expect(dstl_set_scfg_urc_dst_ifc(module))
        test.expect(dstl_set_sms_center_address(module, module.sim.sca_int))
        test.expect(dstl_select_sms_message_format(module, "PDU"))
        test.expect(module.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMS=1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSDH=1", ".*OK.*"))
        if module.project.upper() == "SERVAL":
            test.expect(module.at1.send_and_verify('AT^SCFG="Sms/AutoAck","0"', ".*OK.*"))
        test.delete_sms_from_memory(module)

    def delete_sms_from_memory(test, module):
        test.log.info("Delete SMS from memory")
        test.expect(dstl_set_preferred_sms_memory(module, "ME"))
        test.expect(dstl_delete_all_sms_messages(module))

    def restore_values(test, module):
        test.expect(module.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(module.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()