#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0011136.001

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


class Test(BaseTest):
    """
    TC0011136.001    CscaText

    To test the set service centre address command (+CSCA) in various formats, then send SMS in text mode.

    Set SCA in international format. Attempt to:
    1. set blank SCA values
    2. set SCA in national and international format without specifying <TOSCA> value
    3. set SCA as a too long number
    4. set the SCA value with incorrect format identifier, i.e. <TOSCA> and send a message
    (only works on certain networks)
    5. set SCA with correct national format and send a message (only works on certain networks)
    6. set SCA with correct international format and send a message

    SCA number and <TOSCA> parameter are only used in 3GPP networks

    For 3GPP2 network SCA number and <TOSCA> parameter are not used
    so only checks if no ERRORs appears while setting different SCA and <TOSCA> values should be checked
    """

    def setup(test):
        test.log.info('According to additional info in TC Precondition section test will be executed on 1 module:'
                      '"For platforms: QCT, INTEL, SQN one module logged to the network is needed."')
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_register_to_network(test.dut)
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1", ".*OK.*"))
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.delete_sms_from_memory()
        test.sms_timeout = 120
        test.sca_nat = test.dut.sim.sca
        test.sca_int = test.dut.sim.sca_int
        test.tosca_nat = 129
        test.tosca_int = 145

    def run(test):
        test.log.step("Set SCA in international format. Attempt to:")
        test.log.step("1. set blank SCA values")
        test.log.info("For QCT it returns ERROR")
        test.set_sca_incorrect_value("=")
        test.set_sca_incorrect_value("=,")
        test.set_sca_incorrect_value('=""')
        test.set_sca_incorrect_value('="",')

        test.log.step("2. set SCA in national and international format without specifying <TOSCA> value")
        test.log.info("set SCA in national format without specifying <TOSCA> value")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat))
        test.check_sca_values('.*CSCA: "{}",{}.*OK.*'.format(test.sca_nat, test.tosca_nat))
        test.log.info("set SCA in international format without specifying <TOSCA> value")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int))
        test.check_sca_values('.*CSCA: "\{}",{}.*OK.*'.format(test.sca_int, test.tosca_int))

        test.log.step("3. set SCA as a too long number")
        test.set_sca_incorrect_value('="+1234567890123456789123456789"')

        test.log.step("4. set the SCA value with incorrect format identifier, i.e. <TOSCA> and send a message "
                      "(only works on certain networks)")
        test.log.info("Depending on module and network used message may or may not be sent. Crash must not occur")
        test.log.info("sending SMS: SCA international format and <TOSCA> national format")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int, test.tosca_nat))
        test.send_sms_depending_on_network("SMS SCA int format and TOSCA nat format", ".*OK.*|.*ERROR.*")
        test.log.info("sending SMS: SCA national format and <TOSCA> international format")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat, test.tosca_int))
        test.send_sms_depending_on_network("SMS SCA nat format and TOSCA int format", ".*OK.*|.*ERROR.*")

        test.log.step("5. set SCA with correct national format and send a message (only works on certain networks)")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_nat, test.tosca_nat))
        test.send_sms_depending_on_network("SMS SCA nat format and TOSCA nat format", ".*OK.*|.*ERROR.*")

        test.log.step("6. set SCA with correct international format and send a message")
        test.expect(dstl_set_sms_center_address(test.dut, test.sca_int, test.tosca_int))
        test.send_sms_directly("SMS SCA int format and TOSCA int format", ".*OK.*")

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

    def send_sms_directly(test, msg_text, msg_response):
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.int_voice_nr), expect=">"))
        test.expect(test.dut.at1.send_and_verify(msg_text, end="\u001A", expect=msg_response, timeout=test.sms_timeout))
        msg_response_content = re.search(".*CMGS.*", test.dut.at1.last_response)
        if msg_response_content:
            test.log.info("CMGS command accepted - wait for CMTI")
            urc = dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout)
            if urc:
                test.read_incoming_sms(msg_text)
            else:
                test.expect(False, "Module does not received SMS in required timeout")
        else:
            test.expect(False, "Message has NOT been sent")

    def send_sms_depending_on_network(test, msg_text, msg_response):
        test.expect(test.dut.at1.send_and_verify('AT+CMGS="{}"'.format(test.dut.sim.int_voice_nr), expect=">"))
        test.expect(test.dut.at1.send_and_verify(msg_text, end="\u001A", expect=msg_response,
                                                 timeout=test.sms_timeout), critical=True)
        msg_response_content = re.search(".*CMGS.*", test.dut.at1.last_response)
        if msg_response_content:
            test.log.info("CMGS command accepted - check if CMTI occurs (dependent on the network)")
            urc = dstl_check_urc(test.dut, ".*CMTI.*", timeout=test.sms_timeout)
            if urc:
                test.read_incoming_sms(msg_text)
            else:
                test.log.info("Message has NOT been received (dependent on the network)")
        else:
            test.log.info("Message has NOT been sent (dependent on the network)")

    def read_incoming_sms(test, msg_text):
        test.log.info("if CMTI occurs - read received SMS")
        sms_index = re.search(r".*CMTI.*\",\s*(\d{1,3})", test.dut.at1.last_response)
        if sms_index:
            test.expect(test.dut.at1.send_and_verify("AT+CMGR={}".format(sms_index.group(1)),
                        '.*CMGR:.*"\{}".*{}.*OK.*'.format(test.dut.sim.int_voice_nr, msg_text)))
        else:
            test.expect(False, "SMS content incorrect")


if "__main__" == __name__:
    unicorn.main()