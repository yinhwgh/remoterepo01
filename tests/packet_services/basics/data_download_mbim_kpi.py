#responsible: mateusz.wasielewski@globallogic.com
#location: Wroclaw
#TC

import unicorn
from core.basetest import BaseTest
from dstl.devboard.ignite_module import dstl_ignite_module
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.configuration.scfg_radio_band import dstl_set_all_radio_bands
from dstl.packet_domain.speedtest import dstl_test_mbim_throughput

class Test(BaseTest):

    """
        data_download_mbim
        This procedure measures download throughput using mbim
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

        # 1. Wait 10 s
        # 2. Measure data_download_mbim

        # 1
        test.log.info("Wait 10 seconds")
        test.sleep(10)

        # 2
        status = test.dut.dstl_test_mbim_throughput(direction=0)
        test.expect(status)

    def cleanup(test):
        test.sleep(30)
        pass

if "__main__" == __name__:
    unicorn.main()



