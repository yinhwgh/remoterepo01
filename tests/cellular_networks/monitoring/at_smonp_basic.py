# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0091866.001


import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.network_service import check_cell_monitor_parameters
from dstl.network_service import customization_network_types
from dstl.network_service import network_monitor


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1 test without pin.")
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP=?", ".*SMONP=\\?\\s*OK\\s*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*O.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", ".*OK.*"))

        test.log.step("2. test with pin")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT^SMONP=?", ".*SMONP=\\?\\s*OK\\s*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", ".*OK.*"))

        test.log.step("3. test with invalid parameters with PIN.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONP?", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP=0", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONP=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI=254", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SMONI="hallo"', ".*ERROR.*"))

        test.log.step("4. Functionality test.")
        test.log.info('****** Testing SMONP for each supported network.')
        supported_networks = test.dut.dstl_customized_network_types()
        for network, is_supported in supported_networks.items():
            test.log.info(f"{network}: {is_supported}")
        for network, is_supported in supported_networks.items():
            if is_supported:
                test.log.info(f"Test under {network} starts.")
                registered = test.register_to_network(network)
                if registered:
                    test.check_smonp_response()
                else:
                    test.expect(False, msg=f'Fail to register to {network}. '
                                           f'Please find network information below.')
                    test.dut.at1.send_and_verify("AT+COPS?")
                    test.dut.at1.send_and_verify("AT^SMONI")
                    test.dut.at1.send_and_verify("AT^SMONP")
        test.log.info(f"Test under {network} ends.")

    def register_to_network(test, network):
        if hasattr(test.dut, "dstl_register_to_" + network.lower()):
            register_to_act = eval("test.dut.dstl_register_to_" + network.lower())
            registered = register_to_act()
        else:
            test.log.error(f"No DSTL found to register to {network}.")
            registered = False
        return registered

    def check_smonp_response(test):
        act = test.dut.dstl_monitor_network_act()
        if act == "Cat.M":
            act = "4g"
        elif act == "Cat.NB":
            act = "nb"

        dstl_function = "dstl_expect_smonp_parameter_" + act.lower()
        if hasattr(test.dut, dstl_function):
            get_expect_smonp = eval("test.dut." + dstl_function)
            expect_smonp = get_expect_smonp()
            # perform more times, CatNB shows a few seconds '--' for SrxLev, but then valid values
            test.attempt(test.dut.at1.send_and_verify, "AT^SMONP", expect_smonp, retry=7, sleep=3)
        else:
            if act=='unknown':
                test.expect(False, msg=f"Network ACT is wrong,please check response of AT^SMONI.")
            else:
                test.expect(False, msg=f"No DSTL {dstl_function} found.")

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
