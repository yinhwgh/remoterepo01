#responsible: mateusz.wasielewski@globallogic.com
#location: Wroclaw
#TC

import unicorn
from core.basetest import BaseTest
# from dstl.devboard.ignite_module import dstl_ignite_module
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.configuration.scfg_radio_band import dstl_set_all_radio_bands
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.operator_selector import dstl_get_available_operator_rats

class Test(BaseTest):

    """
        This procedure verifies if UE can present the available PLMNs.
    """

    def setup(test):
        # test.dut.dstl_ignite_module()
        
        # 0.1 Run dstl_detect() to identify device attributes
        # 0.2 Set Normal Functionality Mode
        # 1. Insert SIM PIN and attach to network
        # 2. Enable all radio bands for all RATs

        # 0.1
        test.dut.dstl_detect()      

        # 0.2
        test.log.info("Set Normal Functionality Mode")
        test.dut.dstl_set_full_functionality_mode()

        # 1
        test.log.info("Insert SIM PIN and attach to network")
        status = dstl_register_to_network(test.dut)
        test.expect(status, critical = True)

        # 2
        test.log.info("Enable all radio bands for all RATs")
        status = test.dut.dstl_set_all_radio_bands()
        test.expect(status, critical = True)

    def run(test):

        # 1. Sleep for  10 s
        test.sleep(10)

        # 2. Measure plmn_search and plmn_search_time KPIs
        status = test.dut.dstl_get_available_operator_rats(timeout=300)
        test.expect(status)

    def cleanup(test):

        test.log.info("Restart module")
        test.dut.dstl_restart()

        test.sleep(20)


if "__main__" == __name__:
    unicorn.main()
