#responsible: jian-j.li@thalesgroup.com
#location: Beijing
#TC0105485.001
import unicorn
import getpass
import time
import random
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.internet_service import start_stop_mods_client
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer
from dstl.internet_service import trigger_fota_action_on_mods_client
from dstl.internet_service import set_get_mods_client_service_tag
from dstl.internet_service import trigger_fota_action_on_mods_client

class ModsFotaAfterHours(BaseTest):
    def setup(test):
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        test.log.info("ModsFotaAfterHours started")
        test.log.info("*************************************")
        test.log.info("1.ReStart Mods client...")
        test.log.info("*************************************")
        if test.dut.dstl_check_mods_service_status():
            test.dut.dstl_stop_mods_service()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        if not test.dut.dstl_check_mods_service_status():
            test.dut.dstl_start_mods_service()
        test.dut.detect()
        test.original_firmware = test.dut.software

        test.log.info("*************************************")
        test.log.info("2.Sleep 16 hours...")
        test.log.info("*************************************")
        # test.sleep(16 * 60 * 60)
        test.sleep(120)

        test.log.info("*************************************")
        test.log.info("3.Do fota...")
        test.log.info("*************************************")
        if test.dut.dstl_check_mods_service_status():
            test.do_fota()

        test.log.info("*************************************")
        test.log.info("4.Fota back to original version...")
        test.log.info("*************************************")
        test.sleep(60)
        test.dut.detect()
        test.current_firmware = test.dut.software
        if test.current_firmware != test.original_firmware:
            test.do_fota()

        test.log.info("ModsFotaAfterHours finished")




        # mods_server_obj = ModsServer("https://partners-mods.gemalto.io/", "5684", "root.Thales.ST", "yafan.liu@thalesgroup.com",
        #                              "Edcol.1234")

        ############################################
        # Input parameters:
        # test.firware_1 = "_300-ATT_014"
        # test.firware_package_1 = "Serval_014_014A"
        # #
        # test.firware_2 = "_300-ATT_014A"
        # test.firware_package_2 = "Serval_014_014A"
        ############################################
        # mods_server_obj = ModsServer()
        # imei = test.dut.dstl_get_imei()
        # fota_package = mods_server_obj.dstl_get_fota_package()
        # target_firmware = mods_server_obj.dstl_get_target_firmware()
        #
        #
        #
        # test.log.info("*************************************")
        # test.log.info("2.Start IoT Service Agent service...")
        # test.log.info("*************************************")
        #
        #
        # # test.get_firmware_info()
        # # test.log.info("Current Software version: {}".format(test.current_firmware))
        # test.log.info("Target Software version: {}".format(test.target_firmware))
        # test.log.info("Fota package: {}".format(test.fota_package))
        # test.sleep(60)
        #
        # test.log.info("*************************************")
        # test.log.info("3. Trigger FOTA Job from MODS server...")
        # test.log.info("*************************************")
        #
        # fota_job_name = "{}_{}_FOTA_After_Hours_{}".format(getpass.getuser(),
        #                                             time.strftime("%Y-%m-%d_%H:%M:%S"),
        #                                             '001')
        # start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
        #                                                             test.fota_package,
        #                                                             imei,
        #                                                             start_time,
        #                                                             end_time)
        # mods_server_obj.dstl_check_fota_job_status(job_id)
        # test.sleep(30)
        # mods_server_obj.dstl_check_fota_job_status(job_id)
        # test.sleep(16 * 60 * 60)
        #
        # test.log.info("*************************************")
        # test.log.info("4. Wait for the Init firmware download URC...")
        # test.log.info("*************************************")
        # test.dut.dstl_check_mods_service_status()
        # test.dut.dstl_start_mods_service()
        # test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","init".*', 60)
        #
        # test.log.info("*************************************")
        # test.log.info("5. Wait for the download progress URC...")
        # test.log.info("*************************************")
        #
        #
        # test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress".*', 5 * 60)
        #
        # test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*', 5 * 60)
        #
        # test.log.info("*************************************")
        # test.log.info("6. Wait for the FOTA Install URC...")
        # test.log.info("*************************************")
        # test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 60)
        # test.dut.at1.wait_for(".*PHASE 1 OK!.*", 5 * 60)
        # test.dut.at1.wait_for(".*SYSSTART.*", 5 * 60)
        # test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
        # test.dut.at1.send_and_verify("AT^CICRET=SWN")

    # def get_firmware_info(test):
    #     test.dut.dstl_detect_comprehensive()
    #     current_firmware = test.dut.software
    #     test.target_package = None
    #     test.current_firmware = None
    #
    #     if current_firmware in test.firware_1:
    #         test.current_firmware = test.firware_1
    #         test.target_firmware = test.firware_2
    #         test.target_package = test.firware_package_1
    #
    #     elif current_firmware in test.firware_2:
    #         test.current_firmware = test.firware_2
    #         test.target_firmware = test.firware_1
    #         test.target_package = test.firware_package_2
    #
    #     else:
    #         test.log.error("Unmatched firmwares.")

    def do_fota(test):
        mods_server_obj = ModsServer()
        fota_package = mods_server_obj.dstl_get_fota_package()
        target_firmware = mods_server_obj.dstl_get_target_firmware()
        imei = test.dut.dstl_get_imei()

        # test.log.info("Current Software version: {}".format(test.current_firmware))
        test.log.info("Target Software version: {}".format(target_firmware))
        test.log.info("Target Firmware package: {}".format(fota_package))

        if fota_package:
            fota_job_name = "{}_{}_FOTA_After_Hours_{}".format(getpass.getuser(),
                                                        time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                        str(1).zfill(3))
            start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                        fota_package,
                                                                        imei,
                                                                        start_time,
                                                                        end_time)
            mods_server_obj.dstl_check_job_status(job_id)
            test.log.info("Wait for progress URC...")
            i = 5
            while i < 100:
                test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)
                i += 5
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*')
            test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 5 * 60)
            test.dut.at1.wait_for(".*SYSSTART.*", 10 * 60)
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*', 120)
            test.dut.dstl_detect_comprehensive()
            current_firmware = test.dut.software
            if current_firmware in target_firmware:
                test.log.info("FOTA success")
                test.expect(True)
            else:
                test.log.info("FOTA fail")
                test.expect(False)

            test.log.info("Make sure the job status will not affect the next round FOTA...")
            mods_server_obj.dstl_disable_job(job_id)
        else:
            test.log.error("Fail to get the target Firmware package.")

    def cleanup(test):
        pass

if __name__ == "__main__":
    unicorn.main()