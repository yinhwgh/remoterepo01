# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0010243.001,TC0010243.002

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service import register_to_network

class Test(BaseTest):
    """
    TC0010243.001	Gprs__attach_detach_stress
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_gsm()
       
    def run(test):
        test.log.step('SCENARIO 1: steps 1-3 will be realized 30 times')
        test.log.step('Step 1: Attach module to the network ')
        test.log.step('Step 2: Check module state in network')
        test.log.step('Step 3: Deattach module from network')
        for i in range(1,31):
            test.log.info('Loop times: '+str(i))
            test.expect(test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*",timeout=60))
            test.sleep(3)
            test.expect(
                test.dut.at1.send_and_verify('AT^SMONI',
                                             '.*SMONI: 2G,.*,.*,\d+,\d+,.*,.*,.*,.*,.*,.*,.*,.*,.*,NOCONN'))
            test.expect(test.dut.at1.send_and_verify("at+cgatt=0", ".*OK.*", timeout=60))
            
            
        test.log.step('SCENARIO 2:steps 4-5 will be realized 100 times')
        test.log.step('Step 4: Attach module to the network')
        test.log.step('Step 5: Deattach module from network')
        for i in range(1,101):
            test.log.info('Loop times: '+str(i))
            test.expect(test.dut.at1.send_and_verify("at+cgatt=1", ".*OK.*", timeout=60))
            test.expect(test.dut.at1.send_and_verify("at+cgatt=0", ".*OK.*", timeout=60))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))




if "__main__" == __name__:
    unicorn.main()
