# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0095639.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init


class Test(BaseTest):

    def setup(test):

        test.dut.detect()

    def run(test):

        test.dut.dstl_enter_pin()

        for i in range(1, 500):
            test.log.info("Iteration without interrupt: {}".format(i))
            test.expect(test.dut.at1.send_and_verify('at+copn', '.*\sOK\s.*', timeout=20))
            test.sleep(1)

        for i in range(1, 200):
            test.log.info("Iteration with interrupt: {}".format(i))
            test.expect(
                test.dut.at1.send_and_verify('at+copn', '', wait_for=''))
            test.expect(
                test.dut.at1.send_and_verify('at+copn', 'CME ERROR: unknown'))

        test.sleep(3)
        test.expect(test.dut.at1.send_and_verify('ati', 'OK'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
