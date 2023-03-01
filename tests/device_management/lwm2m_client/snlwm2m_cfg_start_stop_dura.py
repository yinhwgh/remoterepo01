#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC
import unicorn

import re
import time

from core.basetest import BaseTest
from dstl.internet_service.lwm2m_constant import Lwm2mConstant

from dstl.internet_service import  lwm2m_service
from dstl.network_service import register_to_network


class Snlwm2mStartStopDura(BaseTest):
    '''global server_param_file_path
    global global_param_file_path
    global stack_id_str
    global server_instance_id
    global server_address
    global is_server_bootstrap
    global server_sec_mode
    global server_short_id
    global lifetime, default_pmin, default_pmax, disable_timeout, notification_stored, binding'''
    global loop

    def setup(test):
        test.carrier_apn_cfg_path = r"C:\Users\wenywu\Desktop\lwm2m_config_file\leshan_config_files\factory_nosec" \
                                      r"\carrier_apn_cfg"
        test.lwm2m_cfg_path = r"C:\Users\wenywu\Desktop\lwm2m_config_file\leshan_config_files\factory_nosec" \
                                      r"\lwm2m_cfg"
        test.stack_id_str = "Lwm2mStartStopDura"
        test.server_address = "coap://10.170.47.252:1001"
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
        test.loop = 1

    def run(test):
        test.create_application_object(test.stack_id_str, 0, test.server_address, test.is_server_bootstrap,
                                       test.server_sec_mode, test.server_short_id, test.lifetime, test.default_pmin,
                                       test.default_pmax, test.disable_timeout, test.notification_stored, test.binding)
        #test.write_param_from_file(test.stack_id_str, 0, test.server_param_file_path, test.global_param_file_path)

        # server_param_file_path = None
        # global_param_file_path = None
        # if test.carrier_apn_cfg_path:
        #     server_param_file_path = test.carrier_apn_cfg
        # if test.lwm2m_cfg_path:
        #     global_param_file_path = test.lwm2m_cfg_path

        #test.write_param_from_file(test.stack_id_str, 0, server_param_file_path, global_param_file_path)

        test.write_param_from_file(test.stack_id_str, 0, test.carrier_apn_cfg_path, test.lwm2m_cfg_path)

        test.dut.dstl_register_to_network()
        time.sleep(60)

        for i in range(0, test.loop):
            test.log.info("Loop " + str(i) + " start")
            if not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str):
                test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str))
            time.sleep(120)
            test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
            test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str))
            test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
            test.log.info("Loop " + str(i) + " end")
            time.sleep(120)

    def cleanup(test):
        test.log.info("Delete application " + test.stack_id_str)
        test.expect(test.dut.dstl_lwm2m_del_application(test.stack_id_str))
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
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 7, server_short_id, 10, 0, 15, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 8, server_short_id, 11, 0, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 9, server_short_id, 16, 0, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 10, server_short_id, 16, 1, 31, True))
        test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 11, server_short_id, 10308, 0, 31, True))

    def write_param_from_file(test, stack_id_str, server_instance_id, server_param_file_path, global_param_file_path):
        if server_param_file_path and server_param_file_path != "":
            f = open(server_param_file_path)
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                ma = re.match(r'(\S+)=(\S+)', line)
                if ma:
                    ext_param = ma.group(1)
                    ext_value = ma.group(2)
                    if ext_param in Lwm2mConstant.SEVER_EXT_PARAM_LIST:
                        test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                                   ext_param, ext_value))

        if global_param_file_path and global_param_file_path != "":
            f = open(global_param_file_path)
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                ma = re.match(r'(\S+)=(\S+)', line)
                if ma:
                    ext_param = ma.group(1)
                    ext_value = ma.group(2)
                    if ext_param in Lwm2mConstant.GLOBAL_EXT_PARAM_LIST:
                        test.expect(test.dut.dstl_lwm2m_write_global_ext_parameter(stack_id_str, ext_param, ext_value))


if __name__ == "__main__":
    unicorn.main()
