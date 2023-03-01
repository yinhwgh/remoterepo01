# responsible: johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-346

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *

import json

testkey = "UNISIM01-346"


class Test(BaseTest):
    """
    Class to test some of the CRUD operations of the device group endpoint of the MODS REST API.
    Tested operations: create, read, update, delete
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()
        test.group_name = "CRUD_TEST_DEVICEGROUP"

    def run(test):
        # read all device groups
        test.log.info(f'{40 * "*"} Read all device groups {40 * "*"}')
        device_groups = test.rest_client.get_device_groups(test, True)
        test.expect(device_groups)
        test.log.info("Found " + str(len(device_groups)) + " device_groups:\n" + json.dumps(device_groups, indent=4,
                                                                                            sort_keys=True))
        test.expect(len(device_groups) > 0)

        test.log.info(f'{40 * "*"} create new device group {40 * "*"}')
        test.log.info("New devicegroup : " + test.group_name)
        device_group = test.rest_client.create_device_group(test.group_name, description="Temporary group for API Test",
                                                            to_json=True)
        test.expect(device_group)

        test.log.info(f'{40 * "*"} update device group description {40 * "*"}')
        description_update = "This is another description for device group"
        updated_device_group = test.rest_client.update_device_group(device_group['id'], test.group_name,
                                                                    description_update,
                                                                    to_json=True)
        test.expect(updated_device_group)
        if updated_device_group:
            test.expect(updated_device_group['description'] == description_update)
        else:
            test.expect(False, msg="Device group has not been updated")

        test.log.info(f'{40 * "*"} update device group name {40 * "*"}')
        name_update = test.group_name + "_UPDATED"
        updated_device_group = test.rest_client.update_device_group(device_group['id'], name_update,
                                                                    device_group['description'],
                                                                    to_json=True)
        test.expect(updated_device_group)
        if updated_device_group:
            test.expect(updated_device_group['name'] == name_update)
        else:
            test.expect(False, msg="Device group name has not been updated")

        test.log.info(f'{40 * "*"} add member to device group {40 * "*"}')
        created_device = test.rest_client.create_device("12345678901235", label="DUMMY FOR TEST", to_json=True)
        if created_device:
            test.expect(device_group['size'] == 0)
            member = test.rest_client.add_device_group_member(device_group['id'], created_device['id'],
                                                              to_json=True)
            test.expect(member)

            device_group = test.rest_client.get_device_group(device_group['id'], True)
            test.expect(device_group['size'] == 1)

            test.log.info(f'{40 * "*"} remove member from device group {40 * "*"}')
            delete_member = test.rest_client.delete_device_group_member(device_group['id'], member['id'])
            #test.expect(delete_member.status_code == 200)

            test.rest_client.delete_device(created_device['id'], to_json=True)
        else:
            test.expect(False, msg="Could not create device")

        test.log.info(f'{40 * "*"} remove device group {40 * "*"}')
        delete_device_group = test.rest_client.delete_device_group(device_group['id'], to_json=True)
        test.expect(delete_device_group)

    def cleanup(test):
        test.log.info("404 is expected here")
        device = test.rest_client.get_device_with_imei(12345678901235, True)
        if device:
            test.rest_client.delete_device(device['id'])
        device_groups = test.rest_client.get_device_groups(True)
        if device_groups:
            test_group = [group for group in device_groups if group['name'] == test.group_name]
            if len(test_group) == 1:
                test.log.info(test_group[0]['id'])
                test.rest_client.delete_device_group(test_group[0]['id'])

        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
