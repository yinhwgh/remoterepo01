# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_dstl_simple

#!/usr/bin/env unicorn
"""Unicorn tests.template.py module
This file represents Unicorn test template, that should be the base for every new test using DSTL
"""

import unicorn
from core.basetest import BaseTest


"""
Here, needed DSTL function is imported
`dstl_dummy` function is located in `dstl\template.py`
"""
from dstl.template import dstl_dummy
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Test which presents basic use of DSTL functions
    """

    def setup(test):
        pass

    def run(test):
        """
        Function "dummy" can be used in two ways:
        - as a regular function with arguments (device is always first argument)
        - as a device method (preferred)

        dummy(test.dut)
        test.dut.dummy()
        """

        test.dut.dummy()

        test.expect(not test.dut.platform)
        test.expect(not test.dut.project)
        test.expect(not test.dut.product)

        """until now we don't know module details
        so we call <detect> function to identify it.
        """
        test.dut.dstl_detect()


        """Now <platform>, <project> and <product> attributes should be populated.
        """
        test.expect(test.dut.platform)
        test.expect(test.dut.project)
        test.expect(test.dut.product)

        """
        # if DSTL function returns value:
        value = test.dut.dummy()
        test.expect(value)        
        """

        """
        <restart> function from `dstl/template.py`
        
        from dstl.template import restart
        restart(test.dut)
        test.dut.restart()
        """

        """
        DSTL function may have additional parameters which can be passed:
        
        from dstl.template import restart_timed
        restart_timed(test.dut, 90)
        test.dut.restart_timed(90)
        """
        pass

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
