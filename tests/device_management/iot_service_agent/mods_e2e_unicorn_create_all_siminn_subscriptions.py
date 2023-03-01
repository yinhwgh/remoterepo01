# responsible: katrin.kubald@thalesgroup.com, baris.kildi@thalesgroup.com
# location: Berlin
# test case: UNISIM01-236

import unicorn
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from core.basetest import BaseTest
from dstl.auxiliary.write_json_result_file import *

testkey = "UNISIM01-236"

class Test(BaseTest):
    """
    Create all subscriptions from SIMINN-list on MODS-server
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()
        # TEMPORARY solution. Should not be hardcoded.
        # id of "name": "IS-Siminn-internet",   ----> "id": "5b706ec4-75f7-460d-a702-97dafeb522e3"
        #test.pool_id = '5b706ec4-75f7-460d-a702-97dafeb522e3'

        test.pool_name = "IS-Siminn-internet"
        test.pool_id, pool = test.rest_client.find_pool_by_name(test.pool_name)
        test.log.info('Pool_name: ' + test.pool_name + ' -> Pool_id: ' + test.pool_id)



    def run(test):

        iccid_list = []

        file_name_iccids = "iccids_siminn_gcp.txt"
        base_path, _ = os.path.split(test.test_file)
        file_path = os.path.join(base_path, f'{file_name_iccids}')

        result, iccid_list = test.dut.dstl_get_all_iccids_from_file(file_path)

        if result is False:
            dstl.log.error("ICCID file: " + file_name_iccids + " could not be found - test abort")

        test.expect(result, critical=True)

        result1, iccid_results_list = test.dut.dstl_create_all_subscriptions_with_pool_id(test.rest_client, iccid_list, test.pool_id)
        #result1, iccid_results_list = test.dut.dstl_create_all_subscriptions(iccid_list)

        test.log.com(' ')
        test.log.com('****************************')
        test.log.com('Results: ')
        test.log.com('ICCID:                  created:   message: ')
        for i in range(len(iccid_results_list)):
            test.log.com(str(iccid_results_list[i][0]) + '  -  ' + str(iccid_results_list[i][1]) + '  -  ' +
                         iccid_results_list[i][2])
        test.log.com('****************************')

        # delete test result list
        del iccid_results_list[:]

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
