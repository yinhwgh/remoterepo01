# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-98

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *

import json

testkey = "UNISIM01-98"


class Test(BaseTest):
    """
    Class to test some of the CRUD operations of the devices endpoint of the MODS REST API.
    Tested operations: create, read, delete
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

    def run(test):
        # Device attributes needed to create a new device.
        imei = "004401083712345"
        test.log.info("This is your IMEI: " + imei)
        label = "eSim_TEST"

        test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        device = test.rest_client.get_device_with_imei(imei, to_json=True)
        if not device:
            test.log.info("Device with imei 004401083712345 will be created")
        else:
            test.rest_client.delete_device(device['id'], to_json=True)

        test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        response = test.rest_client.create_device(imei, label)
        test.expect(response.status_code == 200)

        test.log.info(f'{40 * "*"} Create already an existing Device {40 * "*"}')
        response = test.rest_client.create_device(imei, label)
        test.expect('Device imei already exists' in response.json()['message'])

        test.log.info(f'{40 * "*"} Get all Devices {40 * "*"}')
        devices = test.rest_client.get_devices(to_json=True)
        test.expect(devices)

        test.log.info(f'{40 * "*"} Get single Device {40 * "*"}')
        device = test.rest_client.get_device_with_imei(imei, to_json=True)
        device_id = device['id']
        device_obj = test.rest_client.get_device(device_id, to_json=True)
        test.expect(imei == device_obj['imei'])

        test.log.info(f'{40 * "*"} Delete Device {40 * "*"}')
        deleted_device_obj = test.rest_client.delete_device(device_id, to_json=True)
        test.expect(deleted_device_obj)

        test.log.info(f'{40 * "*"} Delete not existing Device {40 * "*"}')
        deleted_device_obj = test.rest_client.delete_device(device_id)
        test.expect(not deleted_device_obj)
        test.expect('Device not found' in deleted_device_obj.json()['message'])

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')
        pass


if "__main__" == __name__:
    unicorn.main()
