# responsible: katrin.kubald@thalesgroup.com
# location: Berlin
# test case: UNISIM01-???
# prerequisite setting in local.cfg:
#              http_proxy = '10.50.101.10:3128'
#              https_proxy = '10.50.101.10:3128'
#              smdp_base_url = 'https://icedemo-testlab-es2plus-in.stg.ondemandconnectivity.com:8443'

import unicorn
import re
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

import json
import datetime


class Test(BaseTest):
    """
    Init
    """
    matching_id_list = []

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' (UNISIM01-???) - Start *****')


    def run(test):
        result = True
#        iccid_list = ["89354010190601000013","8988247000102756910"]
        iccid_list = ["89354010190601000013"]


        # if test.iccid_file:
        #     #test.mctest_antenna_int = '3'
        #     pass
        # iccid_no = "89354010190601000013"
 #       iccid_no = "8988247000102756910"
#        iccid_list.append(iccid_no)

        for iccid in iccid_list:
            profile_info = test.dut.dstl_get_profile_info_from_smdp(iccid)
            if 'matchingId' in str(profile_info):
                matching_id = profile_info['matchingId']
                #matching_id = profile_info['matchingId']
                result_line = f'iccid: {iccid} - matching_id: {matching_id}'
                test.log.info(result_line)
                #matching_id_list.append(f'iccid: {iccid} - matching_id: {matching_id}')
                result = True and result
            else:
                if 'message' in str(profile_info):
                    message = profile_info['header']['functionExecutionStatus']['statusCodeData']['message']
                    result_line = f'iccid: {iccid} - message: {message}'
                    test.log.info(result_line)

                else:
                    result_line = f'iccid: {iccid} - comment: no information could be found for this iccid'
                    test.log.info(result_line)
                result = False and result

            test.matching_id_list.append(result_line)

        test.log.step('Step 1: Check if all matching_id could be found - Start')
        test.dut.dstl_collect_result('Step 1: Check if all matching_id could be found', result)




    def cleanup(test):

        test.dut.dstl_print_results()

        test.log.com(' ')
        test.log.com('****************************')
        test.log.com('Matching ID results:')
        for line in test.matching_id_list:
            test.log.com(line)
        test.log.com('****************************')
        test.log.com(' ')

        test.log.com('***** Testcase: ' + test.test_file + ' (UNISIM01-???) - End *****')


if "__main__" == __name__:
    unicorn.main()
