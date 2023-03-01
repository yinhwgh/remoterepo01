"""
author: wolfgang.koppe@thalesgroup.com, katrin.kubald@thalesgroup.com, duangkeo.krueger@thalesgroup.com
location: Berlin
TC-number: TC0105527.001 - GnssPowersavePsm
intention: The power saving of the GPS engine be configured.
LM-No (if known): LM0003030.004 - Power Saving Configuration of GPS-Engine
                             Serval_01, 03
used eq.: DUT-At1
execution time (appr.): 1 min
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()
        
    def run(test):
        test.log.step('Step 1: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.log.step('Step 2: Check invalid setting for powersave parameter (set to on) - Start')
        test.dut.dstl_collect_result('Step 2: Check invalid setting for powersave parameter(set to on)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"on\"", ".*ERROR.*"))

        test.log.step('Step 3: Check invalid setting for powersave parameter (set to 2) - Start')
        test.dut.dstl_collect_result('Step 3: Check invalid setting for powersave parameter (set to 2)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"2\"", ".*ERROR.*"))

        test.log.step('Step 4: Activate powersave parameter (set to 1) - Start')
        test.dut.dstl_collect_result('Step 4: Activate powersave parameter to (set to 1)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"1\"", "OK"))

        test.log.step('Step 5: Restart Module - Start')
        test.dut.dstl_collect_result('Step 5: Restart Module', test.dut.dstl_restart())
        test.sleep(5)

        test.log.step('Step 6: Check powersave parameter after restart - Start')
        test.dut.dstl_collect_result('Step 6: Check powersave parameter after restart', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\"", ".*1.*OK.*"))

        test.log.step('Step 7: Deactivate powersave parameter (set to 0) - Start')
        test.dut.dstl_collect_result('Step 7: Deactivate powersave parameter (set to 0)', test.dut.at1.send_and_verify("at^sgpsc= \"Power/Psm\",\"0\"", "OK"))


    def cleanup(test):
        test.log.step('Step 8: Initialise GNSS engine to default setting - Start')
        test.dut.dstl_collect_result('Step 8: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss())

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

    if "__main__" == __name__:
        unicorn.main()
