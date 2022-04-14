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
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_a import main_process as us_updatemodule_robustness_test_ef_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_a import main_process as us_downloadfile_exceptional_flow_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_a import setrethread as setrethread_flow_a
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_b import main_process as us_downloadfile_exceptional_flow_b
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_b import setrethread as setrethread_flow_b
from tests.rq6.resmed_ehealth_downloadfile_exceptional_flow_c import main_process as us_downloadfile_exceptional_flow_c
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_b1 import main_process as us_updatemodule_robustness_test_ef_b1
from tests.rq6.resmed_ehealth_updatemodule_robustness_test_ef_b2 import main_process as us_updatemodule_robustness_test_ef_b2
from tests.rq6.resmed_ehealth_sendhealthdata_alternative_flow_a_exceptional_flow_a_b \
    import main_process as us_sendhealthdata_alternative_flow
from tests.rq6.resmed_ehealth_sendhealthdata_af_a import main_process as us_sendhealthdata_af_a
from tests.rq6.resmed_ehealth_sendhealthdata_stress import main_process as us_sendhealthdata_stress
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
        test.log.step("Run TC0107810.001-Resmed_eHealth_DownloadTaskList_NormalFlow.")
        trigger_mqtt2(test)
        NF_pre_config(test)
        uc_download_tasklist(test)

        test.log.step("Run TC0107805.001 - Resmed_eHealth_SendHealthData_NF.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        uc_send_healthdata(test, 1)

        test.log.step("Run TC0107807.001 - Resmed_eHealth_UpdateModule_NF.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        uc_update_module(test)

        test.log.step("Run TC0107808.001 - Resmed_eHealth_UpdateApplication_NormalFlow.")
        uc_init_module(test, 1)
        # test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK\r\n', timeout=5, handle_errors=True))
        trigger_sms(test)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        uc_update_application(test)

        test.log.step("Run TC0107796.001 - Resmed_eHealth_DownloadFile_NormalFlow.")
        test.ssh_server.close()
        test.sleep(10)
        uc_download_file(test)

        test.log.step("Run TC0107792.001 - Resmed_eHealth_DisableFlightMode_NormalFlow.")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=4', 'OK\r\n'))
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=off', 'OK', wait_for='OK'))
        test.sleep(1)
        test.expect(test.dut.devboard.send_and_verify('MC:VBATT=on', 'OK', wait_for='OK'))
        test.expect(test.dut.devboard.send_and_verify('MC:igt=10', 'OK', wait_for='OK'))
        test.sleep(1.5)
        test.expect(uc_init_module(test, 1))

        test.log.step("Run TC0107795.001 - Resmed_eHealth_ShutDownModule_NormalFlow.")
        test.log.step("1. Enable GPIO FSR")
        test.dut.dstl_turn_off_dev_board_urcs()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "GPIO/mode/FSR",std', 'OK'))
        test.dut.dstl_set_urc(urc_str="PWRIND")
        # change takes effect after restart module
        test.dut.dstl_restart()
        test.sleep(10)
        test.log.step("2. Triggers the module's fast shutdown line once a main's voltage drop is detected")
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_for='OK'))
        test.dut.devboard.send('mc:gpio3cfg=0')
        test.expect(test.dut.devboard.wait_for('>URC:  PWRIND: 1'))
        test.dut.devboard.send('MC:VBATT=OFF')
        test.log.step("3. Power off supply after 15ms fast shutdown"
                      "(.ie if the power can hold more then 15ms after shutdown the test will be fail)")
        test.sleep(1)
        test.dut.devboard.send('mc:gpio3cfg=1')
        test.dut.devboard.send('MC:VBATT=ON')
        test.expect(test.dut.devboard.send_and_verify("MC:IGT=1000", ".*SYSSTART.*", wait_for=".*SYSSTART.*"))
        test.dut.devboard.send_and_verify('mc:pwrind?')
        test.sleep(10)

        test.log.step("Run TC0107811.001 - Resmed_eHealth_basic_with_different_SIM.")
        test.ssh_server.close()
        test.sleep(10)
        uc_basic_with_different_sim(test)

        test.log.step("Run TC0107809.001 - Resmed_eHealth_UpdateModule_Robustness_Test_EF_A.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_a(test)
        test.log.info("Softreset the module (AT+CFUN=1,1).")
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        test.ssh_server.close()
        test.sleep(10)
        test.log.step("Initialize the module.")
        uc_init_module(test, 1)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_a(test)
        test.log.step("10. Trigger the firmware swap process.")
        test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        test.log.step("11. Check the module's SW version.")
        test.sleep(5)
        dstl_detect(test.dut)
        test.expect(test.dut.software_number == "100_032")

        test.log.step("Run TC0107798.001 - Resmed_eHealth_DownloadFile_ExceptionalFlow_A.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 1.")
        us_downloadfile_exceptional_flow_a(test, 1)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 2.")
        us_downloadfile_exceptional_flow_a(test, 2)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        setrethread_flow_a(True)
        test.log.step("Begin exceptional_flow step 3.")
        us_downloadfile_exceptional_flow_a(test, 3)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 4.")
        us_downloadfile_exceptional_flow_a(test, 4)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 5.")
        us_downloadfile_exceptional_flow_a(test, 5)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 6.")
        us_downloadfile_exceptional_flow_a(test, 6)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 7.")
        us_downloadfile_exceptional_flow_a(test, 7)

        test.log.step("Run TC0107800.001 - Resmed_eHealth_DownloadFile_ExceptionalFlow_B.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 1.")
        us_downloadfile_exceptional_flow_b(test, 1)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 2.")
        us_downloadfile_exceptional_flow_b(test, 2)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        setrethread_flow_b(True)
        test.log.step("Begin exceptional_flow step 3.")
        us_downloadfile_exceptional_flow_b(test, 3)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 4.")
        us_downloadfile_exceptional_flow_b(test, 4)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 5.")
        us_downloadfile_exceptional_flow_b(test, 5)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 6.")
        us_downloadfile_exceptional_flow_b(test, 6)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 7.")
        us_downloadfile_exceptional_flow_b(test, 7)

        test.log.step("Run TC0107802.001 - Resmed_eHealth_DownloadFile_ExceptionalFlow_C.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow_c.")
        us_downloadfile_exceptional_flow_c(test)

        test.log.step("Run TC0107853.001 - Resmed_eHealth_UpdateModule_Robustness_Test_EF_B1.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_b1(test)
        test.sleep(random.randint(15, 30))
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_after_send=3))
        test.log.info("fast shutdown pulled to GND for 20ms")
        test.dut.devboard.send('mc:gpio3cfg=1')
        test.dut.devboard.send('mc:gpio3cfg=0')
        test.sleep(2)  # can not ignition after 20ms
        test.dut.devboard.send_and_verify('mc:igt=1000', 'OK')
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        test.ssh_server.close()
        test.sleep(10)
        test.log.step("Initialize the module.")
        uc_init_module(test, 1)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_b1(test)
        download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
        if download_succeed:
            test.log.info("downlaod successfully")
        else:
            test.expect(False, critical=True)
        test.log.step("10. Trigger the firmware swap process.")
        test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        test.log.step("11. Check the module's SW version.")
        test.sleep(5)
        dstl_detect(test.dut)
        test.expect(test.dut.software_number == "100_032")

        test.log.step("Run TC0107855.001 - Resmed_eHealth_UpdateModule_Robustness_Test_EF_B2.")
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_b2(test)
        test.sleep(random.randint(15, 30))
        test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_after_send=3))
        test.log.info("fast shutdown pulled to GND for 20ms")
        test.dut.devboard.send('mc:gpio3cfg=1')
        test.dut.devboard.send('mc:gpio3cfg=0')
        test.sleep(2)  # can not ignition after 20ms
        test.dut.devboard.send_and_verify('mc:igt=1000', 'OK')
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        test.ssh_server.close()
        test.sleep(10)
        test.log.step("Initialize the module.")
        uc_init_module(test, 1)
        NF_pre_config(test)
        us_updatemodule_robustness_test_ef_b2(test)
        download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
        if download_succeed:
            test.log.info("downlaod successfully")
        else:
            test.expect(False, critical=True)
        test.log.step("10. Trigger the firmware swap process.")
        test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        test.log.step("11. Check the module's SW version.")
        test.sleep(5)
        dstl_detect(test.dut)
        test.expect(test.dut.software_number == "100_032")

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


    def cleanup(test):
        if test.dut.software_number == "100_032":
            test.log.info("Start downgrade")
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.802_arn01.000.00_lynx_100_032_to_rev00.800_arn01.000.00_lynx_100_030_prod02sign.usf"'))
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="CRC","4ee9a59764736e05efa14ef24eec8573a3e126a6a46e4fac41bc83cb617ac0d4"'))
            test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
            test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
            test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
            test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
            test.sleep(5)
            dstl_detect(test.dut)
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


if __name__ == "__main__":
    unicorn.main()
