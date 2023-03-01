# responsible: johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-232 - REST API: assign provisioning rule/fallback rule to a device

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.miscellaneous.mods_e2e_unicorn_support import *
from dstl.identification import get_imei
from dstl.auxiliary.write_json_result_file import *
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel

testkey = "UNISIM01-232"


class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')

        test.dut.dstl_detect()
        test.mods_client = IotSuiteRESTClient()
        test.imei = test.dut.dstl_get_imei()

        test.log.step("0.1 Create device on MODS if it has not been created yet.")
        devices = test.mods_client.get_devices(to_json=True, log_level=LogLevel.QUIET)
        test.device_id = get_device_id(devices, test.imei)

        if test.device_id:
            test.log.info("Device exists on MODS")
        else:
            test.log.info("Create device")
            create_device_result, test.device_id = test.dut.dstl_create_device_on_mods(test.imei)
            test.expect(create_device_result, critical=True)

    def run(test):
        test.log.step("1. Create rules")
        fallback_rule_name = 'TEMP_FALLBACK'
        fallback_rule_type = 'static'
        fallback_rule_description = 'Fallback rule for test purposes'
        fallback_rule_preferred_operator = {'mcc': '', 'mnc': ''}
        fallback_rule_preferred_issuer = {'countryCode': '354', 'issuerCode': '01'}

        provision_rule_name = 'TEMP_PROVISIONING'
        provision_rule_type = 'static'
        provision_rule_description = 'Provisioning rule for test purposes'
        provision_rule_preferred_operator = {'mcc': '', 'mnc': ''}
        provision_rule_preferred_issuer = {'countryCode': '354', 'issuerCode': '01'}

        test.fallback_rule_id = test.get_rule_id(fallback_rule_name,
                                                 fallback_rule_type,
                                                 fallback_rule_description,
                                                 fallback_rule_preferred_operator,
                                                 fallback_rule_preferred_issuer)

        test.provision_rule_id = test.get_rule_id(provision_rule_name,
                                                  provision_rule_type,
                                                  provision_rule_description,
                                                  provision_rule_preferred_operator,
                                                  provision_rule_preferred_issuer)

        test.log.step("2. Assign fallback rule")
        assign_fallback_rule_resp = test.mods_client.assign_fallback_rule(test.device_id,
                                                                          fallback_rule_name,
                                                                          log_level=LogLevel.SPARE)
        test.expect(assign_fallback_rule_resp.status_code == 200)

        test.log.step("3. Assign provision rule")
        assign_fallback_rule_resp = test.mods_client.assign_provision_rule(test.device_id,
                                                                           provision_rule_name,
                                                                           log_level=LogLevel.SPARE)
        test.expect(assign_fallback_rule_resp.status_code == 200)

        test.check_connectivity_plan(fallback_rule_name, provision_rule_name)

        test.log.step('4. Assign non-existing provisioning rule')
        non_existing_rule = 'DOES_NOT_EXIST'

        assign_provision_rule_resp = test.mods_client.assign_provision_rule(test.device_id,
                                                                            non_existing_rule,
                                                                            log_level=LogLevel.SPARE)
        test.expect(assign_provision_rule_resp.status_code == 200)

        test.log.step('5. Assign non-existing fallback rule')
        assign_fallback_rule_resp = test.mods_client.assign_fallback_rule(test.device_id,
                                                                          non_existing_rule,
                                                                          log_level=LogLevel.SPARE)
        test.expect(assign_fallback_rule_resp.status_code == 200)

        test.check_connectivity_plan(expected_fallback=non_existing_rule,
                                     expected_provision=non_existing_rule)

        test.log.step('6. Assign empty provisioning rule')
        assign_provision_rule_resp = test.mods_client.assign_provision_rule(test.device_id,
                                                                            '',
                                                                            log_level=LogLevel.SPARE)
        test.expect(assign_provision_rule_resp.status_code == 404)

        test.log.step('7. Assign empty fallback rule')
        assign_fallback_rule_resp = test.mods_client.assign_fallback_rule(test.device_id,
                                                                          '',
                                                                          log_level=LogLevel.SPARE)
        test.expect(assign_fallback_rule_resp.status_code == 404)

    def get_rule_id(test, name, type, description, preferred_operator, preferred_issuer):
        create_rule_resp_body = test.mods_client.create_rule(name,
                                                             type,
                                                             description,
                                                             preferred_operator,
                                                             preferred_issuer,
                                                             to_json=True)

        if not create_rule_resp_body:
            rules = test.mods_client.get_rules(to_json=True, log_level=LogLevel.SPARE)
            rule = test.mods_client.find_rule(rules, name)
            return rule['id']
        else:
            return create_rule_resp_body['id']

    def check_connectivity_plan(test, expected_fallback, expected_provision):
        test.log.step("x1. Check device parameters")
        get_device_resp_body = test.mods_client.get_device_long(test.device_id, to_json=True)

        connectivity_plan = get_device_resp_body['shadow']['connectivityPlan']

        assigned_fallback_rule = connectivity_plan['fallbackProvisionRule']
        test.expect(assigned_fallback_rule == expected_fallback)

        assigned_provision_rule = connectivity_plan['initialProvisionRule']
        test.expect(assigned_provision_rule == expected_provision)

    def cleanup(test):
        test.log.step("y1. Delete fallback rule")
        test.mods_client.delete_rule(test.fallback_rule_id)

        test.log.step("y2. Delete provision rule")
        test.mods_client.delete_rule(test.provision_rule_id)

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
