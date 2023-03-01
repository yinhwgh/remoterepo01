"""
author: katrin.kubald@thalesgroup.com
location: Berlin
TC-number: TC0093342.001 - Widetest_ECall_eCallSimple
intention: Perform one simple eCall
LM-No (if known): LM0003558.00x - eCall-Management (MSD, AT+CECALL, Progress and Error Indications)
used eq.: DUT-At1, PSAP
execution time (appr.): 2 minutes

"""
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.call.ecall.ecall_support import dstl_enable_ecall_urcs
from dstl.call.ecall.ecall_support import dstl_disable_ecall_urcs
from dstl.call.ecall.ecall_support import dstl_set_default_ecall_parameter
from dstl.call.ecall.ecall_support import dstl_init_dev
from dstl.call.ecall.ecall_support import dstl_perform_normal_ecall

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader


class Test(BaseTest):
    #psap_number = ""
    #psap_number = "+493038307462"
    #psap_number = test.psap_number_ericsson_public
    ecall_type = "0"  # test eCall
    pull_mode = "0"   # push mode

    def setup(test):

        Test.psap_number = test.psap_number_ericsson_public

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.dut.dstl_detect()
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
#        test.dut.dstl_collect_module_info()



        # restart the DUT module
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()

        test.log.step('Step 1: Init device settings - Start')
        test.dut.dstl_collect_result('Step 1: Init device settings', test.dut.dstl_init_dev())

        test.log.step('Step 2: Enable eCall URCs - Start')
        test.dut.dstl_collect_result('Step 2: Enable eCall URCs', test.dut.dstl_enable_ecall_urcs())

        test.log.step('Step 3: Set default eCall parameter - Start')
        test.dut.dstl_collect_result('Step 3: Set default eCall parameter', test.dut.dstl_set_default_ecall_parameter())


    def run(test):
       # test.psap_number = "+493038307462"
        #test.psap_number = test.psap_number_ericsson_public

        ecall_type_str = test.dut.dstl_get_ecall_type_str(test.ecall_type)
        msd_version = 2
        msd_test_ecall = True
        msd_automatic_ecall = False

        # perfom test eCall
        test.log.step('Step 4: Perform normal \'' + ecall_type_str + ' eCall\' - Start')
        test.dut.dstl_collect_result('Step 4: Perform normal \'' + ecall_type_str + 'eCall\'', test.dut.dstl_perform_normal_ecall(test))



    def cleanup(test):
        # Disable ecCall paramter
        test.log.step('Step 5: Disable eCall URCs - Start')
        test.dut.dstl_collect_result('Step 5: Disable eCall URCs', test.dut.dstl_disable_ecall_urcs())

        test.log.step('Step 6: Set default eCall parameter - Start')
        test.dut.dstl_collect_result('Step 6: Set default eCall parameter', test.dut.dstl_set_default_ecall_parameter())

        test.dut.dstl_show_scfg_sind()

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('** testcase log directory: ' + test.workspace + ' **')

        test.log.com(' ')
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')

if "__main__" == __name__:
    unicorn.main()
