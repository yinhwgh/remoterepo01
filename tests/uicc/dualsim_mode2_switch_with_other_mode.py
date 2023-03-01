#author: jin.li@thalesgroup.com
#location: Dalian
#TC0095507.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.configuration import dual_sim_operation
from dstl.configuration.dual_sim_operation import dstl_switch_to_sim_slot2
from dstl.network_service.register_to_network import dstl_enter_pin

class Test(BaseTest):
    '''
    "TC0095507.001
     Intention:Test Dual SIM Mode2 switch with other mode.
     subscriber: 1 with
     define 2 sim card info in local.cfg: dut_sim=   ; dut_sim2 =
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))


    def run(test):
        test.expect(test.dut.dstl_enable_dual_sim_mode(2))
        test.expect(test.dut.dstl_switch_to_sim_slot2)
        test.expect(test.dut.dstl_enter_pin(test.dut.sim2))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect=test.dut.sim2.imsi))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std".', expect='.*ERROR'))
        test.expect(not test.dut.dstl_enable_dual_sim_mode(1))
        test.expect(test.dut.dstl_disable_dual_sim_mode())
        test.expect(test.dut.at1.send_and_verify('at^scfg?', expect='.*^SCFG: "SIM/CS","0"', waitfor="OK"))
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect=test.dut.sim.imsi))

    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
