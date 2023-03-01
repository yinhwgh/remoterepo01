# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0088311.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import unlock_sim_pin2
from dstl.security import get_spic_facility


class Test(BaseTest):
    """
    TC0088311.001 - TpAtSpicFunc
    Intention:
    Check all states of valid and invalid PIN/PUK-entering.
    Check status for all states and for correct responses of the module
    Subscriber: 1
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.simpin1 = test.dut.sim.pin1
        test.simpin2 = test.dut.sim.pin2
        test.simpuk1 = test.dut.sim.puk1
        test.simpuk2 = test.dut.sim.puk2

    def run(test):

        test.log.info("1. Check all responses of AT^SPIC")
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", ".*\^SPIC:.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", ".*\^SPIC: \d+.*OK.*"))

        f_list = test.dut.dstl_supported_spic_facility()
        for facility_value in f_list:
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\"".format(facility_value), ".*\^SPIC:.*OK.*"))
            if facility_value == 'SC' or facility_value == 'P2':
                test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\",0".format(facility_value), ".*\^SPIC:.*OK.*"))
                test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"{}\",1".format(facility_value), ".*\^SPIC:.*OK.*"))

        test.log.info("2. Check invalid parameters")
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",2", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"PS\",0,0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",0,\"1234\"", ".*ERROR.*"))

        test.log.info("3. Check SC facility function")
        if test.simpuk1 and test.simpin1:
            test.check_p1()
        else:
            test.log.info('Please check SIM properties in database')

        test.log.info("4. Check P2 facility function")
        if 'P2' in f_list:
            if test.simpuk2 and test.simpin2:
                test.check_p2()
            else:
                test.log.info('Please check SIM properties in database')
        else:
            test.log.info('Not support P2 facility, skip')

    def cleanup(test):
        test.log.info('***Test End, clean up***')

    def check_p1(test):
        test.log.info('3.1 Enter wrong pin1 code 1 time, and check spic')
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", "SPIC: 3"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",0", "SPIC: 2"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",1", "SPIC: 10"))

        test.log.info('3.2 Enter wrong pin1 code 3 times, and check spic')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "SIM PUK"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",0", "SPIC: 0"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",1", "SPIC: 10"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"67896789\",\"1234\"", "ERROR"))
        test.expect(test.dut.at1.send_and_verify("AT^SPIC", "SPIC: 9"))

        test.log.info('3.3 Restore pin1, check SPIC and CPIN status')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\",\"{}\"".format(test.simpuk1, test.simpin1), "OK"))

        # IPIS100357682 - SPIC? shows CME: unknown or only OK: NOT TO FIX in Viper01
        if str(test.dut.step) == '1' and test.dut.project == 'VIPER':
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "(CME ERROR: unknwon|OK)"))
            test.log.warning("IPIS100357682 - SPIC? shows CME: unknown or only OK: NOT TO FIX in Viper01")
        else:
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "SPIC: SIM PIN2"))

        test.expect(test.dut.at1.send_and_verify("AT^SPIC", "SPIC: 3"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))

    def check_p2(test):
        if test.dut.dstl_support_at_cpin2():
            test.log.info('4.1 Enter wrong pin2 code 1 time, and check spic')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 2"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 10"))

            test.log.info('4.2 Enter wrong pin2 code 3 times, and check spic')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "SIM PUK2"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 10"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 9"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 8"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 7"))

            test.log.info('4.3 Restore pin2, check SPIC and CPIN status')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2=\"{}\",\"{}\"".format(test.simpuk2, test.simpin2), "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\"", "SPIC: 3"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN2?", "READY"))

        else:
            test.log.info('4.1 Enter wrong pin2 code 1 time, and check spic')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 2"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 10"))

            test.log.info('4.2 Enter wrong pin2 code 3 times, and check spic')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"5678\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PUK2"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "SIM PUK2"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"SC\",0", "SPIC: 3"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 10"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 9"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 8"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"56785678\",\"2345\"", "ERROR"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",0", "SPIC: 0"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 7"))

            test.log.info('4.3 Restore pin2, check SPIC and CPIN status')
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\",\"{}\"".format(test.simpuk2, test.simpin2), "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC?", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\"", "SPIC: 3"))
            test.expect(test.dut.at1.send_and_verify("AT^SPIC=\"P2\",1", "SPIC: 10"))


if "__main__" == __name__:
    unicorn.main()
