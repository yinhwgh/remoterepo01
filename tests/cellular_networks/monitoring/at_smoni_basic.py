# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0091865.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import customization_network_types
from dstl.network_service import network_monitor


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("1.1 test without pin.")
        test.dut.dstl_restart()
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=?", ".*SMONI=\\?\\s*OK\\s*"))
        test.sleep(15)
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*"))

        test.log.step("1.2. test invalid parameters without PIN.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONI?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=0", ".*OK.*|.*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=256", ".*OK.*|.*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=ABC", ".*ERROR.*"))

        test.log.step("2. Regsiter to network")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step("3. test with invalid parameters with PIN.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONI?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=0", ".*OK.*|.*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI254", ".*OK.*|.*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SMONI="hallo"', ".*ERROR.*"))

        test.log.step("4. Functionality test.")

        # if test.dut.GSM.lower() == "true" and ("serval" not in test.dut.project.lower()):
        #     The AT^SMONI command for EXS82-W 2G has seperate LM and separate test case

        # if test.dut.UMTS.lower() == "true":
        #     test.test_UMTS()

        test.log.info('****** Testing SMONI for each supported network.')
        supported_networks = test.dut.dstl_customized_network_types()
        for network, is_supported in supported_networks.items():
            test.log.info(f"{network}: {is_supported}")
        for network, is_supported in supported_networks.items():
            if is_supported:
                if hasattr(test, 'test_' + network):
                    test_act = eval('test.test_' + network)
                    test_act()
                else:
                    test.expect(False, msg=f'Function test_{network} may be not defined or in a different name.')

    def test_GSM(test):
        test.log.info("Test under GSM starts.")
        test.expect(test.dut.dstl_register_to_gsm())
        test.sleep(5)
        test.expect(test.dut.dstl_monitor_serving_cell('GSM', 'registered'))
        test.log.info("Test under GSM ends.")

    def test_UMTS(test):
        test.log.info("Test under UMTS starts.")
        test.expect(test.dut.dstl_register_to_umts())
        test.sleep(5)
        test.expect(test.dut.dstl_monitor_serving_cell('UMTS', 'registered'))
        test.log.info("Test under UMTS ends.")

    def test_LTE(test):
        test.log.info("Test under LTE starts.")
        test.expect(test.dut.dstl_register_to_lte())
        test.sleep(5)
        test.expect(test.dut.dstl_monitor_serving_cell('LTE', 'registered'))
        test.log.info("Test under LTE ends.")

    def test_NBIOT(test):
        test.log.info("Test under NB-IOT starts.")
        test.expect(test.dut.dstl_register_to_nbiot())
        test.expect(test.dut.dstl_monitor_serving_cell('NBIOT', 'registered'))
        test.log.info("Test under NB-IOT ends.")

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
