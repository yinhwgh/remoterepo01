#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0106137.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
from dstl.auxiliary.restart_module import dstl_restart

class Test(BaseTest):
    """
      TC0106137.001 ECM_PPP_Linux
    """

    def setup(test):
        dstl_detect(test.dut)
        test.log.info("USB Service Set for ECM")
        test.dut.at1.send_and_verify('AT^SSRVSET="actSrvSet",1', "OK")
        dstl_restart(test.dut)
    def run(test):
        test.log.step("Register on Network")
        dstl_register_to_network(test.dut)
        test.log.step("Enter Data State - ECM PPP LINUX")
        test.expect(test.dut.at1.send_and_verify('AT+CGDATA=PPP,1', '.*CONNECT', wait_for="CONNECT", timeout=10))
        test.log.step("Quit Data State")
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.log.info("Check at command mode")
        test.expect(test.dut.at1.send_and_verify('AT', 'OK'))
        test.expect(test.dut.at1.send_and_verify('ATI', 'OK'))
    def cleanup(test):
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()
