#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC0104341.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.lwm2m_constant import Lwm2mConstant


from dstl.internet_service import  lwm2m_service
from dstl.auxiliary import restart_module


class Snlwm2mCfgAppObj(BaseTest):
    def setup(test):
        pass
        # test.expect(test.dut.restart())

    def run(test):
        server1_address = "coap://10.170.47.253:1101"
        is_server1_bootstrap = False
        server1_sec_mode = Lwm2mConstant.NON_SEC_MODE
        server1_short_id = "101"

        server2_address = "coap://10.170.47.253:1111"
        is_server2_bootstrap = False
        server2_sec_mode = Lwm2mConstant.NON_SEC_MODE
        server2_short_id = "102"

        lifetime = 30
        default_pmin = 1
        default_pmax = 60
        disable_timeout = 86400
        notification_stored = True
        binding = "UQS"

        test.log.info("1.Write resources with non-existed stack_id_str")
        stack_id_str = "stack_id_test1"
        app_list = test.dut.dstl_lwm2m_read_application()

        if stack_id_str in app_list:
            test.log.error("The stack_id_str is already existed, please check the enviornment")
        else:
            test.expect(test.dut.dstl_lwm2m_add_server_instance_to_mem(stack_id_str, 0, server1_address,
                                                                       is_server1_bootstrap, server1_sec_mode,
                                                                       server1_short_id, lifetime, default_pmin,
                                                                       default_pmax, disable_timeout,
                                                                       notification_stored, binding))
            test.dut.dstl_restart()
            app_list = test.dut.dstl_lwm2m_read_application()
            if stack_id_str in app_list:
                test.log.error("Server object just created in memory, shouldn't restore automatically")
            else:
                test.expect(test.dut.dstl_lwm2m_add_server_instance_to_mem(stack_id_str, 0, server1_address,
                                                                           is_server1_bootstrap, server1_sec_mode,
                                                                           server1_short_id, lifetime, default_pmin,
                                                                           default_pmax, disable_timeout,
                                                                           notification_stored, binding))
                test.expect(test.dut.dstl_lwm2m_add_server_instance_to_mem(stack_id_str, 1, server2_address,
                                                                           is_server1_bootstrap, server2_sec_mode,
                                                                           server2_short_id, lifetime, default_pmin,
                                                                           default_pmax, disable_timeout,
                                                                           notification_stored, binding))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 0))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 0, 0))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 0, 1))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 1))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 1, 0))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 1, 1))

                test.expect(test.dut.dstl_lwm2m_store_sever_instance(stack_id_str, 0))
                test.expect(test.dut.dstl_lwm2m_store_sever_instance(stack_id_str, 1))

                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 0, server1_short_id, 1, 1, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 1, server1_short_id, 1, 2, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 2, server1_short_id, 3, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 3, server1_short_id, 4, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 4, server1_short_id, 5, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 5, server1_short_id, 6, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 6, server1_short_id, 7, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 7, server1_short_id, 10, 0, 15, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 8, server1_short_id, 11, 0, 31, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 9, server1_short_id, 16, 0, 31, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 10, server1_short_id, 16, 1, 31, True))
                test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str, 11, server1_short_id, 10308, 0, 31, True))

                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 0, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 1, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 2, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 3, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 4, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 5, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 6, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 7, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 8, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 9, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 10, server2_short_id, 1))
                test.expect(test.dut.dstl_lwm2m_set_server_acl(stack_id_str, 11, server2_short_id, 1))

                '''test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 0))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 1))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 2))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 3))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 4))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 5))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 6))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 7))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 8))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 9))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 10))
                test.expect(test.dut.dstl_lwm2m_read_resource_from_mem(stack_id_str, 2, 11))'''

                test.dut.dstl_restart()
                app_list = test.dut.dstl_lwm2m_read_application()
                if stack_id_str not in app_list:
                    test.log.error("Server object not stored as expected")

        test.log.info("2.Delete server_2")
        test.expect(test.dut.dstl_lwm2m_del_server(stack_id_str, 1))

        test.log.info("3.Modify resources in existed stack_id_str")
        test.expect(test.dut.dstl_lwm2m_modify_server_host(stack_id_str, 0, server2_address, is_server2_bootstrap,
                                                           server2_sec_mode))
        test.expect(test.dut.dstl_lwm2m_get_server_address(stack_id_str, 0) == server2_address)
        test.expect(test.dut.dstl_lwm2m_is_server_bootstrap(stack_id_str, 0) == is_server2_bootstrap)
        test.expect(test.dut.dstl_lwm2m_get_server_sec_mode(stack_id_str, 0) == server2_sec_mode)

        test.expect(test.dut.dstl_lwm2m_get_server_short_id(stack_id_str, 0) == server1_short_id)
        test.expect(test.dut.dstl_lwm2m_get_server_lifetime(stack_id_str, 0) == lifetime)
        test.expect(test.dut.dstl_lwm2m_get_server_pmax(stack_id_str, 0) == default_pmax)
        test.expect(test.dut.dstl_lwm2m_get_server_pmin(stack_id_str, 0) == default_pmin)
        test.expect(test.dut.dstl_lwm2m_get_server_disable_timeout(stack_id_str, 0) == disable_timeout)
        test.expect(test.dut.dstl_lwm2m_get_server_binding(stack_id_str, 0) == binding)
        test.expect(test.dut.dstl_lwm2m_is_server_notification_stored(stack_id_str, 0) == notification_stored)

        lifetime1 = 60
        default_pmin1 = 2
        default_pmax1 = 90
        disable_timeout1 = 120
        notification_stored1 = False
        binding1 = "UQ"
        test.expect(test.dut.dstl_lwm2m_modify_server_lifetime(stack_id_str, 0, lifetime1))
        test.expect(test.dut.dstl_lwm2m_modify_server_pmin(stack_id_str, 0, default_pmin1))
        test.expect(test.dut.dstl_lwm2m_modify_server_pmax(stack_id_str, 0, default_pmax1))
        test.expect(test.dut.dstl_lwm2m_modify_server_disable_timeout(stack_id_str, 0, disable_timeout1))
        test.expect(test.dut.dstl_lwm2m_modify_server_notification_stored(stack_id_str, 0, notification_stored1))
        test.expect(test.dut.dstl_lwm2m_modify_server_binding(stack_id_str, 0, binding1))

        test.expect(test.dut.dstl_lwm2m_get_server_lifetime(stack_id_str, 0) == lifetime1)
        test.expect(test.dut.dstl_lwm2m_get_server_pmax(stack_id_str, 0) == default_pmax1)
        test.expect(test.dut.dstl_lwm2m_get_server_pmin(stack_id_str, 0) == default_pmin1)
        test.expect(test.dut.dstl_lwm2m_get_server_disable_timeout(stack_id_str, 0) == disable_timeout1)
        test.expect(test.dut.dstl_lwm2m_get_server_binding(stack_id_str, 0) == binding1)
        test.expect(test.dut.dstl_lwm2m_is_server_notification_stored(stack_id_str, 0) == notification_stored1)

        test.log.info("4.Create the second application")
        stack_id_str2 = "stack_id_test2"
        app_list = test.dut.dstl_lwm2m_read_application()

        if stack_id_str2 in app_list:
            test.expect(test.log.error("The stack_id_str is already existed, please check the enviornment"))
        else:
            test.expect(test.dut.dstl_lwm2m_add_server_instance_to_mem(stack_id_str2, 0, server1_address,
                                                                       is_server1_bootstrap, server1_sec_mode,
                                                                       server2_short_id, lifetime, default_pmin,
                                                                       default_pmax, disable_timeout,
                                                                       notification_stored, binding))
            test.expect(test.dut.dstl_lwm2m_store_sever_instance(stack_id_str2, 0))

            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 0, server2_short_id, 1, 1, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 1, server2_short_id, 1, 2, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 2, server2_short_id, 3, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 3, server2_short_id, 4, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 4, server2_short_id, 5, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 5, server2_short_id, 6, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 6, server2_short_id, 7, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 7, server2_short_id, 10, 0, 15, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 8, server2_short_id, 11, 0, 31, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 9, server2_short_id, 16, 0, 31, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 10, server2_short_id, 16, 1, 31, True))
            test.expect(test.dut.dstl_lwm2m_create_acl_obj(stack_id_str2, 11, server2_short_id, 10308, 0, 31, True))

            app_list = test.dut.dstl_lwm2m_read_application()
            if stack_id_str2 not in app_list:
                test.log.error("Server object not stored as expected")

        test.log.info("5.Restart module and check if both application existed")
        test.dut.dstl_restart()
        app_list = test.dut.dstl_lwm2m_read_application()
        if stack_id_str not in app_list:
            test.log.error("Application " + stack_id_str + " not stored successfully")
        if stack_id_str2 not in app_list:
            test.log.error("Application " + stack_id_str2 + " not stored successfully")

        test.log.info("6.Check setting in two applications")
        test.log.info("Settings for " + stack_id_str)
        test.expect(test.dut.dstl_lwm2m_get_server_address(stack_id_str, 0) == server2_address)
        test.expect(test.dut.dstl_lwm2m_is_server_bootstrap(stack_id_str, 0) == is_server2_bootstrap)
        test.expect(test.dut.dstl_lwm2m_get_server_sec_mode(stack_id_str, 0) == server2_sec_mode)
        test.expect(test.dut.dstl_lwm2m_get_server_short_id(stack_id_str, 0) == server1_short_id)
        test.expect(test.dut.dstl_lwm2m_get_server_lifetime(stack_id_str, 0) == lifetime1)
        test.expect(test.dut.dstl_lwm2m_get_server_pmax(stack_id_str, 0) == default_pmax1)
        test.expect(test.dut.dstl_lwm2m_get_server_pmin(stack_id_str, 0) == default_pmin1)
        test.expect(test.dut.dstl_lwm2m_get_server_disable_timeout(stack_id_str, 0) == disable_timeout1)
        test.expect(test.dut.dstl_lwm2m_get_server_binding(stack_id_str, 0) == binding1)
        test.expect(test.dut.dstl_lwm2m_is_server_notification_stored(stack_id_str, 0) == notification_stored1)

        test.log.info("Settings for " + stack_id_str2)
        test.expect(test.dut.dstl_lwm2m_get_server_address(stack_id_str2, 0) == server1_address)
        test.expect(test.dut.dstl_lwm2m_is_server_bootstrap(stack_id_str2, 0) == is_server1_bootstrap)
        test.expect(test.dut.dstl_lwm2m_get_server_sec_mode(stack_id_str2, 0) == server1_sec_mode)
        test.expect(test.dut.dstl_lwm2m_get_server_short_id(stack_id_str2, 0) == server2_short_id)
        test.expect(test.dut.dstl_lwm2m_get_server_lifetime(stack_id_str2, 0) == lifetime)
        test.expect(test.dut.dstl_lwm2m_get_server_pmax(stack_id_str2, 0) == default_pmax)
        test.expect(test.dut.dstl_lwm2m_get_server_pmin(stack_id_str2, 0) == default_pmin)
        test.expect(test.dut.dstl_lwm2m_get_server_disable_timeout(stack_id_str2, 0) == disable_timeout)
        test.expect(test.dut.dstl_lwm2m_get_server_binding(stack_id_str2, 0) == binding)
        test.expect(test.dut.dstl_lwm2m_is_server_notification_stored(stack_id_str2, 0) == notification_stored)

        test.log.info("7. Delete the second application ")
        test.expect(test.dut.dstl_lwm2m_del_application(stack_id_str))
        test.expect(test.dut.dstl_lwm2m_del_application(stack_id_str2))
        app_list = test.dut.dstl_lwm2m_read_application()
        if stack_id_str in app_list:
            test.log.error("Application " + stack_id_str + " not deleted successfully" )
        if stack_id_str2 in app_list:
            test.log.error("Application " + stack_id_str2 + " not deleted successfully")

        test.log.info("8.Restart module and check if both application not existed")
        test.dut.dstl_restart()
        app_list = test.dut.dstl_lwm2m_read_application()
        if stack_id_str in app_list:
            test.log.error("Application " + stack_id_str + " not deleted successfully")
        if stack_id_str2 in app_list:
            test.log.error("Application " + stack_id_str2 + " not deleted successfully")

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
