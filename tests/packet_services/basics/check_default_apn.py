#responsible: maik.roge@thalesgroup.com
#location: BLN
#TC0095978.001

import unicorn
from core.basetest import BaseTest
import re
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Test(BaseTest):
    """
      	TC0095978.001 - CheckDefaultAPN
    PDP context for each serial port (or virtual serial port) can be active by Qos setting.

    """
    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        

    def run(test):
        
        test.log.info('1.Check APN')
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'SIM PIN'))
        test.dut.dstl_enter_pin()
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', 'READY'))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*OK.*'))
        
        
    def cleanup(test):
        
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.dut.at1.send_and_verify("AT&W", ".*OK.*")
        
        
    if "__main__" == __name__:
        unicorn.main()
