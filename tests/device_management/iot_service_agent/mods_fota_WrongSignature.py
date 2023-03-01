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
from dstl.identification import get_imei
from dstl.internet_service.schedule_fota_from_mods_server import ModsServer


class Test(BaseTest):
    def setup(test):
        # # test.dut.dstl_restart()
        #         # test.dut.dstl_detect_comprehensive()
        #         # # test.access_server = "partners-mods.gemalto.io"
        #         # test.access_server = "https://partners-mods.gemalto.io"
        #         # test.access_server_port = ""
        #         # test.job_server = "partners-mods.gemalto.io"
        #         # test.job_server_port = ""
        #         # test.device_inquire_port = ""
        #         # test.organization = "root.Thales.Serval"
        #         # test.user = "wenyan.wu@thalesgroup.com"
        #         # test.password = "Mods,1234!"

        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        # test.access_server = "partners-mods.gemalto.io"
        test.access_server = "10.151.127.73"
        test.access_server_port = "8443"
        test.job_server = "10.151.127.74"
        test.job_server_port = "19280"
        test.device_inquire_port = "19170"
        test.organization = "root.SERVAL"
        test.user = "serval@gemalto.com"
        test.password = "mods,123"
        pass

    def run(test):
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.mods",
        #                          "serval@gemalto.com", "mods,123")

        mods_server_obj = ModsServer(test.access_server, test.access_server_port, test.job_server, test.job_server_port,
                                     test.device_inquire_port, test.organization, test.user, test.password)

        # mods_server_obj = ModsServer(test.access_server, test.organization, test.user, test.password)

        ############################################
        #Input parameters:
        test.target_package = "Serval_054EC_054ECA_INVALID"

        ############################################

        imei = test.dut.dstl_get_imei()

        test.log.info("*************************************")
        test.log.info("Start MODS FOTA  test.")
        test.log.info("*************************************")

        test.log.info("Target Firmware package: {}".format(test.target_package))

        if test.target_package:
            fota_job_name = "{}_{}_FOTA_Load_{}".format(getpass.getuser(),
                                                        time.strftime("%Y-%m-%d_%H:%M:%S"),
                                                        str(1).zfill(3))
            start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                        test.target_package,
                                                                        imei,
                                                                        start_time,
                                                                        end_time)
            mods_server_obj.dstl_check_fota_job_status(job_id)

            test.log.info("Wait for progress URC...")
            i = 5
            while i < 100:
                test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","progress","{}.*".*'.format(i), 5 * 60)
                i += 5

            test.dut.at1.wait_for('.*SRVACT: "MODS","fwdownload","status","download success".*', 5*60)

            test.dut.at1.wait_for(".*FOTA START.*Checksum Fail.*", 5 * 60)
        else:
            test.log.error("Fail to get the target Firmware package.")

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
