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
from dstl.auxiliary import devboard
from dstl.internet_service import start_stop_mods_client
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.schedule_fota_from_mods_server import ModsServer
from dstl.internet_service import trigger_fota_action_on_mods_client
from dstl.internet_service import set_get_mods_client_service_tag
from dstl.internet_service import trigger_fota_action_on_mods_client


class ModsFotaNetworkLoss(BaseTest):
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
        test.firware_1 = "SERVAL_300-ATT_014E"
        test.firware_package_1 = "Serval_014E_022B"
        #
        test.firware_2 = "SERVAL_300-ATT_022B"
        test.firware_package_2 = "Serval_014E_022B"
        ############################################

        imei = test.dut.dstl_get_imei()

        test.log.info("*************************************")
        test.log.info("1.Start Mods_Fota_NetworkLoss test...")
        test.log.info("*************************************")
        test.dut.dstl_check_mods_service_status()
        test.dut.dstl_stop_mods_service()
        test.expect(test.dut.dstl_restart())
        test.sleep(60)

        test.log.info("*************************************")
        test.log.info("2.Start IoT Service Agent service...")
        test.log.info("*************************************")
#        test.expect(test.dut.dstl_register_to_network())

        test.get_firmware_info()
        test.log.info("Current Software version: {}".format(test.current_firmware))
        test.log.info("Target Software version: {}".format(test.target_firmware))
        test.log.info("Target Firmware package: {}".format(test.target_package))
        test.sleep(60)

        test.log.info("*************************************")
        test.log.info("3. Trigger FOTA Job from MODS server...")
        test.log.info("*************************************")

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
        test.sleep(30)
        mods_server_obj.dstl_check_fota_job_status(job_id)
        test.sleep(30)

        test.log.info("*************************************")
        test.log.info("4. Wait for the Init firmware download URC...")
        test.log.info("*************************************")
        test.dut.dstl_check_mods_service_status()
        test.dut.dstl_start_mods_service()
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","init".*', 60 * 5)

        test.log.info("*************************************")
        test.log.info("5. Wait for download progress URC and trigger NetworkLoss...")
        test.log.info("*************************************")
        i = random.randrange(5, 100, 5)
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)

        test.log.info("*************************************")
        test.log.info("6. Trigger Module network loss...")
        test.log.info("*************************************")
        test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=60)
        test.sleep(5 * 60)

        test.log.info("*************************************")
        test.log.info("7. Revocer Module network...")
        test.log.info("*************************************")
        test.dut.at1.send_and_verify("AT+COPS=0", "OK", timeout=300, retry=30)
        if test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress".*', 10 * 60):
            test.log.info("Revocer Module network...")
        else:
            test.log.info("Revocer Module network failed...")

        test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*')
        test.dut.at1.wait_for('.*SRVACT: "MODS","ready","to update"\\s+')
        test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 5 * 60)
        test.dut.at1.wait_for(".*SYSSTART.*", 5 * 60)
        test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
        test.dut.at1.send_and_verify("AT^CICRET=SWN")

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