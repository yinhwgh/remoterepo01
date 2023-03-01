# responsible: karsten.labuske@thalesgroup.com
# location: Berlin
# test case: UNISIM01-375

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *

import json

testkey = "UNISIM01-375"


class Test(BaseTest):
    """
    Class to read available SM-DP+ servers
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

    def run(test):

        r = test.rest_client.get_smdp_servers()
        test.expect(r, critical=True)
        servers = r.json()
        test.expect(servers, critical=True)
        test.log.info("Cinterion IoT Suite SM-DP+ servers:\n " + json.dumps(servers, indent=4, sort_keys=True))


    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
