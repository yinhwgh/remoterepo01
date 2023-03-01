#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC0104557.001

import unicorn
import random
import getpass
import time

from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.internet_service import start_stop_mods_client
from dstl.internet_service import set_get_mods_client_service_tag
from dstl.internet_service import trigger_fota_action_on_mods_client
from dstl.identification import get_imei
from dstl.internet_service.lwm2m_constant import Lwm2mConstant
from dstl.internet_service.mods_server import ModsServer
from dstl.internet_service.mods_client import ModsClient


class ModsFotaConditional(BaseTest):
    def setup(test):
        # test.stack_id_str = "MODS"
        # test.server1_address = "coaps://10.170.47.251:15684"
        # test.is_server1_bootstrap = False
        # test.server1_sec_mode = Lwm2mConstant.CERTIFICATE_MODE
        # test.server1_short_id = "101"
        #
        # test.lifetime = 30
        # test.default_pmin = 1
        # test.default_pmax = 120
        # test.disable_timeout = 86400
        # test.notification_stored = True
        # test.binding = "UQS"
        # test.is_bootstrap = False

        # test.access_server = "https://partners-mods.gemalto.io"
        # test.access_server_port = ""
        # test.job_server = "partners-mods.gemalto.io"
        # test.job_server_port = ""
        # test.device_inquire_port = ""
        # test.organization = "root.Thales.Serval"
        # test.user = "wenyan.wu@thalesgroup.com"
        # test.password = "Mods,1234!"
        # test.firware_package = "SERVAL_054G_054F"

        # test.access_server = "10.151.127.73"
        # test.access_server_port = "8443"
        # test.job_server = "10.151.127.74"
        # test.job_server_port = "19280"
        # test.device_inquire_port = "19170"
        # test.organization = "root.SERVAL"
        # test.user = "serval@gemalto.com"
        # test.password = "mods,123"
        pass

    def run(test):

        deferlimits = [random.randint(1, 254), 254]
        # deferlimits = [254]
        mods_server_obj = ModsServer()
        mods_client = ModsClient(True)
        imei = test.dut.dstl_get_imei()

        for deferlimit in deferlimits:
            test.log.info('Set deferlimit...')
            test.expect(test.dut.dstl_set_fwdownload_deferlimit(str(deferlimit)))
            test.expect(test.dut.dstl_set_fwupdate_deferlimit(str(deferlimit)))

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

            test.target_package = mods_server_obj.dstl_get_fota_package()
            test.log.info("Target Firmware package: {}".format(test.target_package))

            test.log.info("Trigger FOTA from MODS server...")
            # Trigger FOTA from MODS server

            test.log.info("4. Wait for to download URC...")
            fota_job_name = "{}_{}_FOTA_Conditional_{}".format(getpass.getuser(),
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
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","init".*')
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","ready","to download"\\s+')
            test.sleep(60)

            test.log.info("5. Initiate the firmware download...")
            test.expect(test.dut.dstl_trigger_mods_firmware_download())

            test.log.info("6. Wait for progress URC...")
            i = 5
            while i < 100:
                test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)
                i += 5

            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*')

            test.log.info("7. Initiate the firmware download...")

            test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","ready","to update"\\s+')
            test.sleep(60)
            test.expect(test.dut.dstl_trigger_mods_firmware_update())
            test.dut.at1.wait_for(".*FOTA START.*Checksum OK.*", 5 * 60)
            test.dut.at1.wait_for(".*SYSSTART.*", 5 * 60)
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
            test.dut.at1.send_and_verify("AT^CICRET=SWN")

            test.log.info("Check whether the counter for fwdownload/deferLimit is reset to 5")
            print(test.dut.dstl_get_fwdownload_deferlimit())
            print(deferlimit)
            test.expect(test.dut.dstl_get_fwdownload_deferlimit() == str(deferlimit))
            test.expect(test.dut.dstl_get_fwupdate_deferlimit() == str(deferlimit))

        test.expect(test.dut.dstl_set_fwdownload_deferlimit("0"))
        test.expect(test.dut.dstl_set_fwupdate_deferlimit("0"))

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()

