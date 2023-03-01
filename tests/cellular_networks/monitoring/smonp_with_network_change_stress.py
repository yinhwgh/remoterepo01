#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0102618.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.network_service import check_cell_monitor_parameters
import time

class Test(BaseTest):
    '''
    TC0102618.001 - SmonpwithNetworkChange_Stresstest
    Intention: To check if at^smonp response ok and module work well when network change.
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)
        test.dut.dstl_enter_pin()


    def run(test):
        test.expect(test.dut.at2.send_and_verify('at+creg=2','OK'))

        test.log.info('***Test Start***')
        test.time_start = time.time()
        #stress test for 4h (14400s)
        t1 = test.thread(test.func_1,test.dut.at1)
        t2 = test.thread(test.func_2, test.dut.at2)



    def cleanup(test):
       test.log.info('***Test End***')

    def func_1(test,port):
        while(time.time()-test.time_start<14400):
            test.expect(port.send_and_verify('at^smonp','.*OK.*'))
            test.sleep(2)

    def func_2(test,port):
        while (time.time() - test.time_start <14400):
            test.expect(port.send_and_verify('at^sxrat=0', '.*OK.*',wait_for='CREG: 1',timeout=20))
            test.expect(port.send_and_verify('at^sxrat=2', '.*OK.*', wait_for='CREG: 1', timeout=20))
            test.expect(port.send_and_verify('at^sxrat=3', '.*OK.*', wait_for='CREG: 1',timeout=10))





if "__main__" == __name__:
    unicorn.main()

