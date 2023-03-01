#author: xiaolin.liu@thalesgroup.com
#location: Dalian
#TC0092776.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import dual_sim_operation
from dstl.configuration.dual_sim_operation import dstl_switch_to_sim_slot2

class Test(BaseTest):
    '''
    TC0092776.001 - TPAtSpicFunctionPN
    Intention: This test case is to check PIN counter function while in SPIC command is set to “PN”, means PH-NET PIN.
        '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at^scfg="SIM/CS","SIM1"', 'OK'))
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step('1.Get the "MNC.MCC" for sim slot1.')
        data1= test.get_operator()

        test.log.step('2.Get the "MNC.MCC" for sim slot2.')
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.dut.dstl_restart()
        data2 = test.get_operator()
        if data1!=data2:
            test.log.info(f'Sim "MNC.MCC"_1: {data1}, Sim "MNC.MCC"_2: {data2}')
        else:
            test.log.error("Two sim cards cannot belong to the same network operator")

        test.log.step('3.Lock the module with particular network for SIM 1.')
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(3)
        password = 12345678
        test.expect(test.dut.at1.send_and_verify(f'at+clck="PN",1,{password},,"{data1}"', 'OK'))

        test.log.step('4.Switch to SIM2 and enter SIM PIN.')
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify(f'AT+CPIN="{test.dut.sim2.pin1}"', 'OK'))
        test.sleep(3)

        test.log.step('5.Check the PIN status and PIN counter by using CPIN and SPIC.')
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "+CPIN: PH-NET PIN"))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 10'))

        test.log.step('6.Enter wrong PN password, at the same time check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN="22222222"', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 9'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC?', '\^SPIC: PH-NET PIN'))

        test.log.step('7.Enter correct PIN and then check the PIN counter.')
        test.expect(test.dut.at1.send_and_verify(f'AT+CPIN={password}', 'OK'))
        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'READY'))
        test.expect(test.dut.at1.send_and_verify('AT^SPIC', '\^SPIC: 10'))


    def get_operator(test):
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0,2", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", "OK"))
        last_response = test.dut.at1.last_response
        data_array = last_response.split('"')
        result = data_array[1][0:3] + '.' + data_array[1][3:5]
        return result


    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
