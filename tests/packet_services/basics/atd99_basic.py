#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0092085.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.call.switch_to_command_mode import *
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.security.lock_unlock_sim import *

class Test(BaseTest):
    """
    TC0092085.002 -  Atd99Basic
    Basic ATD*99# test
     debugged by serval
    """
    def setup(test):
        dstl_detect(test.dut)
    def run(test):
        test.log.step("1.1 Check command without PIN")
        test.dut.dstl_lock_sim()
        dstl_restart(test.dut)
        test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*SIM PIN required.*'))
        test.log.step("1.2 Check command with PIN")
        dstl_enter_pin(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        test.log.step("2.1 Check ATD*99# ")
        test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT", timeout=60))
        test.log.step("2.2 Check +++ commands")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        test.log.step("3. Check ATD with invalid parameters")
        test.expect(test.dut.at1.send_and_verify('ATD*98#', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('ATD*9#', '.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('ATD*ab#', '.*ERROR.*'))
        dstl_restart(test.dut)
    def cleanup(test):
        test.dut.at1.send_and_verify('ATI', '.*OK*')
        test.dut.at1.send_and_verify('AT&F', '.*OK*')
        pass
if __name__ == "__main__":
    unicorn.main()
