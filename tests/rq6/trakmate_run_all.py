# responsible hongwei.yin@thalesgroup.com
# location Dalian
# trakmate all cases

import unicorn
from core.basetest import BaseTest
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from tests.rq6 import trakmate_trackingunit_updatemoduleIotsuite_nf03 as uc_updatemoduleIotsuite_nf03
from tests.rq6 import trakmate_trackingunit_updatemodule_ef01 as uc_updatemodule_ef01
from tests.rq6 import trakmate_trackingunit_updatemodule_ef02 as uc_updatemodule_ef02
from tests.rq6 import trakmate_send_alert_normal_flow as uc_send_alert_nf
from tests.rq6 import trakmate_download_config_normal_flow as uc_download_config_nf
from tests.rq6 import trakmate_update_module_nf_1 as uc_update_module_nf_1
from tests.rq6 import trakmate_update_module_nf_2 as uc_update_module_nf_2
from tests.rq6 import trakmate_update_application_normal_flow as uc_update_application_nf
from tests.rq6 import trakmate_update_application_exceptional_flow as uc_update_application_ef
from tests.rq6 import trakmate_switch_sim_profile_normal_flow as uc_switch_sim_profile_nf
from tests.rq6 import trakmate_send_trackingdata_normal_flow as uc_send_trackingdata_nf
from tests.rq6.trakmate_send_trackingdata_loadtest_nf import main_process as uc_send_trackingdata_loadtest_nf
from tests.rq6.trakmate_send_notification_normal_flow import main_process as uc_send_notification_nf





class Test(BaseTest):
    """
     Run all trakmate test cases
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_enter_pin()
        test.r1.dstl_enter_pin()
        test.expect(test.dut.at1.send_and_verify('AT^SCFG= "GPIO/mode/FSR",std', 'OK'))
        test.r1.dstl_select_sms_message_format('Text')
        test.r1.dstl_configure_sms_event_reporting("2", "1")
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        # test.log.step("Run TC0107882.001 - Trakmate_TrackingUnit_UpdateModuleIotSuite_NF03.")
        # # uc_updatemoduleIotsuite_nf03.whole_flow(test, uc_updatemoduleIotsuite_nf03.step_list)
        #
        # test.log.step("Run TC0107883.001 - Trakmate_TrackingUnit_UpdateModule_EF01.")
        # uc_updatemodule_ef01.whole_flow(test, uc_updatemodule_ef01.step_list1)
        # uc_updatemodule_ef01.whole_flow(test, uc_updatemodule_ef01.step_list2)
        # uc_updatemodule_ef01.whole_flow(test, uc_updatemodule_ef01.step_list1)
        # uc_updatemodule_ef01.whole_flow(test, uc_updatemodule_ef01.step_list3)
        #
        # test.log.step("Run TC0107884.001 - Trakmate_TrackingUnit_UpdateModule_EF02.")
        # uc_updatemodule_ef02.whole_flow(test, uc_updatemodule_ef02.step_list1)
        # uc_updatemodule_ef02.whole_flow(test, uc_updatemodule_ef02.step_list2)
        # uc_updatemodule_ef02.whole_flow(test, uc_updatemodule_ef02.step_list1)
        # uc_updatemodule_ef02.whole_flow(test, uc_updatemodule_ef02.step_list3)
        #
        # test.log.step("Run TC0107880.001 - Trakmate_TrackingUnit_UpdateModuleFOTA_NF01.")
        # uc_update_module_nf_1.whole_flow(test, False)
        #
        # test.log.step("Run TC0107881.001 - Trakmate_TrackingUnit_UpdateModuleFOTA_NF02.")
        # uc_update_module_nf_2.whole_flow(test, False)
        #
        # test.log.step("Run TC0107845.001 - Trakmate_TrackingUnit_SwitchSimProfile_NormalFlow.")
        # uc_switch_sim_profile_nf.whole_flow(test, uc_switch_sim_profile_nf.step_list)

        # ===============================================================================

        test.log.step("Run TC0107873.001 - Trakmate_TrackingUnit_SendAlert_NF.")
        uc_send_alert_nf.whole_flow(test, uc_send_alert_nf.step_list)

        test.log.step("Run TC0107874.001 - Trakmate_TrackingUnit_SendAlert_EF.")
        for i in range(1, 4):
            test.log.info(f'Start check when occur error happen in step{i}')
            uc_send_alert_nf.whole_flow(test, uc_send_alert_nf.step_list, fail_step=i)

        test.log.step("Run TC0107854.001 - Trakmate_TrackingUnit_DownLoadConfiguration_NormalFlow.")
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list)

        test.log.step("Run TC0107861.001 - Trakmate_TrackingUnit_DownLoadConfiguration_ExceptionalFLow.")
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list, fail_step=2)
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list, fail_step=8)
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list, fail_step=9)
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list, fail_step=10)
        uc_download_config_nf.whole_flow(test, uc_download_config_nf.step_list, fail_step=11)

        test.log.step("Run TC0107862.001 - Trakmate_TrackingUnit_UpdateApplication_NormalFlow.")
        uc_update_application_nf.whole_flow(test)

        test.log.step("Run TC0107863.001 - Trakmate_TrackingUnit_UpdateApplication_ExceptionalFlow.")
        uc_update_application_ef.whole_flow(test)

        test.log.step("Run TC0107875.001 - Trakmate_TrackingUnit_SendTrackingData_NF.")
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list)

        test.log.step("Run TC0107876.001 - Trakmate_TrackingUnit_SendTrackingData_TCP_EF01.")
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=8)
        # uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=9)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=10)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=11)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=12)

        test.log.step("Run TC0107877.001 - Trakmate_TrackingUnit_SendTrackingData_HTTP_EF02.")
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=18)
        # uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=19)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=20)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=21)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=22)

        test.log.step("Run TC0107878.001 - Trakmate_TrackingUnit_SendTrackingData_MQTT_EF03.")
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=30)
        # uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=32)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=33)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=34)
        uc_send_trackingdata_nf.whole_flow(test, uc_send_trackingdata_nf.step_list, fail_step=35)

        test.log.step("Run TC0107879.001 - Trakmate_TrackingUnit_SendTrackingData_LoadTest_NF.")
        uc_send_trackingdata_loadtest_nf(test)

        test.log.step("Run TC0107865.001 - Trakmate_TrackingUnit_SendNotification_NormalFlow.")
        uc_send_notification_nf(test)

        test.log.step("Run TC0107872.001 - Trakmate_TrackingUnit_InitModule_EF.")
        for i in range(1, 36):
            test.log.info(f'Start check when occur error happen in step{i}')
            uc_init.whole_flow(test, uc_init.step_list, fail_step=i)

    def cleanup(test):
        # if test.dut.software_number == "100_050":
        #     test.log.info("Start downgrade")
        #     test.expect(test.dut.at1.send_and_verify('at^snfota="conid",1'))
        #     test.expect(test.dut.at1.send_and_verify(f'at^snfota="url","{test.downgrade_sw_url}"'))
        #     test.expect(test.dut.at1.send_and_verify(f'at^snfota="CRC","{test.downgrade_sw_crc}"'))
        #     test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
        #     test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
        #     test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
        #     test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
        #     test.sleep(5)
        #     dstl_detect(test.dut)
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
