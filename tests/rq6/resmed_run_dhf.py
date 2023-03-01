# responsible hongwei.yin@thalesgroup.com
# location Dalian
# resmed all cases

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import NF_pre_config
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import uc_send_healthdata
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import set_reinit_flag
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import set_run_all
from tests.rq6.resmed_ehealth_downloadtasklist_normalflow import main_process as uc_download_tasklist
from tests.rq6.resmed_ehealth_downloadtasklist_normalflow import trigger_mqtt2
from tests.rq6.resmed_ehealth_updatemodule_nf import main_process as uc_update_module
from tests.rq6.resmed_ehealth_updateapplication_normalflow import trigger_sms
from tests.rq6.resmed_ehealth_updateapplication_normalflow import main_process as uc_update_application
from tests.rq6.resmed_ehealth_download_file_normal_flow import main_process as uc_download_file
from dstl.auxiliary import restart_module
from tests.rq6.resmed_ehealth_basic_with_different_sim import main_process as uc_basic_with_different_sim
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_a import \
    main_process as us_updatemodule_robustness_test_ef_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_a import main_process as us_downloadfile_exceptional_flow_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_a import setrethread as setrethread_flow_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_b import main_process as us_downloadfile_exceptional_flow_b
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_b import setrethread as setrethread_flow_b
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_c import main_process as us_downloadfile_exceptional_flow_c
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_b1 import \
    main_process as us_updatemodule_robustness_test_ef_b1
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_b2 import \
    main_process as us_updatemodule_robustness_test_ef_b2
from tests.rq6.resmed_ehealth_sendhealthdata_alternative_flow_a_exceptional_flow_a_b \
    import main_process as us_sendhealthdata_alternative_flow
from tests.rq6.resmed_ehealth_sendhealthdata_af_a import main_process as us_sendhealthdata_af_a
from tests.rq6.resmed_ehealth_sendhealthdata_stress import main_process as us_sendhealthdata_stress
from tests.rq6.resmed_ehealth_downloadfile_alternativeflow import main_process as us_downloadfile_af
from tests.rq6.resmed_ehealth_downloadfile_normalflow_stress_test import main_process as us_downloadfile_nf_stress
from tests.rq6.resmed_ehealth_initmodule_alternative_flow_b_c import main_process as us_initmodule_af_b_c
from tests.rq6.resmed_ehealth_initmodule_normal_flow import set_run_all as init_set_run_all
from tests.rq6.resmed_ehealth_initmodule_normal_flow import set_reinit_flag as init_set_reinit_flag
from tests.rq6.resmed_ehealth_shutdownmodule_stresstest import main_process as us_shutdownmodule_stress
from tests.rq6.resmed_ehealth_shut_down_module_normal_flow_stress_test import \
    main_process as us_shutdownmodule_nf_stress
import random


class Test(BaseTest):
    """
     Run all resmed test cases
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        uc_init_module(test, 1)

    def run(test):

        '''
        test.log.step("Run TC0107805.001 - Resmed_eHealth_SendHealthData_NF.")
        # test.ssh_server.close()
        # test.sleep(10)
        NF_pre_config(test)
        uc_send_healthdata(test, 1)

        test.log.step("Run TC0107852.001 - resmed_ehealth_sendhealthdata_alternative_flow_a_exceptional_flow_a_b.py.")
        test.ssh_server.close()
        test.sleep(10)
        set_run_all(True)
        us_sendhealthdata_alternative_flow(test)
        set_reinit_flag(False)
        set_run_all(False)

        test.log.step("Run TC0107851.001 - Resmed_eHealth_SendHealthData_AF_A.")
        test.ssh_server.close()
        test.sleep(10)
        us_sendhealthdata_af_a(test)

        test.log.step("Run TC0107806.001 - Resmed_eHealth_SendHealthData_Stress_Test.")
        test.ssh_server.close()
        test.sleep(10)
        us_sendhealthdata_stress(test)
        '''

        test.log.step("Run TC0107813.001 - Resmed_eHealth_DownloadFile_NormalFlow_StressTest.")
        # test.ssh_server.close()
        # test.sleep(10)
        us_downloadfile_nf_stress(test)

        # test.log.step("Run TC0107850.001 - Resmed_eHealth_InitModule_AF_B_C.")
        # init_set_run_all(True)
        # us_initmodule_af_b_c(test)
        # init_set_reinit_flag(False)
        # init_set_run_all(False)
        #
        # test.log.step("Run TC0107864.001 - Resmed_eHealth_ShutDownModule_StressTest.")
        # us_shutdownmodule_stress(test)
        #
        # test.log.step("Run TC0107812.001 - Resmed_eHealth_ShutDownModule_NormalFlow_StressTest.")
        # us_shutdownmodule_nf_stress(test)

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


def downgrade(test):
    if test.dut.software_number == "100_038":
        test.log.info("Start downgrade")
        test.expect(test.dut.at1.send_and_verify(
            'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.808_arn01.000.00_lynx_100_038_to_rev00.042_arn01.000.00_lynx_100_028b_resmed_prod02sign.usf"'))
        test.expect(test.dut.at1.send_and_verify(
            'at^snfota="CRC","852b7532d11eecb3f3a2d7a1e731a6d50cf7b93c5cc76bd4fabb77241379c42c"'))
        test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
        test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
        test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        test.sleep(5)
        dstl_detect(test.dut)
    else:
        pass


if __name__ == "__main__":
    unicorn.main()
