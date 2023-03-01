# responsible: marcin.kossak@globallogic.com
# location: Wroclaw
# TC0000001.001 template_dstl

import unicorn
from core.basetest import BaseTest

from dstl.template import dstl_dummy
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):

        """If we want to use targeted DSTL functions
        we should always import <detect> function from <dstl.init> and call it as a first step
        in setup method
        """

        dstl_detect(test.dut)

    def run(test):

        """Now <dstl_dummy> function is aware of the product and it will choose
        appropriate implementation"""

        test.dut.dstl_dummy()
        test.expect(test.dut.id)

    def cleanup(test):
        pass
