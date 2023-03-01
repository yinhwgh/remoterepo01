#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0088060.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    '''
    TC0088060.001 - Cereg
    Subscriber :1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.sleep(5)

        test.check_para = []
        test.invalid_para = []

    def run(test):
        test.log.info('1) Enter the test command (shall be not accepted)')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=?','ERROR'))

        test.log.info('2) Enter the SIM PIN')
        test.dut.dstl_enter_pin()
        test.sleep(5)

        test.log.info('3) Enter the test command (shall be accepted)')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=?', 'OK'))
        if 'CEREG: (0-2,4)' in test.dut.at1.last_response:
            test.check_para=[0,1,2,4]
            test.invalid_para = [-1,3,5,'a']

        elif 'CEREG: (0-2)' in test.dut.at1.last_response:
            test.check_para=[0,1,2]
            test.invalid_para = [-1, 3, 666, 'a']

        elif 'CEREG: (0-5)' in test.dut.at1.last_response:
            test.check_para=[0,1,2,3,4,5]
            test.invalid_para = [-1, 6, 5, 'a']

        for i in test.check_para:
            test.log.info(f'Start test <n> = {i}')
            test.step3to10(i)

        test.log.info('11) Enter the write command with an illegal parameter value (shall be rejected)')
        for i in test.invalid_para:
            test.expect(test.dut.at1.send_and_verify(f'AT+CEREG={i}','ERROR'))

        test.log.info('12) Enter the read command (the last legal parameter value shall be shown)')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG?', f'\+CEREG: {test.check_para[-1]},1.*OK.*'))


    def cleanup(test):
        pass

    def step3to10(test,n):
        test.log.info('4) Enter the write command (shall be accepted)')
        test.expect(test.dut.at1.send_and_verify(f'AT+CEREG={n}', 'OK'))

        test.log.info('5) Manually deregister from the network')
        test.log.info('6) if n is not 0, wait up to few seconds for +CEREG: 0')
        if n == 0:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG:.*', timeout=60) == False)
        else:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK', wait_for='\+CEREG: 0'))

        test.log.info('7) Enter the read command')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG?', f'\+CEREG: {n},0.*OK.*'))

        test.log.info('8) Manually register to the network')
        test.log.info('9) If n is not 0, wait up to few seconds for 2 URCs ')
        if n == 0:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK'))
            test.expect(test.dut.at1.wait_for('.*\\+CEREG:.*', timeout=60) == False)
        elif n ==1:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', wait_for='\+CEREG: 2.*\+CEREG: 1.*'))

        elif n ==2:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', wait_for='\+CEREG: 2.*\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*'))

        elif n ==3:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', wait_for='\+CEREG: 2.*\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,[0-9]{1}.*'))

        elif n ==4:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', wait_for='\+CEREG: 2.*\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,\"?[0-9]{1}\"?,,,\"?[0-1]{8}\"?,\"?[0-1]{8}\"?.*'))

        elif n == 5:
            test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', wait_for='\+CEREG: 2.*\+CEREG: 1,\"?[0-9,a-f,A-F]{4}\"?,\"?[0-9,a-f,A-F]{8}\"?,\"?[0-9]{1}\"?,,,\"?[0-1]{8}\"?,\"?[0-1]{8}\"?.*'))

        test.log.info('10) Enter the read command ')
        test.expect(test.dut.at1.send_and_verify('AT+CEREG?', f'\+CEREG: {n},1.*OK.*'))



if "__main__" == __name__:
    unicorn.main()
