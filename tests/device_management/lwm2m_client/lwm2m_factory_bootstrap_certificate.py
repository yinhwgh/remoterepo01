#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.lwm2m_constant import Lwm2mConstant
from dstl.internet_service import lwm2m_service
from dstl.network_service import register_to_network

import re
import time


class Lwm2mFactoryBootstrapCertificate(BaseTest):
    '''def __init__(test):
        super(BaseTest, test).__init__()'''


    def setup(test):
        test.server_param_file_path = r"C:\lwm2m\lwm2m_config_file\leshan_config_files\factory_cert" \
                                      r"\carrier_apn_cfg"
        test.global_param_file_path = r"C:\lwm2m\lwm2m_config_file\leshan_config_files\factory_cert" \
                                      r"\lwm2m_cfg"

        '''test.bootstrap_server_address = ""
        test.bootstrap_sec_mode = Lwm2mConstant.NON_SEC_MODE
        test.bootstrap_server_id = "100"'''

        test.stack_id_str = "MODS"
        test.server1_address = "coaps://10.170.47.251:15684"
        test.is_server1_bootstrap = False
        test.server1_sec_mode = Lwm2mConstant.CERTIFICATE_MODE
        test.server1_short_id = "105"

        test.server2_address = "coap://10.170.47.252:1101"
        test.is_server2_bootstrap = False
        test.server2_sec_mode = Lwm2mConstant.NON_SEC_MODE
        test.server2_short_id = "102"

        test.lifetime = 30
        test.default_pmin = 1
        test.default_pmax = 120
        test.disable_timeout = 86400
        test.notification_stored = True
        test.binding = "UQS"

    def run(test):
        test.log.info("1.Create and config the first lwm2m server")
        test.dut.dstl_register_to_network()
        test.create_application_object(test.stack_id_str, 0, test.server1_address, False,
                                       test.server1_sec_mode, test.server1_short_id, test.lifetime, test.default_pmin,
                                       test.default_pmax, test.disable_timeout, test.notification_stored, test.binding)
        test.config_server_param(test.stack_id_str, 0)
        test.write_param_from_file(test.stack_id_str, 0, test.server_param_file_path, test.global_param_file_path)

        '''test.log.info("2.Config available bootstrap server")
        test.expect(test.dut.dstl_lwm2m_add_server(test.stack_id_str, 0, test.bootstrap_server_address, True,
                                                   test.bootstrap_sec_mode, test.bootstrap_server_id, test.lifetime,
                                                   test.default_pmin, test.default_max, test.disable_timeout,
                                                   test.notification_stored, test.binding))'''

        # test.log.info("2.Start application and check the register status")
        # test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str))
        # time.sleep(60)
        # test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
        # # test.expect(test.dut.dstl_lwm2m_get_serv_conn_status(test.stack_id_str) == "deregistered")
        # test.expect(test.dut.dstl_lwm2m_get_serv_conn_status(test.stack_id_str, test.server1_short_id) == "registered")

        test.log.info("3.Config the second lwm2m server")
        test.expect(test.dut.dstl_lwm2m_add_server(test.stack_id_str, 1, test.server2_address,
                                                   test.is_server2_bootstrap, test.server2_sec_mode,
                                                   test.server2_short_id, test.lifetime, test.default_pmin,
                                                   test.default_pmax, test.disable_timeout,
                                                   test.notification_stored, test.binding))
        # test.config_server_param(test.stack_id_str, 1)
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 0, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 1, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 2, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 3, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 4, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 5, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 6, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 7, test.server2_short_id, 15))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 8, test.server2_short_id, 31))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 9, test.server2_short_id, 31))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 10, test.server2_short_id, 31))
        test.expect(test.dut.dstl_lwm2m_set_server_acl(test.stack_id_str, 11, test.server2_short_id, 31))
        #
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 0))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 1))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 2))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 3))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 4))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 5))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 6))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 7))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 8))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 9))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 10))
        # test.expect(test.dut.dstl_lwm2m_new_object_instance(test.stack_id_str, 2, 11))

        test.log.info("4.Restart application and check the register status of the two servers")
        test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str))
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))

        test.expect(test.dut.dstl_lwm2m_start_service(test.stack_id_str))
        time.sleep(60)
        test.expect(test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
        test.expect(test.dut.dstl_lwm2m_get_serv_conn_status(test.stack_id_str, test.server1_short_id) == 'registered')
        test.expect(test.dut.dstl_lwm2m_get_serv_conn_status(test.stack_id_str, test.server2_short_id) == 'registered')

        test.log.info("5.Stop application and delete the application")
        test.expect(test.dut.dstl_lwm2m_stop_service(test.stack_id_str))
        time.sleep(60)
        test.expect(not test.dut.dstl_lwm2m_is_application_running(test.stack_id_str))
        test.expect(test.dut.dstl_lwm2m_del_application(test.stack_id_str))

    def cleanup(test):
        pass

    def config_server_param(test, stack_id_str, server_instance_id):

        test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                   "APN_NAME", test.get_apn_v4()))
        test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                   "APN_CLASS", "2"))
        test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                   "BS_IF_REG_FAILS", "1"))
        test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
                                                                   "IP_FAMILY", "v4"))

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
        # f = open(server_param_file_path)
        # lines = f.readlines()
        # for line in lines:
        #     line = line.strip()
        #     ma = re.match(r'(\S+)=(\S+)', line)
        #     if ma:
        #         ext_param = ma.group(1)
        #         ext_value = ma.group(2)
        #         if ext_param in Lwm2mConstant.SEVER_EXT_PARAM_LIST:
        #             test.expect(test.dut.dstl_lwm2m_write_server_ext_parameter(stack_id_str, server_instance_id,
        #                                                                        ext_param, ext_value))

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

    def get_apn_v4(test):
        if test.dut.sim.gprs_apn:
            return test.dut.sim.gprs_apn
        elif test.dut.apn_v4:
            return test.dut.sim.apn.v4
        else:
            return ""


if __name__ == "__main__":
    unicorn.main()
