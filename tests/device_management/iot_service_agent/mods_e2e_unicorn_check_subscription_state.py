# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-96

import unicorn
import json
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.identification import get_imei
from dstl.auxiliary.write_json_result_file import *
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel

testkey = "UNISIM01-96"


class Test(BaseTest):
    """
    Test if a specific subscription is activated and check the status of the belonging job.
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

    def run(test):
        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = test.rest_client.get_subscriptions(to_json=True)
        test.expect(subscriptions)

        test.log.info(f'{40 * "*"} Get single Subscription {40 * "*"}')
        try:
            first_subscription_with_imei = [subscription for subscription
                                            in subscriptions
                                            if 'imei' in subscription][0]
        except:
            test.log.error("No subscription with imei found")
            test.expect(False)
            return
        imei = first_subscription_with_imei['imei']
        test.log.info(f"IMEI: {imei}")

        subscription_id = first_subscription_with_imei['id']
        test.log.info(f"ID: {subscription_id}")

        subscription = test.rest_client.get_subscription(subscription_id, to_json=True)
        test.expect(subscription)

        test.log.info(f'{40 * "*"} Check Subscription state by imei {40 * "*"}')
        subscription_state = subscription['status']
        test.log.info(f'Subscription state: {subscription_state}')

        test.log.info(f'{40 * "*"} Check belonging Job state {40 * "*"}')
        if "jobId" in subscription:
            jobId = subscription['jobId']
            job = test.rest_client.get_job(jobId, to_json=True)
            test.expect(job)
            test.log.info(f'Job state: {job["status"]}')

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
