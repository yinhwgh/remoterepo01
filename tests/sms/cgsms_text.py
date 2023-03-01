#responsible: grzegorz.brzyk@globallogic.com
#location: Wroclaw
#TC0011194.001, TC0011194.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_umts, dstl_register_to_gsm
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.sms.sms_functions import *
from dstl.sms.delete_sms import dstl_delete_sms_message_from_index
from dstl.sms.read_sms_message import dstl_read_sms_message
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.configuration.network_registration_status import dstl_set_common_network_registration_urc
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    """
    TC0011194.001 / TC0011194.002 - CgsmsText

    INTENTION
    To test sending an SMS over GRPS rather than GSM in network which doesn't support that feature.

    PRECONDITION
    Two modules, logged on to network. Both modules are attached to GPRS.
    Provider shouldn't support smses over GPRS.
    """

    def setup(test):
        test.time_value = 10
        test.timeout_long = 60
        test.log.step("Prepare DUT")
        prepare_subscribers(test, test.dut)

        test.log.step("Prepare REM")
        prepare_subscribers(test, test.r1)

    def run(test):
        if test.dut.project.upper() == "SERVAL":
            supported_services = "1,3"
            tc_steps(test, supported_services, cid='1', pdp_type="IP")
        else:
            supported_services = "0,1,2,3"
            tc_steps(test, supported_services, cid='1', pdp_type="IP")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS={}".format(1), ".*OK.*", wait_for=".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", r".*\+CGSMS: {}.*".format(1), wait_for=".*OK.*"))
        dstl_delete_all_sms_messages(test.r1)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))
        test.expect(test.r1.at1.send_and_verify("AT&F", ".*OK.*", timeout=test.time_value))


def tc_steps(test, supported_services, cid, pdp_type):
    test.log.step("Step 1. Attach dut and remote to gprs.")
    test.log.info("Attach dut to gprs.")
    define_pdp_context_and_attach(test, test.dut, cid, pdp_type, pdp_apn=test.dut.sim.apn_v4)
    test.log.info("Attach remote to gprs.")
    define_pdp_context_and_attach(test, test.r1, cid, pdp_type, pdp_apn=test.r1.sim.apn_v4)

    test.log.step("Step 2. send sms using at+cgsms = 0 (sms over gprs).")
    if supported_services == "1,3":
        test.log.info("<service> = 0 check omitted, <service> = 0 not supported on module.")
    else:
        send_sms(test, test.dut, test.r1, 0, "sms over GPRS")

    test.log.step("Step 3. send sms using at+cgsms = 1 (sms over cs).")
    send_sms(test, test.dut, test.r1, 1, "sms over CS")

    test.log.step("Step 4. send sms using at+cgsms = 2 (sms over GPRS (preferred)).")
    if supported_services == "1,3":
        test.log.info("<service> = 2 check omitted, <service> = 2 not supported on module.")
    else:
        send_sms(test, test.dut, test.r1, 2, "sms over GPRS (preferred)")

    test.log.step("Step 5. send sms using at+cgsms = 3 (sms over CS (preferred)).")
    send_sms(test, test.dut, test.r1, 3, "sms over CS (preferred)")


def prepare_subscribers(test, device):
    dstl_detect(device)
    dstl_enter_pin(device)
    dstl_delete_all_sms_messages(device)
    dstl_get_imei(device)
    test.expect(device.at1.send_and_verify("AT+CIMI", ".*OK.*", timeout=test.time_value))
    test.expect(device.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=test.time_value))
    test.expect(dstl_set_scfg_urc_dst_ifc(device, device_interface="at1"))
    test.expect(dstl_set_common_network_registration_urc(device))
    test.expect(dstl_select_sms_message_format(device, "Text"))
    test.expect(device.at1.send_and_verify("AT+CSMP={}".format("17,167,0,0"), ".*OK.*", wait_for=".*OK.*"))
    test.expect(device.at1.send_and_verify("AT+CNMI={}".format("2,1"), ".*OK.*", wait_for=".*OK.*"))
    test.expect(device.at1.send_and_verify("AT+CNMI?", r".*\+CNMI: {}.*".format("2,1"), wait_for=".*OK.*"))

def define_pdp_context_and_attach(test, device, cid, pdp_type, pdp_apn):
    test.connection = dstl_get_connection_setup_object(device, device_interface="at1")
    test.expect(test.connection.dstl_detach_from_packet_domain())
    test.connection.cgdcont_parameters['cid'] = cid
    test.connection.cgdcont_parameters['pdp_type'] = pdp_type
    test.connection.cgdcont_parameters['apn'] = pdp_apn
    test.expect(test.connection.dstl_define_pdp_context())
    if device.project.upper() == "SERVAL":
        test.expect(dstl_register_to_gsm(device))
    else:
        test.expect(dstl_register_to_umts(device))
    test.expect(test.connection.dstl_attach_to_packet_domain())

def send_sms(test, device, device_2, service, message):
    test.expect(device.at1.send_and_verify("AT+CGSMS={}".format(service), ".*OK.*", wait_for=".*OK.*"))
    test.expect(device.at1.send_and_verify("AT+CGSMS?", r".*\+CGSMS: {}.*".format(service), wait_for=".*OK.*"))
    test.expect(dstl_send_sms_message(device, device_2.sim.int_voice_nr, message))
    test.expect(device_2.at1.wait_for("\+CMTI:", timeout=test.timeout_long))
    test.expect(device.at1.send_and_verify("AT+CGSMS?", r".*\+CGSMS: {}.*".format(service), wait_for=".*OK.*"))
    read_and_clean_sms(test, test.r1, message)

def read_and_clean_sms(test, device, message):
    if test.expect(dstl_list_occupied_sms_indexes(device) is not None):
        sms_index = max(dstl_list_occupied_sms_indexes(device))
        test.expect(r"{}".format(message) in dstl_read_sms_message(device, sms_index))
        test.expect(dstl_delete_sms_message_from_index(device, message_index=sms_index))
    else:
        test.log.error("No SMS found in memory")


if  "__main__" == __name__:
    unicorn.main()