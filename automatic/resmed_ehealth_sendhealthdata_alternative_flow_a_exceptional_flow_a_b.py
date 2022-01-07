# responsible: haofeng.dding@thalesgroup.com
# location: Dalian
# TC0107851.001&TC0107852.001
# Hints:
# ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
# apn should be defined in local.cfg currently,shuch as apn="internet"
# The SIM card should not with PIN
import unicorn
import time
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_adjust_clock_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import resmed_ehealth_initmodule_normal_flow
from tests.rq6 import resmed_ehealth_sendhealthdata_normal_flow

class Test(BaseTest):
    def setup(test):
        test.log.step('Init the module first')
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def run(test):
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        NF01_goto_EF_A_restart(test)
        Set_re_init_flag(test)
        test.ssh_server.close()
        test.sleep(10)
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        NF02_goto_EF_A_restart(test)
        Set_re_init_flag(test)
        test.ssh_server.close()
        test.sleep(10)
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        NF03_goto_EF_A_restart(test)
        Set_re_init_flag(test)
        test.ssh_server.close()
        test.sleep(10)
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        NF04_goto_EF_A_restart(test)
        Set_re_init_flag(test)
        test.ssh_server.close()
        test.sleep(10)
        resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test)
        NF05_goto_EF_A_restart(test)
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

def NF01_goto_EF_A_restart(test):
    test.log.step('***** NF01_goto_EF_A flow start *****')
    test.expect(resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test,1,1))
    test.log.step('***** NF01_goto_EF_A flow end *****')

def NF02_goto_EF_A_restart(test):
    test.log.step('***** NF02_goto_EF_A flow start *****')
    test.expect(resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test,1,2))
    test.log.step('***** NF02_goto_EF_A flow end *****')

def NF03_goto_EF_A_restart(test):
    test.log.step('***** NF03_goto_EF_A flow start *****')
    test.expect(resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test,1,3))
    test.log.step('***** NF03_goto_EF_A flow end *****')

def NF04_goto_EF_A_restart(test):
    test.log.step('***** NF04_goto_EF_A flow start *****')
    test.expect(resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test,1,4))
    test.log.step('***** NF04_goto_EF_A flow end *****')

def NF05_goto_EF_A_restart(test):
    test.log.step('***** NF05_goto_EF_A flow start *****')
    test.expect(resmed_ehealth_sendhealthdata_normal_flow.uc_send_healthdata(test,1,5))
    test.log.step('***** NF05_goto_EF_A flow end *****')

def Set_re_init_flag(test):
    test.log.step('***** Set the re_init_flag to False *****')
    resmed_ehealth_sendhealthdata_normal_flow.set_reinit_flag(False)

if "__main__" == __name__:
    unicorn.main()