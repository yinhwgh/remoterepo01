#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0011200.001, TC0011200.002

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
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.auxiliary_sms_functions import _convert_number_to_pdu_number
from dstl.sms.auxiliary_sms_functions import _calculate_pdu_length


class Test(BaseTest):
    """
    TC0011200.001 / TC0011200.002    CscaPDU

    To test the set service centre address command (+CSCA) in various formats, then send SMS in PDU mode

    Set SCA in international format. Attempt to:
    1. set blank SCA values
    2. set SCA in national and international format without specifying <TOSCA> value
    3. set SCA as a too long number
    4a. set SCA in national format using AT+CSCA and send a PDU message without implemented SCA - SCA field is empty
        (only works on certain networks)
    4b. set SCA in national format using AT+CSCA and send a PDU message with implemented SCA in national format.
        Destination adress is in national format (only works on certain networks).
    4c. set SCA in national format using AT+CSCA and send a PDU message with implemented SCA in national format.
        Destination adress is in international format in PDU message (only works on certain networks).
    5a. set SCA in international format using AT+CSCA and send a PDU message without implemented SCA
        - SCA field is empty (only works on certain networks).
    5b. set SCA in international format using AT+CSCA and send a PDU message with implemented SCA
        in international format. Destination adress is in national format (only works on certain networks).
    5c. set SCA in international format using AT+CSCA and send a PDU message with implemented SCA
        in international format. Destination adress is in international format in PDU message
        (only works on certain networks).
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.delete_sms_from_memory()
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.sca_nat = test.dut.sim.sca
        test.sca_int = test.dut.sim.sca_int
        test.tosca_nat = 129
        test.tosca_int = 145
        test.sms_timeout = 360
        test.sca_nat_pdu = _convert_number_to_pdu_number(test.dut.sim.sca, "SCA")
        test.nat_number_pdu = _convert_number_to_pdu_number(test.dut.sim.nat_voice_nr)
        test.sca_int_pdu = test.dut.sim.sca_pdu
        test.int_number_pdu = test.dut.sim.pdu
        test.sca_empty = _convert_number_to_pdu_number("", "SCA")

    def run(test):
        if test.dut.project.upper() == "VIPER":
            test.log.h2("Starting TP TC0011200.002 CscaPDU")
        else:
            test.log.h2("Starting TP TC0011200.001 CscaPDU")
        test.log.step("Set SCA in international format. Attempt to:")
        test.log.info("Set PDU mode")
        test.expect(dstl_select_sms_message_format(test.dut, 'PDU'))
        test.log.step("Step 1. set blank SCA values")
        test.log.info("For QCT it returns ERROR")
        test.set_sca_incorrect_value("=")
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))
        test.set_sca_incorrect_value("=,")
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))
        test.set_sca_incorrect_value('=""')
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))
        test.set_sca_incorrect_value('="",')
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))

        test.log.step("Step 2. set SCA in national and international format without specifying <TOSCA> value")
        test.log.info("set SCA in national format without specifying <TOSCA> value")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat))
        test.check_sca_values('.*CSCA: "{}",{}.*OK.*'.format(test.sca_nat, test.tosca_nat))
        test.log.info("set SCA in international format without specifying <TOSCA> value")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))

        test.log.step("Step 3. set SCA as a too long number")
        test.set_sca_incorrect_value('="+1234567890123456789123456789"')
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))

        test.log.step("Step 4a. set SCA in national format using AT+CSCA and send a PDU message without "
                      "implemented SCA - SCA field is empty (only works on certain networks)")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat))
        test.send_sms_pdu_depending_on_network(test.sca_empty, test.nat_number_pdu,
                                               "19E3F9380C7206A9A0F9380C2A36A1D42C881C06398354")

        test.log.step("Step 4b. set SCA in national format using AT+CSCA and send a PDU message with "
                      "implemented SCA in national format. Destination adress is in national format "
                      "(only works on certain networks).")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat))
        test.send_sms_pdu_depending_on_network(test.sca_nat_pdu, test.nat_number_pdu,
                                               "17E3F9380C7206A9A0F9380C7206A9207218E40C5201")

        test.log.step("Step 4c. set SCA in national format using AT+CSCA and send a PDU message with "
                      "implemented SCA in national format. Destination adress is in international format "
                      "in PDU message (only works on certain networks).")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat))
        test.send_sms_pdu_depending_on_network(test.sca_nat_pdu, test.int_number_pdu,
                                               "17E3F9380C7206A9A0F9380C7206A920721894745201")

        test.log.step("Step 5a. set SCA in international format using AT+CSCA and send a PDU message without "
                      "implemented SCA - SCA field is empty (only works on certain networks).")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.send_sms_pdu_depending_on_network(test.sca_empty, test.int_number_pdu,
                                               "19E3F9380C4A3AA9A0F9380C2A36A1D42C881C06259D54")

        test.log.step("Step 5b. set SCA in international format using AT+CSCA and send a PDU message with "
                      "implemented SCA in international format. Destination adress is in national format "
                      "(only works on certain networks).")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.send_sms_pdu_depending_on_network(test.sca_int_pdu, test.nat_number_pdu,
                                               "17E3F9380C4A3AA9A0F9380C4A3AA9207218E40C5201")

        test.log.step("Step 5c. set SCA in international format using AT+CSCA and send a PDU message with "
                      "implemented SCA in international format. Destination adress is in international format "
                      "in PDU message (only works on certain networks).")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.send_sms_pdu_depending_on_network(test.sca_int_pdu, test.int_number_pdu,
                                               "17E3F9380C4A3AA9A0F9380C4A3AA920721894745201")

    def cleanup(test):
        test.delete_sms_from_memory()
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def delete_sms_from_memory(test):
        test.log.info("Delete SMS from memory")
        dstl_set_preferred_sms_memory(test.dut, "ME")
        dstl_delete_all_sms_messages(test.dut)

    def set_sca_incorrect_value(test, value):
        test.expect(test.dut.at1.send_and_verify("AT+CSCA{}".format(value), ".*ERROR.*"))

    def check_sca_values(test, cmd_response):
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", cmd_response))

    def send_sms_pdu_depending_on_network(test, sca_pdu, pdu_num, content):
        sms_pdu = "{}1100{}000001{}".format(sca_pdu, pdu_num, content)
        test.log.info("SMS PDU: {}".format(sms_pdu))
        test.dut.at1.send_and_verify("AT+CMGS={}".format(_calculate_pdu_length(sms_pdu)), expect=">")
        test.expect(test.dut.at1.send_and_verify(sms_pdu, end="\u001A", expect=".*OK.*|.*ERROR.*",
                                                 timeout=test.sms_timeout))
        msg_response = re.search(".*CMGS.*", test.dut.at1.last_response)
        if msg_response:
            test.log.info("CMGS command accepted - check if CMTI occurs (dependent on the network)")
            urc = dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout)
            if urc:
                test.read_incoming_sms(content)
            else:
                test.log.info("Message has NOT been received (dependent on the network)")
        else:
            test.log.info("Message has NOT been sent (dependent on the network)")

    def read_incoming_sms(test, content):
        test.log.info("if CMTI occurs - read received SMS")
        sms_index = re.search(r".*CMTI.*\",\s*(\d{1,3})", test.dut.at1.last_response)
        if sms_index:
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index.group(1)),
                        ".*CMGR: 0,,.*{}.*OK.*".format(content)))
        else:
            test.expect(False, msg="SMS content incorrect")


if "__main__" == __name__:
    unicorn.main()