#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0104292.001

import unicorn
import time
from core.basetest import BaseTest

from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import  dstl_enter_pin
from dstl.network_service.register_to_network import dstl_register_to_gsm

'''Currently,for serval only'''
class Test(BaseTest):
    def setup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.info('---------Test Begin -------------------------------------------------------------')
        test.log.info('1. Attach module to 2G Network.')
        test.dut.dstl_restart()
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_gsm())
        test.log.info('2. Use AT^SMONP command.')
        test.log.info('3. Compare response with proper section of AT Command Specification document.')
        test.expect(test.check_smonp_response_2g('SEARCH') or test.check_smonp_response_2g('CONN'))
        time.sleep(3)
        test.expect(test.check_smonp_response_2g('CONN'))
        test.log.info('4.Establish data connection and voice call.')
        test.establish_data_connection()
        test.log.info('5. Use AT^SMONP command.')
        test.log.info('6. Compare response with proper section of AT Command Specification document.')
        test.expect(test.check_smonp_response_2g('CONN'))
        test.log.info('7. Detach Network.')
        test.expect(test.dut.at1.send_and_verify('at+cops=2', 'OK', timeout=7))
        test.log.info('8. Use AT^SMONP Command.')
        test.log.info('9. Compare response with proper section of AT Command Specification document.')
        test.expect(test.check_smonp_response_2g('SEARCH'))
        test.log.info('---------Test End -------------------------------------------------------------')


    def establish_data_connection(test):
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","internet"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sica=1,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,srvtype,socket', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,conid,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siss=1,address,"socktcp://10.163.27.30:4444"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^siso=1', 'OK', wait_for='^SISW: 1,1'))
        test.expect(test.dut.at1.send_and_verify('at^sisw=1,10', '^SISW: 1,10,0'))
        test.dut.at1.send_and_verify('1111111111', wait_for='^SISR: 1,1')

    def check_smonp_response_2g(test,conn_state):
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", ".*OK.*"))
        if conn_state is 'SEARCH':
            if "^SMONP: Searching" in test.dut.at1.last_response:
                return True
            else:
                return False
        else:
            if "2G" in test.dut.at1.last_response:
                return True
            else:
                return False

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
