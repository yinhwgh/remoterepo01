# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_expect

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
        Examples:
        """
        pass

    def run(test):
        """Run method.

        Actual test steps.
        """
        # expect true
        test.expect(True)
        test.expect(not False)

        # expect equal
        test.expect(1 == 1)

        # expect lower than
        test.expect(1 < 2)

        # expect higher than
        test.expect(2 > 1)

        #expect not equal
        test.expect(1 != 2)

        #joining expectations
        test.expect(1 != 2 and 2 > 1)
        test.expect(1 != 2 or 2 <= 1)

        """
        Examples:
            
            # expect test.config.local_config_path parameter is set
            test.expect(test.config.local_config_path)
            
            # expect r1 device is defined
            test.expect(test.r1)
            
        """
        pass

    def cleanup(test):
        """Cleanup method.

        Steps to be executed after test run steps.
        """
        pass


if "__main__" == __name__:
    unicorn.main()
