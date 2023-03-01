#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0105483.001 TC0105483.002 TpLwm2mFotaWithPPPConnection

import unicorn

import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.packet_domain import start_public_IPv4_data_connection
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification import get_imei
from dstl.internet_service.mods_server import ModsServer

class Test(BaseTest):
    def setup(test):
        # test.dut.dstl_restart()
        test.dut.dstl_detect_comprehensive()
        test.dstl_is_PDPShare_supported = True
        pass

    def run(test):
        #test.do_ppp_connect()
        #test.sleep(60)
        test.do_fota()
        test.do_ppp_connect()

        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
        #                          "serval@gemalto.com", "mods,123")
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.mods",
        #                              "serval@gemalto.com", "mods,123")

        # mods_server_obj = ModsServer()

        #
        # test.dut.dstl_register_to_network()
        # test.dut.at1.send_and_verify("AT+CREG=2")
        # test.dut.at1.send_and_verify("AT+CGREG=2")
        # imei = test.dut.dstl_get_imei()
        # test.target_package = mods_server_obj.dstl_get_fota_package()
        # test.target_firmware = mods_server_obj.dstl_get_target_firmware()
        # test.current_firmware = test.dut.software
        # test.original_firmware = test.dut.software
        #
        # if test.dut.dstl_check_mods_service_status():
        #     for i in range(0, 10):
        #         if test.dut.dstl_stop_mods_service():
        #             break
        #
        # test.sleep(60)
        #
        # for i in range(0, 10):
        #     if test.dut.dstl_start_mods_service():
        #         break
        #
        # # test.dut.dstl_register_to_nbiot()
        # # test.dut.at1.send_and_verify("AT+CREG=2")
        # # test.dut.at1.send_and_verify("AT+CGREG=2")
        #
        # test.log.info("*************************************")
        # test.log.info("Step1: Create and schedule FOTA job.")
        # test.log.info("*************************************")
        #
        # fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
        #                                             time.strftime("%Y-%m-%d_%H:%M:%S"))
        # start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        # job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
        #                                                             test.target_package,
        #                                                             imei,
        #                                                             start_time,
        #                                                             end_time)
        # mods_server_obj.dstl_check_job_status(job_id)
        #
        # test.log.info("*************************************")
        # test.log.info("Step2: Create PPP connection.")
        # test.log.info("*************************************")
        #
        # if test.dut.dstl_is_PDPShare_supported:
        #     test.log.info("Create PPP connection with the same APN.")
        #     test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup())
        # else:
        #     test.log.info("Create PPP connection with the different APN.")
        #     test.dut.at1.send_and_verify("AT+CGDCONT=2,\"IPV4V6\",\"{}\"".format(test.dut.sim.apn_v4_2nd))
        #     test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup())
        #
        # test.log.info("*************************************")
        # test.log.info("Step3: Wait till FW download finishes, close PPP connection.")
        # test.log.info("*************************************")
        #
        # if test.dut.at1.wait_for(".*download success.*", timeout=60 * 60):
        #     test.log.info("FW download success.")
        #     test.expect(True)
        # else:
        #     test.log.info("FW download failed.")
        #     test.expect(False)
        #
        # test.log.info("Close PPP connection.")
        # test.expect(test.dut.dstl_stop_public_ipv4_data_connection_over_dialup())
        #
        # test.log.info("Wait till update finishes.")
        # if test.dut.wait_for(".*update success.*", timeout=60*5):
        #     test.log.info("FW update success.")
        #     test.expect(True)
        # else:
        #     test.log.info("FW update failed.")
        #     test.expect(False)

    def cleanup(test):
        pass

    def do_fota(test):
        mods_server_obj = ModsServer()
        fota_package = mods_server_obj.dstl_get_fota_package()
        target_firmware = mods_server_obj.dstl_get_target_firmware()
        imei = test.dut.dstl_get_imei()

        # test.log.info("Current Software version: {}".format(test.current_firmware))
        test.log.info("Target Software version: {}".format(target_firmware))
        test.log.info("Target Firmware package: {}".format(fota_package))

        if test.target_package:
            fota_job_name = "{}_{}_FOTA_CATM_{}".format(getpass.getuser(),
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
            test.dut.at1.wait_for('.*SRVACT: "MODS","fwupdate","status","update success".*')
            test.dut.dstl_detect_comprehensive()
            current_firmware = test.dut.software
            if current_firmware in test.target_firmware:
                test.log.info("FOTA success")
                test.expect(True)
            else:
                test.log.info("FOTA fail")
                test.expect(False)

            test.log.info("Make sure the job status will not affect the next round FOTA...")
            mods_server_obj.dstl_disable_job(job_id)
        else:
            test.log.error("Fail to get the target Firmware package.")

    def do_ppp_connect(test):
        if test.dstl_is_PDPShare_supported:
            test.log.info("Create PPP connection with the same APN.")
            # test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup())
            #test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2", "DialupUsb")
            test.dut.at2.dstl_start_public_ipv4_data_connection_over_dialup(test, "DialupUsb")
            test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2", "DialupUsb")
        else:
            test.log.info("Create PPP connection with the different APN.")
            test.dut.at1.send_and_verify("AT+CGDCONT=2,\"IPV4V6\",\"{}\"".format(test.dut.sim.apn_v4_2nd))
            test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2", "dialup_2nd_apn",
                                                                                 "*99***2#")
            # test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup())


if __name__ == "__main__":
    unicorn.main()
