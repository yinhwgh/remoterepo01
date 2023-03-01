# responsible: baris.kildi@thalesgroup.com
# location: Berlin
# Dummy test case which needs to be called at the end of serval product tests in Dev-CI


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim


class Test(BaseTest):
    '''
    Intention:
    Unlock PIN at the end of test campaign
    Subscriber: 1
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(10)

    def run(test):
        test.log.info('Unlock PIN')
        test.dut.dstl_unlock_sim()


    def cleanup(test):
        test.log.info('***Test End, clean up***')



if "__main__" == __name__:
    unicorn.main()
