#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC
import unicorn

import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.internet_service.schedule_fota_from_mods_server import ModsServer


class Test(BaseTest):
    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
                                 "serval@gemalto.com", "mods,123")

        test.firware_1 = "SERVAL_100_050"
        test.firware_package_1 = "SERVAL_046_044"

        test.firware_2 = "SERVAL_100_050"
        test.firware_package_2 = "SERVAL_044_046"

        imei = "004401083356838"

        test.log.info("*************************************")
        test.log.info("Start MODS FOTA load test.")
        test.log.info("*************************************")

        total_loop = 20
        current_loop = 0

        while current_loop < total_loop:
            test.log.info("*************************************")
            test.log.info("FOTA Loop {} starts...".format(current_loop+1))
            test.log.info("*************************************")
            test.dut. dstl_register_to_nbiot()
            test.dut.at1.send_and_verify("AT+CREG=2")
            test.dut.at1.send_and_verify("AT+CGREG=2")

            test.get_firmware_info()
            test.log.info("Current Software version: {}".format(test.current_firmware))
            test.log.info("Target Software version: {}".format(test.target_firmware))
            test.log.info("Target Firmware package: {}".format(test.target_package))

            if test.target_package:
                fota_job_name = "{}_{}_FOTA_Load_{}".format(getpass.getuser(),
                                                            time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                            str(current_loop+1).zfill(3))
                start_time = (datetime.now()+timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                end_time = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                               test.target_package,
                                                               imei,
                                                               start_time,
                                                               end_time)
                mods_server_obj.dstl_check_fota_job_status(job_id)
                if test.dut.at1.wait_for(".*FW_MISMATCH.*", timeout=60*60*2):
                    test.log.info("Restart the module...")
                    test.dut.dstl_restart()

                    test.log.info("Make sure the job status will not affect the next round FOTA...")
                    mods_server_obj.dstl_disable_fota_job(job_id)

                else:
                    test.log.error("Fail to update during the timeout. ")

                    test.log.info("Make sure the job status will not affect the next round FOTA...")
                    mods_server_obj.dstl_disable_fota_job(job_id)

                    test.log.info("Restart the module...")
                    test.dut.dstl_restart()

            else:
                test.log.error("Fail to get the target Firmware package.")

            current_loop += 1

    def get_firmware_info(test):
        test.dut.dstl_detect_comprehensive()
        current_firmware = test.dut.software
        test.target_package = None
        test.current_firmware = None

        if current_firmware in test.firware_1:
            test.current_firmware = test.firware_1
            test.target_firmware = test.firware_2
            test.target_package = test.firware_package_1

        elif current_firmware in test.firware_2:
            test.current_firmware = test.firware_2
            test.target_firmware = test.firware_1
            test.target_package = test.firware_package_2

        else:
            test.log.error("Unmatched firmwares.")

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
