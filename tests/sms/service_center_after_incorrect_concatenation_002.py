# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0093784.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory


class Test(BaseTest):
    """
    TC0093784.002   ServiceCenterAfterIncorrectConcatenation

    Intention of this TC is to check whether module is robust against specific commands combination,
    which could lead to hang up of the DUT.
    TC has been created to cover: IPIS100130372 - [AHS3-W]
    module hangs up/AT-interface blocked by using the SMS AT commands AT^SCMW, AT+CSCA

    1. Provide PIN
    2. After logging to the network set: at+cmgf=1 and at+cmee=2
    3. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")
    4. Check 'at+csca?' command
    5. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")
    6. Set 'at+csca="1234567"
    7. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")
    8. Check 'at+csca=?'
    9. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")
    10. Perform 'at+csca="1234"' command
    11. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")
    12. Perform "at+csca=_vailid_sca_number_for_used_sim_card _" command
    13. Set at^scmw command with correct parameter : (e.g. AT^SCMW="123456789",,,0,0,8,0)
    14. After promt > send some characters to the module and issue ctrl+z
    15. Check 'at+csca?' command
    Repeat 10 times steps from 3 to 15.
    """

    response_cms_error_invalid = ".*CMS ERROR: invalid parameter.*"
    response_ok = ".*OK.*"

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.dut))
        test.delete_sms_from_memory()

    def run(test):
        test.log.step("Step 1. Provide PIN")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("Step 2. After logging to the network set: at+cmgf=1 and at+cmee=2")
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

        for i in range(1, 11):
            test.log.info("===== START of ITERATION: {} =====".format(i))
            test.log.step('Step 3. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")')
            test.set_scmw('"0123456789"', test.response_cms_error_invalid)

            test.log.step("Step 4. Check 'at+csca?' command")
            test.check_csca_command("AT+CSCA?", '.*CSCA: "\{}",145.*OK.*'.format(test.dut.sim.sca_int))

            test.log.step('Step 5. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")')
            test.set_scmw('"0123456789"', test.response_cms_error_invalid)

            test.log.step("Step 6. Set 'at+csca=\"1234567\"'")
            test.set_sca_value('"1234567"', test.response_ok)

            test.log.step('Step 7. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")')
            test.set_scmw('"0123456789"', test.response_cms_error_invalid)

            test.log.step("Step 8. Check 'at+csca=?' command")
            test.check_csca_command("AT+CSCA=?", test.response_ok)

            test.log.step('Step 9. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")')
            test.set_scmw('"0123456789"', test.response_cms_error_invalid)

            test.log.step("Step 10. Perform 'at+csca=\"1234\"' command")
            test.set_sca_value('"1234"', test.response_ok)

            test.log.step('Step 11. Set at^scmw command with incorrect parameter : (e.g. at^scmw="0123456789")')
            test.set_scmw('"0123456789"', test.response_cms_error_invalid)

            test.log.step('Step 12. Perform "at+csca=_vailid_sca_number_for_used_sim_card _" command')
            test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))

            test.log.step('Step 13. Set at^scmw command with correct parameter : (e.g. AT^SCMW="123456789",,,0,0,8,0)')
            test.log.step("Step 14. After promt > send some characters to the module and issue ctrl+z")
            test.set_scmw('"123456789",,,0,0,8,0', test.response_ok)

            test.log.step("Step 15. Check 'at+csca?' command")
            test.check_csca_command("AT+CSCA?", '.*CSCA: "\{}",145.*OK.*'.format(test.dut.sim.sca_int))

            test.log.info("===== END of ITERATION: {} =====".format(i))
            if i < 10:
                test.log.step("Repeat 10 times steps from 3 to 15.")

    def cleanup(test):
        test.delete_sms_from_memory()
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")

    def delete_sms_from_memory(test):
        test.log.info("Delete SMS from memory")
        dstl_set_preferred_sms_memory(test.dut, "ME")
        dstl_delete_all_sms_messages(test.dut)

    def set_scmw(test, parameters, cmd_response):
        if "ERROR" in cmd_response:
            test.expect(test.dut.at1.send_and_verify("AT^SCMW={}".format(parameters), cmd_response))
        else:
            test.expect(test.dut.at1.send_and_verify("AT^SCMW={}".format(parameters), expect=">"))
            test.expect(test.dut.at1.send_and_verify("test scmw step 13", end="\u001A", expect=cmd_response))

    def set_sca_value(test, value, cmd_response):
        test.expect(test.dut.at1.send_and_verify("AT+CSCA={}".format(value), cmd_response))

    def check_csca_command(test, command, cmd_response):
        test.expect(test.dut.at1.send_and_verify(command, cmd_response))


if "__main__" == __name__:
    unicorn.main()