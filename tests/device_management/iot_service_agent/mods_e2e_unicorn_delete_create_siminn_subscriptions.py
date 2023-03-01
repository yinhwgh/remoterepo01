# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-128

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.auxiliary.write_json_result_file import *

testkey = "UNISIM01-128"

class Test(BaseTest):
    """
    Find all created all subscriptions from Transatel-list on MODS-server,
    get the last one, delete it and create it again
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()
        # TEMPORARY solution. Should not be hardcoded.
        # id of "name": "IS-Siminn-internet",   ----> "id": "5b706ec4-75f7-460d-a702-97dafeb522e3"
        test.pool_id = '5b706ec4-75f7-460d-a702-97dafeb522e3'

    def run(test):

        POOL_NAME = "IS-Siminn-internet"

        test.log.step('Step 1: Find last created subscription_id and iccid - Start')
        result, iccid_to_delete, subscription_id_to_delete = test.dut.dstl_get_last_created_subscription_id_and_iccid(test.rest_client, test.pool_id)
        if result is False:
            test.log.warning("Could not find iccid in order to delete, test will be aborted, Step 2 and 3 are not executed !!!")
        test.dut.dstl_collect_result('Step 1: Find last created subscription_id and iccid', result, test_abort = True)


        test.log.step('Step 2: Delete last created iccid - Start')
        result = test.dut.dstl_delete_subscription_only_on_mods(subscription_id_to_delete, iccid_to_delete)
        if result is False:
            test.log.warning("iccid could not be deleted, test will be aborted, Step 3 is not executed !!!")
        test.dut.dstl_collect_result('Step 2: Delete last created iccid', result, test_abort = True)


        test.log.step('Step 3: Create following iccid on MODS: ' + str(iccid_to_delete) + ' - Start')
        result, message_status = test.dut.dstl_create_single_subscription(test.rest_client, iccid_to_delete, test.pool_id)
        #result, message_status = test.dut.dstl_create_single_subscription(iccid_to_delete)
        test.dut.dstl_collect_result('Step 3: Create following iccid on MODS: ' + str(iccid_to_delete), result)


    def cleanup(test):

        test.dut.dstl_print_results()
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
