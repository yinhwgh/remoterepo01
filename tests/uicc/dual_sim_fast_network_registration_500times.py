#author: yandong.wu@thalesgroup.com
#location: Dalian
#TC0092003.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.security import set_sim_waiting_for_pin1
from dstl.auxiliary import check_urc

class Test(BaseTest):
    '''
    TC0092003.001 - DualSimFastNetworkRegistration500times
    Intention: Load test to verify stability of Fast Network Switching (FNS) in 500 loops
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+creg=1', 'OK'))

    def run(test):
        loop = 500
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPIO/mode/FNS","std"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/DualMode","1"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","0"', 'OK'))
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_network())

        test.log.info('---loop 500 times start---')
        for i in range(2, loop):
            if (i % 2 == 0):
                test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","3"', 'OK'))
                test.sleep(10)
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.dstl_register_to_network())

            else:
                test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/CS","0"', 'OK'))
                test.sleep(10)
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.dstl_register_to_network())
        test.log.info('---loop 500 times end---')

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^scfg="Sim/DualMode","0"', 'OK'))
        pass



if '__main__' == __name__:
    unicorn.main()
