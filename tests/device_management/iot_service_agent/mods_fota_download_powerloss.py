#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0104354.001 TpLwm2mFotaDownloadPowerLoss

import unicorn

import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer

class Test(BaseTest):
    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        mods_server_obj = ModsServer()
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
        #                          "serval@gemalto.com", "mods,123")
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.mods",
        #                              "serval@gemalto.com", "mods,123")

        ############################################
        # Input parameters:
        # test.firmware_1 = "_300-ATT_014A"
        # test.target_package = "Serval_014A_014"
        # #
        # test.target_firmware = "_300-ATT_014"
        # test.firware_package_2 = "Serval_014A_014"
        ############################################

        imei = test.dut.dstl_get_imei()
        test.dut.dstl_register_to_nbiot()
        test.dut.at1.send_and_verify("AT+CREG=2")
        test.dut.at1.send_and_verify("AT+CGREG=2")

        test.log.info("*************************************")
        test.log.info("Step1: Create and schedule FOTA job.")
        test.log.info("*************************************")

        fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                                    time.strftime("%Y-%m-%d_%H:%M:%S"))
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                    test.upgrade_fota_package_name,
                                                                    imei,
                                                                    start_time,
                                                                    end_time)
        mods_server_obj.dstl_check_job_status(job_id)

        test.log.info("*************************************")
        test.log.info("Step2: Cut down power during download process.")
        test.log.info("*************************************")

        if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress"', timeout=60*5):
            test.log.info("Firmware downloading...")
            test.expect(True)
            if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress","30%"', timeout=60*5):
                test.log.info("Reset module.")
                test.dut.dstl_reset_with_vbatt_via_dev_board()
                test.log.info("Check if download can recover.")
                if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress"', timeout=60 * 5):
                    test.log.info("Recover to download...")
                    test.expect(True)
                else:
                    test.log.info("Module cannot recover to download.")
                    test.expect(False)

            if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress","50%"', timeout=60*5):
                test.log.info("Reset module.")
                test.dut.dstl_reset_with_vbatt_via_dev_board()
                test.log.info("Check if download can recover.")
                if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress"', timeout=60 * 5):
                    test.log.info("Recover to download...")
                    test.expect(True)
                else:
                    test.log.info("Module cannot recover to download.")
                    test.expect(False)

            if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress","70%"', timeout=60*5):
                test.log.info("Reset module.")
                test.dut.dstl_reset_with_vbatt_via_dev_board()
                test.log.info("Check if download can recover.")
                if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress"', timeout=60 * 5):
                    test.log.info("Recover to download...")
                    test.expect(True)
                else:
                    test.log.info("Module cannot recover to download.")
                    test.expect(False)

        else:
            test.log.info("Fail to download.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step3: After download, update FW.")
        test.log.info("*************************************")

        if test.dut.at1.wait_for(".*Checksum OK.*", timeout=60 * 10):
            test.log.info("Begin to update...")
            test.expect(True)
        else:
            test.log.info("Fail to enter update process.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step4: Check FW version.")
        test.log.info("*************************************")

        if test.dut.at1.wait_for(".*update success.*", timeout=60*10):
            test.log.info("Update success.")
            test.expect(True)
            test.dut.dstl_detect_comprehensive()
            current_firmware = test.dut.software
            test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software, ))

            if (current_firmware in test.target_firmware) and (len(current_firmware) == len(test.target_firmware)):
                test.log.info("FOTA success.")
                test.expect(True)
            else:
                test.log.info("Mismatch FW.")
                test.expect(False)
        else:
            test.log.info("Update fail.")
            test.expect(False)

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()