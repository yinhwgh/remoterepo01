# responsible: haofeng.ding@thalesgroup.com
# location: Dalian
# TC0107806.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
# The SIM card should not with PIN
import unicorn
import time
from core.basetest import BaseTest
from tests.rq6 import resmed_ehealth_initmodule_normal_flow
from tests.rq6 import resmed_ehealth_sendhealthdata_normal_flow


class Test(BaseTest):
    """
     TC0107806.001-Resmed_eHealth_SendHealthData_Stress_Test
    """

    def setup(test):
        test.log.step('Init the module first')
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def run(test):
        main_process(test)

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


def main_process(test):
    for i in range(100):
        time_start = time.time()
        test.log.info("begin loop {} times".format(i))
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test, 1)
        time_end = time.time()
        every_loop_time = time_end - time_start
        test.log.info('loop {} times cost is {}'.format(i, every_loop_time))
        if every_loop_time > 300:
            test.log.info('last loop time cost more than 300s , directly go to next loop')
            pass
        else:
            test.log.info("need to sleep {}".format(300 - every_loop_time))
            test.sleep(300 - every_loop_time)


if "__main__" == __name__:
    unicorn.main()