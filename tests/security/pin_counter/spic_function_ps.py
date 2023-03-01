#author: xiaolin.liu@thalesgroup.com
#location: Dalian
#TC0092779.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import dual_sim_operation
from dstl.configuration.dual_sim_operation import dstl_switch_to_sim_slot2

class Test(BaseTest):
    '''
    TC0092779.001 - TPAtSpicFunctionPS
    Intention: This test case is to check PIN counter function while in SPIC command is set to “PS”, means PH-SIM PIN.
        '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/CS","SIM1"', 'OK'))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step('1.Lock the module with this SIM card using CLCK command.')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        password = 12345678
        test.expect(test.dut.at1.send_and_verify(f'at+clck="PS",1,{password}', 'OK'))

        test.log.step('2.Switch to SIM2 and enter SIM PIN.')
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(f'AT+CPIN="{test.dut.sim2.pin1}"', 'OK'))
        test.sleep(3)

        test.log.step('3.Check the PIN status and PIN counter by using CPIN and SPIC.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "+CPIN: PH-SIM PIN"))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 10'))

        test.log.step('4.Enter wrong PN password, at the same time check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN="22222222"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 9'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC?', '\^SPIC: PH-SIM PIN'))

        test.log.step('5.Enter correct PIN and then check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPIN={password}', 'OK'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'READY'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 10'))



    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/CS","SIM1"', 'OK'))


if '__main__' == __name__:
    unicorn.main()
