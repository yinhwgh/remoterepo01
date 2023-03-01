#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0105021.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_identification import dstl_get_bootloader

class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):
        test.log.step("0. Execute AT+CFUN=1,1")
        test.expect(dstl_restart(test.dut))

        test.log.step("1. Execute AT^SCFG=\"MEopMode/Factory\",\"none\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"none\"",
                                                 "+CME ERROR: SIM PIN required"))

        test.log.step("2. Execute AT^SCFG=\"MEopMode/Factory\",\"all\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"all\"",
                                                 "+CME ERROR: SIM PIN required"))

        test.log.step("3. Enter PIN")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)

        test.log.step("4. Execute AT^SCFG=\"MEopMode/Factory\",\"none\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"none\"",
                                                 ".*OK.*"))
        test.sleep(5)

        test.log.step("5. Execute AT^SCFG=\"MEopMode/Factory\",\"all\"")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"all\"",
                                                 ".*OK.*"))
        test.expect(test.dut.at1.wait_for("^SYSSTART"))

    def cleanup(test):
        pass

if "__main__" == __name__:
   unicorn.main()