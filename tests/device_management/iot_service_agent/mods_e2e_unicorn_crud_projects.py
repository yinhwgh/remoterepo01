# responsible: katrin.kubald@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin
# test case: UNISIM01-317

import unicorn
from core.basetest import BaseTest
from dstl.miscellaneous.iot_suite_rest_client import IotSuiteRESTClient, LogLevel
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary.write_json_result_file import *

import json

testkey = "UNISIM01-317"


class Test(BaseTest):
    """
    Class to test some of the CRUD operations of the project endpoint of the MODS REST API.
    Tested operations: create, read, update, delete
    """

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - Start *****')
        test.rest_client = IotSuiteRESTClient()

        test.project_name = "REST_API_TEST_PROJECT"
        test.devicegroup = "REST_API_TEST_DEVICEGROUP"
        test.group_name = "CRUD_TEST_PROJECT_DEVICEGROUP"
        test.factory_assignment_pool_name = test.get('iot_suite_factory_assignment_pool')
        test.factory_assignment_pool_id, _ = test.rest_client.find_pool_by_name(test.factory_assignment_pool_name)

        test.__check_existing_project()

    def run(test):
        # read all projects
        test.log.info(f'{40 * "*"} Read all projects {40 * "*"}')
        projects = test.rest_client.get_projects(test, True)
        test.expect(projects)
        test.log.info("Found " + str(len(projects)) + " projects:\n" + json.dumps(projects, indent=4, sort_keys=True))
        test.expect(len(projects) > 0)
        existing_devicegroup = projects[0]['deviceGroupId']
        factory_assignment = projects[0]['factoryAssignment'][0]['pools'][0]['id']

        test.log.info(f'{40 * "*"} create new project with new devicegroup {40 * "*"}')
        test.log.info("New devicegroup : " + test.devicegroup)
        project = test.rest_client.create_project(test.project_name, {"name": test.devicegroup}, True)
        test.expect(project)

        test.log.info(f'{40 * "*"} read new project {40 * "*"}')
        project = test.rest_client.get_project(project['id'], True)
        test.expect(project)

        test.log.info(f'{40 * "*"} update new project (set factory assignment) {40 * "*"}')
        test.log.info('Factory Assignment: ' + factory_assignment)
        project = test.rest_client.update_project(project['id'],
                                                  project['name'],
                                                  project['deviceGroupId'],
                                                  to_json=True,
                                                  log_level=LogLevel.FULL,
                                                  factoryAssignment=[{"type": "SINGLE", "pools": [
                                                      {"id": test.factory_assignment_pool_id}]}])

        test.expect(project)
        test.log.info(f'{40 * "*"} read new project {40 * "*"}')
        project = test.rest_client.get_project(project['id'], True)
        test.expect(project)

        test.log.info(f'{40 * "*"} try to create again {40 * "*"}')
        project_err = test.rest_client.create_project(test.project_name, {"name": project['deviceGroupId']}, True)
        test.expect(project_err.status_code == 403)
        test.expect('Project name already exists' == project_err.json()['message'])

        test.log.info(f'{40 * "*"} delete new project {40 * "*"}')
        project = test.rest_client.delete_project(project['id'], True)
        test.expect(project)

        test.log.info(f'{40 * "*"} create new project with existing devicegroup {40 * "*"}')
        test.log.info("Existing devicegroup id: " + existing_devicegroup)
        dgr_name = test.rest_client.get_device_group(id=existing_devicegroup, to_json=True, log_level=LogLevel.QUIET)
        test.expect(dgr_name)
        test.log.info("Existing devicegroup name: " + dgr_name['name'])
        project = test.rest_client.create_project(test.project_name, {"id": existing_devicegroup}, True)
        test.expect(project)

        test.log.info("New devicegroup : " + test.group_name)
        device_group = test.rest_client.create_device_group(test.group_name, description="Temporary group for API Test",
                                                            to_json=True)
        test.expect(device_group)

        test.log.info(f'{40 * "*"} update project: set new device group {40 * "*"}')
        project = test.rest_client.update_project(project['id'],
                                                  project['name'],
                                                  device_group['id'],
                                                  to_json=True,
                                                  log_level=LogLevel.FULL)

        test.expect(project)

        test.log.info(f'{40 * "*"} read new project {40 * "*"}')
        project = test.rest_client.get_project(project['id'], True)
        test.expect(project)

        dgr_name = test.rest_client.get_device_group(project['deviceGroupId'], to_json=True, log_level=LogLevel.QUIET)
        test.expect(dgr_name)
        test.log.info("Updated devicegroup name: " + dgr_name['name'])

        test.log.info(f'{40 * "*"} delete new project {40 * "*"}')
        project = test.rest_client.delete_project(project['id'], True)
        test.expect(project)

        test.log.info(f'{40 * "*"} remove device group {40 * "*"}')
        delete_device_group = test.rest_client.delete_device_group(device_group['id'], to_json=True)
        test.expect(delete_device_group)

    def __check_existing_project(test):
        projects = test.rest_client.get_projects(to_json=True, log_level=LogLevel.QUIET)
        match = [prj for prj in projects if prj['name'] in test.project_name]
        test.log.info(match)
        if len(match) > 0:
            test.log.info(f"Delete project for test preparation.")
            prj_id = match[0]['id']
            delete_prj = test.rest_client.delete_project(prj_id)
        else:
            test.log.info(f"OK, no project with name {test.project_name} found.")

    def cleanup(test):
        test.__check_existing_project()
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        testkey, str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + testkey + ') - End *****')


if "__main__" == __name__:
    unicorn.main()
