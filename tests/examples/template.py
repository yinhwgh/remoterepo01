# responsible: marcin.kossak@globallogic.com
# location: Wroclaw
# TC0000001.001 template

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    JIRA_ID: str = ''   # testcase ID in JIRA, optional

    def setup(test):
        """
        [ Test preconditions ]
        """
        pass

    def run(test):
        """
        [ Actual test steps ]
        - Run identify method on all
        devices used in the test, e.g.: dut, r1, r2, etc...
        if you want them to be properly handled by the DSTL mechanism.
        Run also get imei to identify the modules.
        """
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

        """
        - Use at least one <test.expect> call to properly set test verdict.
        """
        test.expect(True)

    def cleanup(test):
        """
        [ Test postconditions ]
        """
        pass


if "__main__" == __name__:
    unicorn.main()
