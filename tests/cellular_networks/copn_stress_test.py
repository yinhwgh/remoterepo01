#responsible: baris.kildi@thalesgroup.com
#location: Berlin
#TC0095639.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module


class Test(BaseTest):
    """ Read mobile operator names by calling 'at+copn' 500 times and wait for 'OK"
    """
    def setup(test):

        test.dut.dstl_detect()

    def run(test):

        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()

        for i in range(0,500):
            test.log.info("Loop: {}".format(i))
            test.expect(test.dut.at1.send_and_verify('at+copn', wait_for=".*\sOK\s.*"))
            test.sleep(1)



    def cleanup(test):
        pass
if "__main__" == __name__:
    unicorn.main()
