#responsible: jian-j.li@thalesgroup.com
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
from dstl.network_service import network_access_type
from dstl.network_service import operator_selector
from dstl.identification import get_imei
from dstl.internet_service.schedule_fota_from_mods_server import ModsServer
from dstl.internet_service import trigger_fota_action_on_mods_client

class ModsFotaRatChange(BaseTest):
    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
                                 "serval@gemalto.com", "mods,123")
        # mods_server_obj = ModsServer("https://partners-mods.gemalto.io/", "5684", "root.Thales.ST", "yafan.liu@thalesgroup.com",
        #                              "Edcol.1234")

        ############################################
        # Input parameters:
        test.firware_1 = "_300-ATT_014"
        test.firware_package_1 = "Serval_014_014A"
        #
        test.firware_2 = "_300-ATT_014A"
        test.firware_package_2 = "Serval_014A_014"
        ############################################

        imei = test.dut.dstl_get_imei()


        test.log.info("*************************************")
        test.log.info("Start MODS FOTA RAT change test.")
        test.log.info("*************************************")

        total_loop = 3
        current_loop = 0

        while current_loop < total_loop:
            test.log.info("*************************************")
            test.log.info("FOTA RAT change test Loop {} starts...".format(current_loop+1))
            test.log.info("*************************************")
            test.dut.dstl_register_to_network()
            test.dut.at1.send_and_verify("at+creg=2")
            test.dut.at1.send_and_verify("at+cgreg=2")
            time.sleep(10)

            test.get_firmware_info()
            test.log.info("Current Software version: {}".format(test.current_firmware))
            test.log.info("Target Software version: {}".format(test.target_firmware))
            test.log.info("Target Firmware package: {}".format(test.target_package))

            test.log.info("2. Start IoT Service Agent service...")
            test.expect(test.dut.dstl_register_to_gsm())
            test.expect(test.dut.dstl_start_mods_service())

            test.log.info("3. Trigger FOTA from MODS server...")
            fota_job_name = "{}_{}_FOTA_Load_{}".format(getpass.getuser(),
                                                        time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                        '001')
            start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                        test.target_package,
                                                                        imei,
                                                                        start_time,
                                                                        end_time)
            mods_server_obj.dstl_check_fota_job_status(job_id)
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","ready","to download"\\s+')

            test.log.info("5. Wait for progress URC...")
            i = 5
            while i < 90:
                test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)
                i += 5

            test.log.info("6.RAT change during FOTA.")
            test.dut.dstl_register_to_lte()
            test.dut.at1.send_and_verify("at+creg=2")
            test.dut.at1.send_and_verify("at+cgreg=2")
            time.sleep(30)

            test.log.info("7. Wait for progress URC...")
            i = 5
            while i < 100:
                test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)
                i += 5
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*')

            test.log.info("8. Initiate the firmware download...")

            test.dut.at1.wait_for('.*SRVACT: "MODS","ready","to update"\\s+')

            test.expect(test.dut.dstl_trigger_mods_firmware_update())

            test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 60)
            test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 5 * 60)
            test.dut.at1.wait_for(".*SYSSTART.*", 5 * 60)
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
            test.dut.at1.send_and_verify("AT^CICRET=SWN")

            if test.target_package:
                fota_job_name = "{}_{}_FOTA_unconditional_{}".format(getpass.getuser(),
                                                                     time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                                     str(current_loop + 1).zfill(3))
                start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                            test.target_package,
                                                                            imei,
                                                                            start_time,
                                                                            end_time)
                mods_server_obj.dstl_check_fota_job_status(job_id)
                if test.dut.at1.wait_for(".*SYSSTART.*", timeout=60 * 60):
                    test.log.info("SYSTART received")
                    test.dut.dstl_detect_comprehensive()
                    current_firmware = test.dut.software
                    test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software, ))

                    if current_firmware in test.target_firmware:
                        test.log.info("FOTA success in loop {}".format(current_loop + 1))
                        test.expect(True)
                    else:
                        test.log.info("FOTA fail in loop {}".format(current_loop + 1))
                        test.expect(False)

                    test.log.info("Register to network...")
                    test.expect(test.dut.dstl_register_to_network())

                    test.log.info("Sleep two minutes to let client automatically register to server...")
                    test.sleep(60 * 2)

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









