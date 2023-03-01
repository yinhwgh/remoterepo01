#responsible: xueping.zhang@thalesgroup.com
#location: Beijing
#TC

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard


class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        test.dut.dstl_reset_with_vbatt_via_dev_board()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
