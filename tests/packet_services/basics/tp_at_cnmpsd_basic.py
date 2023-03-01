# author: johann.suhr@thalesgroup.com
# location: Berlin
# TC0094387

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.security.lock_unlock_sim import *


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.dut.dstl_unlock_sim()
        test.log.info('Run Test with unlocked SIM ...')
        test.check_cnmpsd()

        test.dut.dstl_lock_sim()
        test.log.info('Run Test with locked SIM ...')
        test.check_cnmpsd()

    def check_cnmpsd(test):
        test.expect(test.dut.at1.send_and_verify('AT+CNMPSD=?'))
        test.expect(test.dut.at1.send_and_verify('AT+CNMPSD'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
