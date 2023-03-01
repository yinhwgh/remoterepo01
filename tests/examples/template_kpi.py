# responsible: tomasz.witka@globallogic.com
# location: Wroclaw 
# TC0000001.001 template_kpi

#!/usr/bin/env unicorn
"""Unicorn tests.template.py module

This file represents Unicorn test template, that should be the base for every new test. Test can be executed with
unicorn.py and test file as parameter, but also can be run as executable script as well. Code defines only what is
necessary while creating new test. Examples of usage can be found in comments. For more details please refer to
basetest.py documentation.

"""

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

class Test(BaseTest):
    """Test class that inherits BaseTest.

    Every new test file should define class named Test, that inherits from BaseTest. Test class definition should also
    contain following methods: setup (executed before test is run), run (actual test steps), cleanup (steps that should
    be executed after test has finished).
    """

    def setup(test):
        """Setup method.
        Steps to be executed before test is run.
        """
        pass

    def run(test):
        """Run method.
        Actual test steps.
        """
        test.kpi_store(name="num_kpi", type="num", value=6, device=test.dut)
        test.kpi_store(name="bin_kpi", type="bin", value=True, device=test.dut)
        test.kpi_store(name="bin_kpi", type="bin", value=4, total=6, device=test.dut)


        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        pass


if "__main__" == __name__:
    unicorn.main()
