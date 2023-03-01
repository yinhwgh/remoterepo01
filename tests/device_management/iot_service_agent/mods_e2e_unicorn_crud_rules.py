# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-99

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *
import json

testkey = "UNISIM01-99"


class Test(BaseTest):
    """
    Class to test some of the CRUD operations of the rules endpoint of the MODS REST API.
    Tested operations: create, read, delete
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

    def run(test):
        # Rule attributes needed to create a rule.
        rule_type = "static"
        rule_status = "created"
        rule_after_delete = "Provisioning rule not found"
        rule_name = "TEST"
        rule_description = "A TEST rule"
        rule_preferred_operator = {
            "mcc": "",
            "mnc": ""
        }
        rule_preferred_issuer = {
            "countryCode": "882",
            "issuerCode": "28"
        }

        test.log.info(f'{40 * "*"} Create Rule {40 * "*"}')
        response = test.rest_client.create_rule(rule_name, rule_type, rule_description, rule_preferred_operator,
                                                rule_preferred_issuer, to_json=True)
        if response:
            test.expect(rule_status == response['status'])
        else:
            test.log.info("Rule already exist ...")

        test.log.info(f'{40 * "*"} Create existing Rule {40 * "*"}')
        response = test.rest_client.create_rule(rule_name, rule_type, rule_description, rule_preferred_operator,
                                                rule_preferred_issuer)
        body = response.json()
        test.expect('Provisioning rule name already exists' == body['message'])

        test.log.info(f'{40 * "*"} Get all Rules {40 * "*"}')
        rules = test.rest_client.get_rules(to_json=True)
        test.expect(rules)

        test.log.info(f'{40 * "*"} Get single Rule {40 * "*"}')
        rules = test.rest_client.get_rules(to_json=True)
        rule_id = test.get_rule_id(rules, rule_name)
        rule_obj = test.rest_client.get_rule(rule_id, to_json=True)
        test.expect(rule_name == rule_obj['name'])

        test.log.info(f'{40 * "*"} Delete Rule {40 * "*"}')
        delete_rule_response = test.rest_client.delete_rule(rule_id, to_json=True)
        test.expect(delete_rule_response)

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass

    def get_rule_id(test, rules, rule_name):
        try:
            return [rule['id'] for rule in rules if rule['name'] == rule_name][0]
        except:
            test.log.error(f'No rule found with name {rule_name}')
            test.expect(False, critical=True)


if "__main__" == __name__:
    unicorn.main()
