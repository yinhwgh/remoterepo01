"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0096566.001 - GNSSAntennaConfig
intention: Command for controll power supply for GNSS  antenna must not visible now.
LM-No (if known): LM0003824.002 - Bobcat_01,04,06
used eq.: DUT-At1
execution time (appr.): 50 sec
"""


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.gnss import gnss
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()
        
    def run(test):

        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        test.log.step('Step 2: Check if \'Power/Antenna\' is visible in test command - Start')
        test.dut.at1.send_and_verify("at^sgpsc=?", ".*OK.*")
        data = test.dut.at1.last_response
        test.log.com("data:\n" + data)
        if 'Power/Antenna' in data:
            test.dut.dstl_collect_result('Step 2: Check \'Power/Antenna\' is visible in test command, but should not', False)
        else:
            test.dut.dstl_collect_result('Step 2: Check \'Power/Antenna\' is not visible in test command', True)

        test.log.step('Step 3: Check if \'Power/Antenna\' is visible in read command - Start')
        test.dut.at1.send_and_verify("at^sgpsc?", ".*OK.*")
        data = test.dut.at1.last_response
        test.log.com("data:\n" + data)
        if 'Power/Antenna' in data:
            test.dut.dstl_collect_result('Step 3: Check \'Power/Antenna\' is visible in read command, but should not', False)
        else:
            test.dut.dstl_collect_result('Step 3: Check \'Power/Antenna\' is not visible in read command', True)

        test.log.step('Step 4: Check if \'Power/Antenna\' is internal command - Start')
        test.dut.at1.send_and_verify("at^sgpsc=\"Power/Antenna\"", ".*OK.*")
        data = test.dut.at1.last_response
        test.log.com("data:\n" + data)
        if 'Power/Antenna' in data:
            test.dut.dstl_collect_result('Step 4: Check if \'Power/Antenna\' is internal command', True)
        else:
            test.dut.dstl_collect_result('Step 4: Check if \'Power/Antenna\' is internal command, but should be', False)

    def cleanup(test):
        test.log.step('Step 5: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 5: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
