# responsible: thomas.troeger@thalesgroup.com
# location: Berlin
# TC0093034.001
# feature: LM0003686.001 - LTE: CSFB vs. USSD
#
# this testcase is mostly hard coded. You can complain but: the answers from network are also hard coded and only
# available in our testnetwork, so this is all hard coded. so WHAT??

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.auxiliary.check_urc import dstl_check_urc


class Test(BaseTest):
    """
    Test the AT+CUSD command and the ATD*xxx#; command if the module was registered in LTE network.

    The goal is to perform a USSD action in LTE band.
    In LTE there is no USSD available, so the module has to be used the 2G fallback to perform the action,.

    """

    def __init__(self):
        super().__init__()
        self.dut = None

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        pass

    def run(test):

        # enable creg indication with at + creg=2
        test.dut.at1.send_and_verify("at+creg=2", "OK")

        # enable text error message format
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        # enter pin with at+cpin="PIN1" and wait for registration
        test.dut.dstl_enter_pin()
        test.sleep(15)

        # check network properties
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", '.*[+]COPS: 0,0,\"EDAV\",7.*'))

        # check first CUSD as try
        test.expect(test.dut.at1.send_and_verify('at+cusd=1,\"*100#\"', "OK"))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"TEST STRING EDAV\",15.*", 60))

        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        # check next CUSD number
        test.expect(test.dut.at1.send_and_verify('at+cusd=1,\"*110#\"', "OK"))
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"UNKNOWN APPLICATION\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        # check next CUSD number
        test.dut.at1.send_and_verify('at+cusd=1,\"*102#\"', "OK")
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"ACCOUNT INFORMATION INVALID, SMD\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)

        # check next CUSD number
        test.expect(test.dut.at1.send_and_verify('at+cusd=1,\"*101#\"', "OK"))
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"INCORRECT SYNTAX FOR TARIFF AREA INTERROGATION\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)

        # testcase am Ende
        # neu: Teste mit ATD
        test.dut.at1.send_and_verify('ATD*100#;', "OK")
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"TEST STRING EDAV\",15.*", 60))

        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        # check next CUSD number
        test.expect(test.dut.at1.send_and_verify('ATD*110#;', "OK"))
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"UNKNOWN APPLICATION\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)
        # check next CUSD number
        test.expect(test.dut.at1.send_and_verify('Atd*102#;', "OK"))
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"ACCOUNT INFORMATION INVALID, SMD\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)

        # check next CUSD number
        test.expect(test.dut.at1.send_and_verify('ATD*101#;', "OK"))
        test.expect(test.dut.dstl_check_urc(".*\+CUSD: 0,\"INCORRECT SYNTAX FOR TARIFF AREA INTERROGATION\",15.*", 60))
        test.dut.dstl_check_urc(".*CREG: 1.*", 60)

        test.sleep(5)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
