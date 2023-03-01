#responsible: mateusz.wasielewski@globallogic.com
#location: Wroclaw
#TC

import unicorn

from core.basetest import BaseTest
import time
from dstl.auxiliary.init import dstl_detect
from dstl.devboard.ignite_module import dstl_ignite_module
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.scfg_radio_band import dstl_set_all_radio_bands
from dstl.configuration.set_autoattach import dstl_enable_ps_autoattach
from dstl.kpi_measurement.attach_kpi_measure import attach_kpi_measure
from dstl.network_service.attach_to_network import attach_to_network, enter_pin

class Test(BaseTest):


    def setup(test):
        test.dut.dstl_ignite_module()
        # 0.1 Run dstl_detect() to identify device attributes
        # 0.2 Set Normal Functionality Mode
        # 1. Unlock SIM PIN
        # 2. Switch to automatic network selection mode
        # 3. Enable all radio bands for all RATs
        # 4. Enable PS Domain auto attach
        # 5. Enable the autoselection of provider profiles
        # 6. Restart module to apply settings
        # 7. Insert SIM PIN and attach to network

        # 0.1
        test.dut.dstl_detect()

        if test.dut.project.upper() == 'SERVAL':
            # Distinction here is needed, because SERVAL_100_054B was not able to
            # process some commands (e.g. 'at+cops=0') before receiving '+CREG: 1'.
            #
            # Moreover SERVAL does not support some commands mentioned in preconditions.

            # 0.2
            test.log.info("Set Normal Functionality Mode")
            test.dut.at1.send_and_verify("at+cfun=1", expect="OK")

            # 1
            # wait for attach added 
            test.log.info("Insert SIM PIN and attach to network")
            status = attach_to_network(test.dut)
            test.expect(status, critical = True)

            # 2
            test.log.info("Switch to automatic network selecion mode")
            status = test.dut.at1.send_and_verify("at+cops=0", expect="OK")
            test.expect(status, critical = True)

            # 3
            status = test.dut.dstl_set_all_radio_bands()
            test.expect(status, critical = True)

            # 4
            test.log.info("Enable PS Domain auto attach")
            status = test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', expect="OK")
            test.expect(status, critical = True)

            # 5
            # unsupported cmd

            # 6
            status = test.dut.dstl_restart()
            test.expect(status, critical = True)

            # 7
            test.log.info("Insert SIM PIN and attach to network")
            status = attach_to_network(test.dut)
            test.expect(status, critical = True)

            # 8
            # disable Power Save Mode to prevent interface sleep
            test.log.info("Disable Power Save Mode")
            status = test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","disabled"', expect="OK")
            test.expect(status, critical = True)
                
        else:

            # 0.2
            test.log.info("Set Normal Functionality Mode")
            test.dut.at1.send_and_verify("at+cfun=1", expect="OK")

            # 1
            test.log.info("Insert SIM PIN")
            status = enter_pin(test.dut)
            test.expect(status, critical = True)

            # 2
            test.log.info("Switch to automatic network selecion mode")
            status = test.dut.at1.send_and_verify("at+cops=0", expect="OK")
            test.expect(status, critical = True)

            # 3
            status = test.dut.dstl_set_all_radio_bands()
            test.expect(status, critical = True)

            # 4
            test.log.info("Enable PS Domain auto attach")
            status = test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"', expect="OK")
            test.expect(status, critical = True)

            # 5
            test.log.info("Enable the autoselection of provider profiles")
            status = test.dut.at1.send_and_verify('AT^SCFG="MEopMode/Prov/AutoSelect","on"', expect="OK")
            test.expect(status, critical = True)

            # 6
            status = test.dut.dstl_restart()
            test.expect(status, critical = True)

            # 7
            test.log.info("Insert SIM PIN and attach to network")
            status = attach_to_network(test.dut)
            test.expect(status, critical = True)

    def run(test):
        # 1. Wait 60 s for module to get into idle state
        # 2. Collect the attach KPI

        # 1
        test.log.info("Wait 60 seconds for module to get into idle state")
        time.sleep(60)

        # 2
        test.expect(test.dut.attach_kpi_measure(), critical=True)

    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
