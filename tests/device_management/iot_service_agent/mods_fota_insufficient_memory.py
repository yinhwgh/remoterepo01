# responsible: yafan.liu@thalesgroup.com
# location: Beijing
# TC0104367.001

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
        # test.access_server = "https://partners-mods.gemalto.io"
        # test.access_server_port = ""
        # test.job_server = "partners-mods.gemalto.io"
        # test.job_server_port = ""
        # test.device_inquire_port = ""
        # test.organization = "root.Thales.Serval"
        # test.user = "wenyan.wu@thalesgroup.com"
        # test.password = "Mods,1234!"
        pass

    def run(test):
        mods_server_obj = ModsServer()
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
        #                              "serval@gemalto.com", "mods,123")

        # mods_server_obj = ModsServer(test.access_server, test.access_server_port, test.job_server, test.job_server_port,
        #                              test.device_inquire_port, test.organization, test.user, test.password)

        # mods_server_obj = ModsServer(test.access_server, test.organization, test.user, test.password)

        ############################################
        #Input parameters:
        # test.current_firmware = "SERVAL_100_054G"
        # test.target_package = "EXS82_054EC_FULL"

        ############################################

        imei = test.dut.dstl_get_imei()
        test.dut.dstl_register_to_network()
        test.dut.at1.send_and_verify("AT+CREG=2")
        test.dut.at1.send_and_verify("AT+CGREG=2")

        # test.log.info("Current Software version: {}".format(test.current_firmware))

        fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                                    time.strftime("%Y-%m-%d_%H:%M:%S"))
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                    test.upgrade_fota_big_size_package_name,
                                                                    imei,
                                                                    start_time,
                                                                    end_time)
        mods_server_obj.dstl_check_job_status(job_id)
        if test.dut.at1.wait_for(".*not enough space.*", timeout=60*5):
            test.log.info("not enough space")
            test.dut.dstl_detect_comprehensive()
            # current_firmware = test.dut.software
            test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software))
            test.expect(True)
        else:
            test.log.info("not enough space URC has not received")
            test.expect(False)

    def cleanup(test):
        pass

if __name__ == "__main__":
    unicorn.main()