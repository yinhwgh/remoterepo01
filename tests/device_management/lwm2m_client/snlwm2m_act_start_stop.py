#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC0104345.001

import unicorn

import re
import time

from core.basetest import BaseTest
from dstl.internet_service.lwm2m_constant import Lwm2mConstant

from dstl.internet_service import  lwm2m_service
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Snlwm2mStartStop(BaseTest):
    '''global server_param_file_path
    global global_param_file_path
    global stack_id_str
    global server_instance_id
    global server_address
    global is_server_bootstrap
    global server_sec_mode
    global server_short_id
    global lifetime, default_pmin, default_pmax, disable_timeout, notification_stored, binding'''
    def setup(test):
        test.server_param_file_path = r"C:\lwm2m\lwm2m_config_file\leshan_config_files\factory_nosec" \
                                      r"\carrier_apn_cfg"
        test.global_param_file_path = r"C:\lwm2m\lwm2m_config_file\leshan_config_files\factory_nosec" \
                                      r"\lwm2m_cfg"
        test.stack_id_str = "MODS"
        test.server_address = "coap://10.170.47.252:1111"
        test.is_server_bootstrap = False
        test.server_sec_mode = 3

        test.server_short_id = 101
        test.server_instance_id = 0
        test.lifetime = 30
        test.default_pmin = 1
        test.default_pmax = 60
        test.disable_timeout = 86400
        test.notification_stored = True
        test.binding = "UQS"

    def run(test):
        test.log.info("1.Create and config application")
        test.create_application_object(test.stack_id_str, 0, test.server_address, False,
                                       test.server_sec_mode, test.server_short_id, test.lifetime, test.default_pmin,
                                       test.default_pmax, test.disable_timeout, test.notification_stored, test.binding)
        test.config_server_param(test.stack_id_str, 0, test.server_short_id)
        test.config_global_param(test.stack_id_str)
        # test.create_application_object(test.stack_id_str, 0, test.server_address, test.is_server_bootstrap,
        #                                test.server_sec_mode, test.server_short_id, test.lifetime, test.default_pmin,
        #                                test.default_pmax, test.disable_timeout, test.notification_stored, test.binding)
        # test.write_param_from_file(test.stack_id_str, 0, test.server_param_file_path, test.global_param_file_path)

        test.log.info("2.Set to auto start")
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str, "on"))
        test.expect(test.dut.dstl_lwm2m_is_application_autostart(test.stack_id_str))

        test.log.info("3.Restart module and check the running status of the applications")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))

        test.log.info("4.Try to start the application again")
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str))

        test.log.info("5.turn off auto start")
        test.expect(test.dut.dstl_lwm2m_set_autostart(test.stack_id_str, "off"))
        test.expect(not test.dut.dstl_lwm2m_is_application_autostart(test.stack_id_str))

        test.log.info("6.Restart module and check the running status of the applications")
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))

        test.log.info("7.Start the application manually")
        test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))

        test.log.info("8.Try to start the application again")
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str))

        test.log.info("9. Stop the application")
        test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str))
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))

        test.log.info("10. Stop the application again")
        test.expect(not test.dut.dstl_lwm2m_stop_service(test.stack_id_str))

        test.log.info("11. Delete the application")
        test.expect(test.dut.dstl_lwm2m_del_application(test.stack_id_str))

        test.log.info("12. Try to start/stop the non-exsited application")
        test.expect(not test.dut.dstl_lwm2m_start_service(test.stack_id_str))
        test.expect(not test.dut.dstl_lwm2m_stop_service(test.stack_id_str))

    def cleanup(test):
        pass

    def create_application_object(test, stack_id_str, server_instance_id, server_address, is_server_bootstrap,
                                  server_sec_mode, server_short_id, lifetime, default_min, default_max,
                                  disable_timeout, notification_stored, binding):
        test.expect(test.dut.dstl_lwm2m_add_server(stack_id_str, server_instance_id, server_address,
                                                   is_server_bootstrap, server_sec_mode, server_short_id, lifetime,
                                                   default_min, default_max, disable_timeout, notification_stored,
                                                   binding))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 0, server_short_id, 1, 1, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 1, server_short_id, 1, 2, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 2, server_short_id, 3, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 3, server_short_id, 4, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 4, server_short_id, 5, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 5, server_short_id, 6, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 6, server_short_id, 7, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 7, server_short_id, 10, 0, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 8, server_short_id, 11, 0, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 9, server_short_id, 16, 0, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 10, server_short_id, 16, 1, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 11, server_short_id, 10308, 0, 31, True))

    def write_param_from_file(test, stack_id_str, server_instance_id, server_param_file_path, global_param_file_path):
        f = open(server_param_file_path)
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            ma = re.match( r'(\S+)=(\S+)',line)
            if ma:
                ext_param = ma.group(1)
                ext_value = ma.group(2)
                if ext_param in Lwm2mConstant.SEVER_EXT_PARAM_LIST:
                    test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                               ext_param, ext_value))

        f = open(global_param_file_path)
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            ma = re.match(r'(\S+)=(\S+)',line)
            if ma:
                ext_param = ma.group(1)
                ext_value = ma.group(2)
                if ext_param in Lwm2mConstant.GLOBAL_EXT_PARAM_LIST:
                    test.expect(test.dut.dstl_lwm2m_write_global_ext_parameter(stack_id_str, ext_param, ext_value))


if __name__ == "__main__":
    unicorn.main()
