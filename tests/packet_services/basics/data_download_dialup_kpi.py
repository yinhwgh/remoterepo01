#responsible: mateusz.wasielewski@globallogic.com
#location: Wroclaw
#TC

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.devboard.ignite_module import dstl_ignite_module
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.configuration.scfg_radio_band import dstl_set_all_radio_bands
from dstl.auxiliary.restart_module import dstl_restart

from dstl.packet_domain.speedtest import dstl_test_dialup_throughput

class Test(BaseTest):

    """
        This procedure performs download throughput speed test using dial-up
    """

    def setup(test):

        test.dut.dstl_ignite_module()

        # 0.1 Run dstl_detect() to identify device attributes
        # 0.2 Set Normal Functionality Mode
        # 1. Unlock SIM PIN
        # 2. Switch to automatic network selection mode
        # 3. Enable all radio bands for all RATs
        # 4. Enable PS Domain auto attach
        # 5. Restart module to apply settings
        # 6. Ensure that the correct APN is specified
        # 7. Insert SIM PIN and attach to network

        # 0.1
        test.dut.dstl_detect()

        # 0.2
        test.log.info("Set Normal Functionality Mode")
        test.dut.dstl_set_full_functionality_mode()

        # 1
        test.log.info("Insert SIM PIN")
        status = dstl_enter_pin(test.dut)
        test.expect(status, critical = True)

        # 2
        test.log.info("Switch to automatic network selecion mode")
        status = test.dut.at1.send_and_verify("at+cops=0", expect="OK")
        test.expect(status, critical = True)

        # 3
        test.log.info("Enable all radio bands for all RATs")
        status = test.dut.dstl_set_all_radio_bands()
        test.expect(status, critical = True)

        # 4
        test.log.info("Enable PS Domain auto attach")
        status = test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', expect="OK")
        test.expect(status, critical = True)

        # 5
        status = test.dut.dstl_restart()
        test.expect(status, critical = True)

        # 6
        test.log.info("Ensure that the correct APN is specified")
        status = test.dut.at1.send_and_verify('AT+CGDCONT?', expect='internet')
        if not status:
            test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","internet"', expect='OK')
            status = test.dut.at1.send_and_verify('AT+CGDCONT?', expect='internet')
        test.expect(status, critical=True)

        # 7
        test.log.info("Insert SIM PIN and attach to network")
        status = dstl_register_to_network(test.dut)
        test.expect(status, critical = True)

    def run(test):

        # 1. Sleep for  10 s
        test.sleep(10)

        # 2. Measure data_download_dialup_Xg_throughput
        status = test.dut.dstl_test_dialup_throughput(direction=0)
        test.expect(status)

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
