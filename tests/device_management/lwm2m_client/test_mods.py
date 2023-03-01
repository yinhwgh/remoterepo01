import unicorn

import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.internet_service.mods_client import ModsClient
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer
# import base64
# import requests
# import dstl


class Test(BaseTest):
    def setup(test):
        pass

    def run(test):
        mods_server_obj = ModsServer()
        fota_job_name = "test"
        fw_package_name = mods_server_obj.dstl_get_fota_package()
        model = "EXS62-W"
        imei = test.dut.dstl_get_imei()    #"004401083714548"
        print(imei)
        phone_number = "+8613520876589"
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # test.dut.detect()
        # product = test.dut.product
        # print(product)
        mods_client = ModsClient()
        #print(mods_client.dstl_is_client_active())
        # mods_client.dstl_import_certificate()
        mods_server_obj.dstl_configure_device_on_mods_server()
        mods_client.dstl_configure_mods_server_to_device()
        #mods_client.dstl_start_client()
        # mods_server_obj.dstl_add_firmware_to_mods_server(fw_package_name, fw_path, model)
        # mods_server_obj.dstl_put_firmware_under_test(fw_package_name)
        #mods_server_obj.dstl_create_device_on_mods_server(model, "004401083714548", "+8613520896587")
        #mods_server_obj.dstl_add_msisdn_to_device(model, "004401083714548", "+8613520896587")
        # fw_package_name = "EXS82-W-054EC-054EB"
        # job_id = mods_server_obj.dstl_trigger_fota_from_mods_server("wenyan_test", fw_package_name, imei, start_time, end_time)
        # job_id = mods_server_obj.dstl_trigger_sms_activation_from_mods_server("wenyan_test_sms", imei, start_time, end_time)
        # if job_id:
        #     job_status = mods_server_obj.dstl_check_job_status(job_id)
        #     print(job_status)
        # if mods_server_obj.dstl_get_device_id(imei):
        #     mods_server_obj.dstl_add_msisdn_to_device(model, imei, phone_number)
        # else:
        #     mods_server_obj.dstl_create_device_on_mods_server(model, imei, phone_number)

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
