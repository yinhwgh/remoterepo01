# responsible: yafan.liu@thalesgroup.com
# location: Beijing
# TC0104810.001

import unicorn

import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer


class Test(BaseTest):
    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        # test.access_server = "partners-mods.gemalto.io"
        test.access_server = "https://10.151.127.73:8443/mods/ui"  #test network Mods address
        test.access_server_port = ""
        test.job_server = "10.151.127.73:39280"
        test.job_server_port = ""
        test.device_inquire_port = ""
        test.organization = "root.SERVAL"
        test.user = "serval@gemalto.com"
        test.password = "mods,123"
        pass

    def run(test):

        imei = test.dut.dstl_get_imei()
        test.dut.dstl_register_to_network()
        test.dut.at1.send_and_verify("AT+CREG=2")
        test.dut.at1.send_and_verify("AT+CGREG=2")

        mods_server_obj = ModsServer()
        test.target_package = mods_server_obj.dstl_get_fota_package()
        test.target_firmware = mods_server_obj.dstl_get_target_firmware()
        test.current_firmware = test.dut.software
        test.original_firmware = test.dut.software

        test.log.info("*************************************")
        test.log.info("Start MODS FOTA Thread.")
        test.log.info("*************************************")

        test.log.info("Current Software version: {}".format(test.current_firmware))
        test.log.info("Target Software version: {}".format(test.target_firmware))
        test.log.info("Target Firmware package: {}".format(test.target_package))

        fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                                    time.strftime("%Y-%m-%d_%H:%M:%S"))
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                    test.target_package,
                                                                    imei,
                                                                    start_time,
                                                                    end_time)
        print(job_id)
        mods_server_obj.dstl_check_job_status(job_id)
        test.ipservice_download()

        if test.dut.at1.wait_for(".*SYSSTART.*", timeout=60 * 60):
            test.log.info("SYSTART received")
            test.dut.dstl_detect_comprehensive()
            current_firmware = test.dut.software
            test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software))

            if current_firmware in test.target_firmware:
                test.log.info("FOTA success.")
                test.expect(True)
            else:
                test.log.info("FOTA fail.")
                test.expect(False)

            test.log.info("Register to network...")
            test.expect(test.dut.dstl_register_to_network())
            test.log.info("Make sure the job status will not affect the next round FOTA...")
            mods_server_obj.dstl_disable_job(job_id)

        else:
            test.log.error("Fail to update during the timeout. ")

            test.log.info("Make sure the job status will not affect the next round FOTA...")
            mods_server_obj.dstl_cancel_fota_job(job_id)

            test.log.info("Restart the module...")
            test.dut.dstl_restart()

        test.dut.dstl_detect_comprehensive()
        current_firmware = test.dut.software
        if current_firmware == test.original_firmware:
            test.log.info("Test Completed...")
        else:
            test.target_package = mods_server_obj.dstl_get_fota_package()
            test.target_firmware = mods_server_obj.dstl_get_target_firmware()
            fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                                time.strftime("%Y-%m-%d_%H:%M:%S"))
            start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                        test.target_package,
                                                                        imei,
                                                                        start_time,
                                                                        end_time)
            print(job_id)
            mods_server_obj.dstl_check_job_status(job_id)
            if test.dut.at1.wait_for(".*SYSSTART.*", timeout=60 * 60):
                test.log.info("SYSTART received")
                test.dut.dstl_detect_comprehensive()
                current_firmware = test.dut.software
                test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software))

                if current_firmware in test.target_firmware:
                    test.log.info("FOTA success.")
                    test.expect(True)
                else:
                    test.log.info("FOTA fail.")
                    test.expect(False)

                test.log.info("Register to network...")
                test.expect(test.dut.dstl_register_to_network())
                test.log.info("Make sure the job status will not affect the next round FOTA...")
                mods_server_obj.dstl_disable_job(job_id)

            else:
                test.log.error("Fail to update during the timeout. ")

                test.log.info("Make sure the job status will not affect the next round FOTA...")
                mods_server_obj.dstl_cancel_job(job_id)

                test.log.info("Restart the module...")
                test.dut.dstl_restart()

    def ipservice_download(test):
        test.ipservice_address = "http://www.itte2.com/phpuploader/savefiles/file_3m.zip"
        # current_loop = 0
        # total_loop = 100

        test.log.info("*************************************")
        test.log.info("Start IP service download Thread.")
        test.log.info("*************************************")

        test.dut.at1.send_and_verify("AT^SICA=1,1")
        test.dut.at1.send_and_verify("at^siss=0,srvType,Http")
        test.dut.at1.send_and_verify("at^siss=0,conId,1")
        test.dut.at1.send_and_verify("at^siss=0,address,{}".format(test.ipservice_address))
        test.dut.at1.send_and_verify("at^siss=0,cmd,get")
        test.dut.at1.send_and_verify("at^siso=0")
        if test.dut.at1.wait_for(".*SISR.*", timeout=30):
            test.log.info("Begin to download data from IP service.")
            while not test.dut.at1.wait_for(".*download success.*"):
                test.dut.at1.send_and_verify("at^sisr=0,1000")
                test.log.info("Sleep 30s.")
                test.sleep(30)
            test.dut.at1.send_and_verify("at^sisc=0")
        else:
            test.log.info("IP service failed.")
            test.expect(False)

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()