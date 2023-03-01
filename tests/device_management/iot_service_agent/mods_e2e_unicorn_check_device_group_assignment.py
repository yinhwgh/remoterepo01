# responsible: johann.suhr@thalesgroup.com
# location: Berlin

import unicorn
from core.basetest import BaseTest
from dstl.identification import get_imei
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
from dstl.miscellaneous.mods_e2e_unicorn_support import *


class Test(BaseTest):
    def setup(test):
        test.rest_client = IotSuiteRESTClient()
        test.project_name = 'UNICORN-POC'
        test.device_group_name = test.get('iot_suite_group_name')
        test.factory_assignment_pool_name = test.get('iot_suite_factory_assignment_pool')
        test.field_assignment_pool_name = test.get('iot_suite_field_assignment_pool')
        test.imei = test.dut.dstl_get_imei()

    def run(test):
        project_id, _ = test.rest_client.find_project_by_name(test.project_name)
        device_group_id, _ = test.rest_client.find_device_group_by_name(test.device_group_name)
        device_created, device_id = test.dut.dstl_create_device_on_mods(test.rest_client, test.imei,
                                                                        group_id=device_group_id)
        test.expect(device_created, critical=True)

        group_ids = test.dut.dstl_get_device_group_ids_of_device(test.rest_client, device_id)
        test.log.info(group_ids)
        test.expect(group_ids, critical=True)

        group_id_in_project = test.dut.dstl_device_group_in_project(test.rest_client, group_ids[0], project_id)
        test.log.info(group_id_in_project)
        test.expect(group_id_in_project)

    def cleanup(test):
        device = test.rest_client.get_device_with_imei(test.imei, to_json=True)
        if device:
            device_deleted = test.rest_client.delete_device(device['id'], to_json=True)
            test.expect(device_deleted)


if "__main__" == __name__:
    unicorn.main()
