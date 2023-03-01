# responsible: katrin.kubald@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-319

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.write_json_result_file import *
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
import json

testkey = "UNISIM01-319"


class Test(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        test.pool_name = "REST_API_TEST_POOLS"
        test.__check_existing_pool()

    def run(test):
        test.log.step("Get all pools")
        pools = test.rest_client.get_pools(to_json=True)
        test.expect(pools)

        test.log.step("Create pool")
        operator = {
            "countryCode": "354",
            "issuerCode": "01"
        }
        apn_name = "internet"
        authentication_type = "PAP"
        pdn_type = "IPv4"

        pool = test.rest_client.create_pool(test.pool_name,
                                            operator,
                                            apn_name,
                                            authentication_type,
                                            pdn_type,
                                            to_json=True
                                            )

        test.expect(pool)

        test.log.step("Error case: Create same pool again")
        same_pool = test.rest_client.create_pool(test.pool_name, operator, apn_name, authentication_type, pdn_type)
        test.expect(same_pool.status_code == 403)

        test.log.step("Update pool")
        pool = test.rest_client.update_pool(pool['id'], name=pool['name'], operator=operator,
                                            authentication_type=authentication_type, pdn_type=pdn_type,
                                            apn_name="Some other APN name", to_json=True)
        test.expect(pool)

        test.log.step("Get pool")
        pool = test.rest_client.get_pool(pool['id'], to_json=True)
        test.expect(pool)

        test.log.step("Delete pool")
        pool = test.rest_client.delete_pool(pool['id'])
        test.expect(pool)

    def __check_existing_pool(test):
        pools = test.rest_client.get_pools(to_json=True, log_level=LogLevel.QUIET)
        match = [pool for pool in pools if pool['name'] in test.pool_name]
        if len(match) > 0:
            test.log.info(f"Delete pool for test preparation.")
            pool_id = match[0]['id']
            delete_pool = test.rest_client.delete_pool(pool_id)
        else:
            test.log.info(f"OK, no pool with name {test.pool_name} found.")

    def cleanup(test):
        test.__check_existing_pool()
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
