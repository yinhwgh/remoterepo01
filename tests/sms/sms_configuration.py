#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0010715.001, TC0010715.003

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory, dstl_get_current_sms_memory


class Test(BaseTest):
    """TC0010715.001    SmsConfiguration

    Change short message configuration which is stored non-volatile and check after power off that the settings
    have been preserved.

    1. Change all short message settings to the user profile as follows:
        at+cmgf=1; at+csdh=1; at+cnmi=2,1; at+csms=1
    2. Change the short message settings to the non-volatile memory as follows:
        at+csmp=17,15,0,8 (on qct modules only two last parameters  <dcs> and <pid> are stored to non-volatile memory)
        at+cpms=sm,sm,sm
        at+csca=12346
    3. Change the short message setting to the volatile memory as follows:
        at+cscs="ucs2"
        at+cgsms=2 (non-volatile parameter on qct modules)
        at^ssmss=1 (no command on qct modules)
        at^ssconf=1 (no command on qct modules)
    4. After restart check the configuration parameters.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*CMGF: 0.*CSDH: 0.*CNMI: 0,0,0,0,1.*CSMS: 0.*OK.*"))


    def run(test):
        test.log.step("Change short message configuration which is stored non-volatile and check after power off that "
                      "the settings have been preserved.")
        test.log.step("1. Change all short message settings to the user profile as follows:\n"
                      "at+cmgf=1; at+csdh=1; at+cnmi=2,1; at+csms=1")
        user_profile_dict = {"CMGF": "1", "CSDH": "1", "CNMI": "2,1", "CSMS": "1"}
        for command, value in user_profile_dict.items():
            test.expect(test.dut.at1.send_and_verify("AT+{}={}".format(command, value), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+{}?".format(command),
                                                     ".*[+]{}: {}.*OK.*".format(command, value)))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*CMGF: 1.*CSDH: 1.*CNMI: 2,1.*CSMS: 1.*OK.*"))

        test.log.step("2. Change the short message settings to the non-volatile memory as follows:\n"
                      "at+csmp=17,15,1,8 (on qct modules only two last parameters  <dcs> and <pid> are stored to "
                      "non-volatile memory)\n"
                      "at+cpms=sm,sm,sm\n"
                      "at+csca=12346")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,15,1,8", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*[+]CSMP: 17,15,1,8.*OK.*"))
        test.expect(dstl_set_preferred_sms_memory(test.dut, "SM"))
        test.expect(dstl_get_current_sms_memory(test.dut) == ('SM', 'SM', 'SM'))
        test.expect(dstl_set_sms_center_address(test.dut, "12346"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", "[+]CSCA: \"12346\".*OK.*"))

        test.log.step("3. Change the short message setting to the volatile memory as follows:\n"
                      "at+cscs=\"ucs2\"\n"
                      "at+cgsms=2 (non-volatile parameter on qct modules)\n"
                      "at^ssmss=1 (no command on qct modules)\n"
                      "at^ssconf=1 (no command on qct modules)")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", ".*[+]CSCS: \"UCS2\".*OK.*"))
        if test.dut.project.upper() == "SERVAL":
            test.log.info("Serval does not support value 2, instead value 3 will be set")
            test.expect(test.dut.at1.send_and_verify("AT+CGSMS=3", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*[+]CGSMS: 3.*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGSMS=2", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*[+]CGSMS: 2.*OK.*"))
        if test.dut.platform.upper() == "QCT":
            test.log.info("{} does not support at^ssmss and at^ssconf commands.".format(test.dut.project.capitalize()))

        test.log.step("4. After restart check the configuration parameters.")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT&V", ".*CMGF: 1.*CSDH: 1.*CNMI: 2,1.*CSMS: 1.*OK.*"))

        test.log.info("4a. Checking settings from the user profile.")
        for command, value in user_profile_dict.items():
            test.expect(test.dut.at1.send_and_verify("AT+{}?".format(command),
                                                     ".*[+]{}: {}.*OK.*".format(command, value)))

        test.log.info("4b. Checking settings from the non-volatile memory.")
        test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*[+]CSMP: 17,167,1,8.*OK.*"))
        test.expect(dstl_get_current_sms_memory(test.dut) == ('SM', 'SM', 'SM'))
        test.expect(test.dut.at1.send_and_verify("AT+CSCA?", "[+]CSCA: \"12346\".*OK.*"))

        test.log.info("4c. Settings from the volatile memory should be back to default values.")
        test.expect(test.dut.at1.send_and_verify("AT+CSCS?", ".*[+]CSCS: \"GSM\".*OK.*"))
        test.log.info("CGSMS is non-volatile parameter on qct modules")

        if test.dut.platform.upper() == "QCT":
            if test.dut.project.upper() == "SERVAL":
                test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*[+]CGSMS: 3.*OK.*"))
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*[+]CGSMS: 2.*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGSMS?", ".*[+]CGSMS: 0.*OK.*"))


    def cleanup(test):
        test.expect(dstl_set_sms_center_address(test.dut, test.dut.sim.sca_int))
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGSMS=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
