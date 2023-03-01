#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC
import unicorn

from core.basetest import BaseTest
from dstl.internet_service.lwm2m_constant import Lwm2mConstant

import re
import time


class Snlwm2mColl(BaseTest):
    '''global server_param_file_path
    global global_param_file_path
    global stack_id_str1, stack_id_str2
    global server1_address, server2_address
    global is_server1_bootstrap, is_server2_bootstrap
    global server1_sec_mode, server2_sec_mode
    global server1_short_id, server2_short_id
    global lifetime, default_pmin, default_pmax, disable_timeout, notification_stored, binding'''

    def __init__(test):
        super(BaseTest, test).__init__()
        test.server_param_file_path = ""
        test.global_param_file_path = ""

        test.stack_id_str1 = ""
        test.server1_address = ""
        test.is_server1_bootstrap = False
        test.server1_sec_mode = Lwm2mConstant.NON_SEC_MODE
        test.server1_short_id = ""

        test.stack_id_str2 = ""
        test.server2_address = ""
        test.is_server2_bootstrap = False
        test.server2_sec_mode = Lwm2mConstant.PSK_MODE
        test.server2_short_id = ""

        test.lifetime = 30
        test.default_pmin = 1
        test.default_pmax = 60
        test.disable_timeout = 86400
        test.notification_stored = True
        test.binding = "UQS"

    def setup(test):
        pass

    def run(test):
        test.log.info("1.Create and config the first application")
        test.create_application_object(test.stack_id_str1, 0, test.server1_address, test.is_server1_bootstrap,
                                       test.server1_sec_mode, test.server1_short_id, test.lifetime, test.default_pmin,
                                       test.default_max, test.disable_timeout, test.notification_stored, test.binding)
        test.write_param_from_file(test.stack_id_str1, 0, test.server_param_file_path, test.global_param_file_path)

        test.log.info("2.Create and config the second application")
        test.create_application_object(test.stack_id_str2, 0, test.server2_address, test.is_server2_bootstrap,
                                       test.server2_sec_mode, test.server2_short_id, test.lifetime, test.default_pmin,
                                       test.default_max, test.disable_timeout, test.notification_stored, test.binding)
        test.write_param_from_file(test.stack_id_str2, 0, test.server_param_file_path, test.global_param_file_path)

        test.log.info("3.Set the first application to auto start")
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str1, True))
        test.expect(test.dut.dstl_lwm2m_is_autostart(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_is_autostart(test.stack_id_str2))

        test.log.info("4.Restart module and check the running status of the two applications")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))

        test.log.info("5.Set the second application to auto start")
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str2, True))
        test.expect(test.dut.dstl_lwm2m_is_autostart(test.stack_id_str2))
        test.expect(not test.dut.dstl_lwm2m_is_autostart(test.stack_id_str1))

        test.log.info("6.Restart module and check the running status of the two applications")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))

        test.log.info("7.Set both the application not to auto start")
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str1, False))
        test.expect(not test.dut.dstl_lwm2m_is_autostart(test.stack_id_str1))
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str2, False))
        test.expect(not test.dut.dstl_lwm2m_is_autostart(test.stack_id_str2))

        test.log.info("8.Restart module and check the running status of the two applications")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))

        test.log.info("9.Start the first application manually")
        test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str1))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))

        test.log.info("10.Try to start the second application while the first one running")
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str2))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))

        test.log.info("11. Stop the first one and start the second one")
        test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str1))
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str2))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))

        test.log.info("12. Stop the second one and start the first one")
        test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str2))
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str2))
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str1))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))

        test.log.info("13. Modify server configuration and ext param while application running")
        test.expect(test.dut.dstl_lwm2m_modify_server_address(test.stack_id_str1, 0, test.server2_address,
                                                              test.is_bootstrap, test.server2_sec_mode))
        test.expect(test.dut.dstl_get_server_address(test.stack_id_str1, 0) == test.server2_address)

        test.log.info("14. Restart module and check the configuration and param")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(test.dut.dstl_get_server_address(test.stack_id_str1, 0) == test.server2_address)

        test.log.info("15. Start the first application")
        test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str1))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str1))

        test.log.info("16. Delete the applications during application running")
        test.expect(test.dut.dstl_del_application(test.stack_id_str1))
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
        test.expect(test.dut.dstl_del_application(test.stack_id_str2))

        test.log.info("17. Restart module and check if the application deleted")
        test.dut.dstl_restart()
        time.sleep(60)
        app_list = test.dut.at1.dstl_lwm2m_read_application()
        if test.stack_id_str1 in app_list:
            test.log.error("Application " + test.stack_id_str1 + " not deleted")
        if test.stack_id_str2 in app_list:
            test.log.error("Application " + test.stack_id_str2 + " not deleted")

    def cleanup(test):
        pass

    def create_application_object(test, stack_id_str, server_instance_id, server_address, is_server_bootstrap,
                                  server_sec_mode, server_short_id, lifetime, default_min, default_max,
                                  disable_timeout, notification_stored, binding):
        test.expect(test.dut.dstl_lwm2m_add_server(stack_id_str, server_instance_id, server_address,
                                                   is_server_bootstrap, server_sec_mode, server_short_id, lifetime,
                                                   default_min, default_max, disable_timeout, notification_stored,
                                                   binding))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 0, server_short_id, 1, 1, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 1, server_short_id, 1, 2, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 2, server_short_id, 3, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 3, server_short_id, 4, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 4, server_short_id, 5, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 5, server_short_id, 6, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 6, server_short_id, 7, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 7, server_short_id, 10, 0, 15, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 8, server_short_id, 11, 0, 31, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 9, server_short_id, 16, 0, 31, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 10, server_short_id, 16, 1, 31, True))
        test.expect(test.dut.dstl_create_acl_obj(stack_id_str, 11, server_short_id, 10308, 0, 31, True))

    def write_param_from_file(test, stack_id_str, server_instance_id, server_param_file_path, global_param_file_path):
        f = open(server_param_file_path)
        lines = f.readlines()
        for line in lines:
            ma = re.match(line, r'(\S+)=(\S+)')
            if ma:
                ext_param = ma.group(1)
                ext_value = ma.group(2)
                if ext_param in Lwm2mConstant.SEVER_EXT_PARAM_LIST:
                    test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                               ext_param, ext_value))

        f = open(global_param_file_path)
        lines = f.readlines()
        for line in lines:
            ma = re.match(line, r'(\S+)=(\S+)')
            if ma:
                ext_param = ma.group(1)
                ext_value = ma.group(2)
                if ext_param in Lwm2mConstant.SEVER_EXT_PARAM_LIST:
                    test.expect(test.dut.dstl_lwm2m_write_global_ext_parameter(stack_id_str, server_instance_id,
                                                                               ext_param, ext_value))


if __name__ == "__main__":
        unicorn.main()
