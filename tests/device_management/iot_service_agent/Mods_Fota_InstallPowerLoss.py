#responsible: jian-j.li@thalesgroup.com
#location: Beijing
#TC
import unicorn
import getpass
import time
import random
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary import init
# from dstl.auxiliary import devboard
from dstl.internet_service import start_stop_mods_client
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer
from dstl.internet_service.mods_client import ModsClient
from dstl.internet_service import trigger_fota_action_on_mods_client
from dstl.internet_service import set_get_mods_client_service_tag
from dstl.internet_service import trigger_fota_action_on_mods_client

class ModsFotaInstallPowerLoss(BaseTest):
    def setup(test):
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
        #                          "serval@gemalto.com", "mods,123")
        # mods_server_obj = ModsServer("https://partners-mods.gemalto.io/", "5684", "root.Thales.ST", "yafan.liu@thalesgroup.com",
        #                              "Edcol.1234")
        test.log.info("*************************************")
        test.log.info("Start Mods_Fota_InstallPowerLoss test...")
        test.log.info("*************************************")
        test.dut.dstl_register_to_network()
        test.dut.at1.send_and_verify("AT+CREG=2")
        test.dut.at1.send_and_verify("AT+CGREG=2")
        imei = test.dut.dstl_get_imei()
        mods_server_obj = ModsServer()
        mods_client = ModsClient(True)
        test.target_package = mods_server_obj.dstl_get_fota_package()
        test.target_firmware = mods_server_obj.dstl_get_target_firmware()
        test.current_firmware = test.dut.software
        test.original_firmware = test.dut.software

        test.log.info("1.Restart IoT Service Agent service...")
        test.log.info("*************************************")
        if test.dut.dstl_check_mods_service_status():
            for i in range(0, 10):
                if test.dut.dstl_stop_mods_service():
                    break
                test.sleep(10)

        test.sleep(60)

        for i in range(0, 10):
            if test.dut.dstl_start_mods_service():
                break
            test.sleep(10)

        for i in range(0, 10):
            if mods_client.dstl_is_client_active():
                break
            test.sleep(20)
        # test.expect(test.dut.dstl_restart())
        # test.sleep(60)
#        test.expect(test.dut.dstl_register_to_gsm())
#         test.get_firmware_info()
        test.log.info("Current Software version: {}".format(test.current_firmware))
        test.log.info("Target Software version: {}".format(test.target_firmware))
        test.log.info("Target Firmware package: {}".format(test.target_package))
        test.sleep(60)

        test.log.info("*************************************")
        test.log.info("2. Trigger FOTA Job from MODS server...")
        test.log.info("*************************************")

        fota_job_name = "{}_{}_FOTA_InstallPowerLoss_{}".format(getpass.getuser(),
                                                    time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                    '001')
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                    test.target_package,
                                                                    imei,
                                                                    start_time,
                                                                    end_time)
        mods_server_obj.dstl_check_job_status(job_id)

        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","init".*', 60)
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress".*', 5 * 60)
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*', 20 * 60)

        test.log.info("*************************************")
        test.log.info("3. Power loss while FOTA Installing...")
        test.log.info("*************************************")
        i = random.randint(0, 10)
        while True:
            if test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 5 * 60):
                test.sleep(i)
                i += 10
            else:
                test.dut.at1.wait_for(".*PHASE 1 OK!.*", 10)
                break

            test.log.info("*************************************")
            test.log.info("Module get power loss...")
            test.log.info("*************************************")
            test.expect(test.dut_devboard.send_and_verify("MC:VBATT=OFF", ".*OK.*", timeout=30))
            test.sleep(30)

            test.log.info("*************************************")
            test.log.info("Power on module...")
            test.log.info("*************************************")
            test.expect(test.dut_devboard.send_and_verify("MC:VBATT=ON", ".*OK.*", timeout=30))
            test.expect(test.dut_devboard.send_and_verify("MC:IGT=555", ".*OK.*", timeout=30))

        test.dut.at1.wait_for(".*SYSSTART.*", 60)
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
        test.dut.at1.send_and_verify("AT^CICRET=SWN")

        test.log.info("*************************************")
        test.log.info("4. Fota back to original software version...")
        test.log.info("*************************************")
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

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()

