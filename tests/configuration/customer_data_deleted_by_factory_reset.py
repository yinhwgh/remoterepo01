#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0104488.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.configuration import reset_to_factory_default_state

class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)

    def run(test):

        test.log.step("1. Set command value of AT^SCFG=\"MEopMode/Factory\",\"none\" and restart the module.")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Factory\",\"none\"", ".*OK.*"))
        test.expect(dstl_restart(test.dut))

        test.log.step("2. Create directory using AT^SFSA command.")
        test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"mkdir\", \"a:/test\"", "^SFSA: 0"))

        test.log.step("3. Display the created directory.")
        test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"ls\",\"a:/\"", "^SFSA: test/"))

        test.log.step("4. Restart the module and check if created directory is still exist.")
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"ls\",\"a:/\"", "^SFSA: test/"))

        test.log.step("5. Execute AT^SCFG=\"MEopMode/Factory\",\"all\" command and restart the module.")
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(5)
        test.expect(test.dut.dstl_reset_to_factory_default())
        test.expect(dstl_restart(test.dut))

        test.log.step("6. Check if directory has been removed.")
        test.expect(test.dut.at1.send_and_verify("AT^SFSA=\"ls\",\"a:/\"", ".*OK.*"))
        test.expect(not "^SFSA: test/" in test.dut.at1.last_response)

    def cleanup(test):
        pass

if "__main__" == __name__:
   unicorn.main()