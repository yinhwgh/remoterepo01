# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-97

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *

testkey = "UNISIM01-97"


class Test(BaseTest):
    """
    Class to test some of the CRUD operations of the apnProfiles endpoint of the MODS REST API.
    Tested operations: create, read, delete
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

    def run(test):
        profile_name = "Test"
        pdn_type = "IPv4v6"
        apn = "test"
        user_name = "Who"
        authentication_type = "NONE"
        secret = ""

        test.log.info(f'{40 * "*"} Delete APN profile if it exists {40 * "*"}')
        apn_profiles = test.rest_client.get_apn_profiles(to_json=True)
        apn_profile_id = test.rest_client.find_apn_profile_id(apn_profiles, profile_name)

        if not apn_profile_id:
            test.log.info("APN profile with ProfileName Test will be created later")
        else:
            response = test.rest_client.delete_apn_profile(apn_profile_id, to_json=True)
            test.expect(response)
            test.expect(profile_name == response['profileName'])

        test.log.info(f'{40 * "*"} Create APN Profile {40 * "*"}')
        response = test.rest_client.create_apn_profile(profile_name, apn, authentication_type, user_name, secret,
                                                       pdn_type, to_json=True)
        test.expect(response)
        test.expect(profile_name == response['profileName'])

        test.log.info(f'{40 * "*"} Create an existing APN Profile {40 * "*"}')
        response = test.rest_client.create_apn_profile(profile_name, apn, authentication_type, user_name, secret,
                                                       pdn_type, to_json=True)
        test.expect(response.status_code == 403)
        test.expect('APN profile name already exists' == response.json()['message'])

        test.log.info(f'{40 * "*"} Get all APN Profiles {40 * "*"}')
        apn_profiles = test.rest_client.get_apn_profiles(to_json=True)
        test.expect(apn_profiles)

        apn_profile_id = test.rest_client.find_apn_profile_id(apn_profiles, profile_name)
        test.log.info(f'ID for profile name {user_name}: {apn_profile_id}')

        test.log.info(f'{40 * "*"} Get single APN Profile {40 * "*"}')
        response = test.rest_client.get_apn_profile(apn_profile_id, to_json=True)
        test.expect(response)
        test.expect(profile_name == response['profileName'])

        test.log.info(f'{40 * "*"} Delete APN Profile {40 * "*"}')
        response = test.rest_client.delete_apn_profile(apn_profile_id, to_json=True)
        test.expect(response)
        test.expect(profile_name == response['profileName'])

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)

        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
