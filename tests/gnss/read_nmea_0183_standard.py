"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096532.001 - ReadNMEA0183Standard
intention: Shows the current implemented of NMEA 0183 Interface Standard - check the NMEA protocol version
LM-No (if known): LM0006518.00x - Bobcat, Serval, Viper
used eq.: DUT-At1
execution time (appr.): 1 sec
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()

    def run(test):

        protcol_version = "-1"
        if test.dut.project == 'BOBCAT':
            if test.dut.step == '2|3':
                protcol_version = "4.10"
            else:
                protcol_version = "\"4\",\"10\""
        elif test.dut.project == 'MIAMI':
            protcol_version = "4"
        elif test.dut.project == 'SERVAL':
            protcol_version = "4.10"
        elif test.dut.project == 'VIPER':
            protcol_version = "4.10"

        test.dut.at1.send_and_verify("at^sgpsc?")

        test.log.step('Step 1: Check the NMEA 0183 Interface Standard (protocol version) - Start')
        test.dut.dstl_collect_result('Step 1: Check the NMEA 0183 Interface Standard (protocol version)', test.dut.at1.send_and_verify("at^sgpsc=\"nmea/version\"", protcol_version))

    def cleanup(test):

        test.dut.nmea.read()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
