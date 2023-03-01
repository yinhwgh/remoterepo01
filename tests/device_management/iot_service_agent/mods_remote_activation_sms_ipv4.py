#responsible: yafan.liu@thalesgroup.com
#location: Beijing
#TC0104417.001 TC0104417.002 TpLwm2mRemoteActivationSMSIpv4

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
        pass

    def run(test):

        test.log.info("Register to network.")
        test.dut.dstl_register_to_network()
        test.dut.at1.send_and_verify("AT+CREG=2")
        test.dut.at1.send_and_verify("AT+CGREG=2")
        test.sleep(30)

        test.log.info("*************************************")
        test.log.info("Step1: Trigger SMS activation job on Mods server.")
        test.log.info("*************************************")

        test.sms_activation()
        if test.checking_status():
            test.log.info("Client is running.")
            test.expect(True)
        else:
            test.log.info("Client is not running.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step2: Trigger SMS activation job on Mods server again.")
        test.log.info("*************************************")

        test.sms_activation()
        if test.checking_status():
            test.log.info("Client is running.")
            test.expect(True)
        else:
            test.log.info("Client is not running.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step3: Stop lwm2m client.")
        test.log.info("*************************************")

        if test.dut.at1.send_and_verify("at^srvctl=\"MODS\",stop", ".*OK.*"):
            test.log.info("lwm2m client stoped.")
            test.expect(True)
        else:
            test.log.info("lwm2m client stop failed.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step4: Trigger SMS activation job on Mods server.")
        test.log.info("*************************************")

        test.sms_activation()
        if test.checking_status():
            test.log.info("Client is running.")
            test.expect(True)
        else:
            test.log.info("Client is not running.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step5: Trigger SMS activation job on Mods server again.")
        test.log.info("*************************************")

        test.sms_activation()
        if test.checking_status():
            test.log.info("Client is running.")
            test.expect(True)
        else:
            test.log.info("Client is not running.")
            test.expect(False)

        test.log.info("*************************************")
        test.log.info("Step6: Stop lwm2m client.")
        test.log.info("*************************************")

        if test.dut.at1.send_and_verify("at^srvctl=\"MODS\",stop", ".*OK.*"):
            test.log.info("lwm2m client stoped.")
            test.expect(True)
        else:
            test.log.info("lwm2m client stop failed.")
            test.expect(False)

    def sms_activation(test):
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
        #                              "serval@gemalto.com", "mods,123")
        mods_server_obj = ModsServer()
        # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.mods",
        #                              "serval@gemalto.com", "mods,123")

        ############################################
        imei = test.dut.dstl_get_imei()
        #test.dut.dstl_add_msisdn_to_device(self, product, imei, msisdn)
        sms_activation_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                                    time.strftime("%Y-%m-%d_%H:%M:%S"))
        start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        job_id = mods_server_obj.dstl_trigger_sms_activation_from_mods_server(sms_activation_job_name,
                                                                    imei,
                                                                    start_time,
                                                                    end_time)
        mods_server_obj.dstl_check_job_status(job_id)

    def checking_status(test):
        test.log.info("Check client running status.")
        if test.dut.at1.send_and_verify("at^srvctl=\"MODS\",status", ".*service is running.*"):
            # test.log.info("Client is running.")
            return True
        else:
            # test.log.info("Client is not running.")
            return False

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()