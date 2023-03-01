# responsible hongwei.yin@thalesgroup.com
# location Dalian
# ebs all cases

import unicorn
from core.basetest import BaseTest
from tests.rq6.ebs_alarmdevice_checknetwork_nf import main_process as us_checknetwork_nf
from tests.rq6.ebs_alarmdevice_checknetwork_errorhanding_b import main_process as us_checknetwork_errorhanding_b
from tests.rq6.ebs_alarmdevice_checknetwork_errorhanding_c import main_process as us_checknetwork_errorhanding_c
from tests.rq6.ebs_alarmdevice_checknetwork_errorhanding_d import main_process as us_checknetwork_errorhanding_d
from tests.rq6.ebs_alarmdevice_updateapplication_nf import main_process as us_updateapplication_nf
from tests.rq6.ebs_alarmdevice_updateapplication_b_c_d import main_process as us_updateapplication_b_c_d
from tests.rq6.ebs_alarmdevice_receiveconfigration_nf import main_process as us_receiveconfigration_nf
from tests.rq6.ebs_alarmdevice_receiveconfigration_errorhanding_b_c_d import main_process as us_receiveconfigration_errorhanding_b_c_d
from tests.rq6.ebs_alarmdevice_sendreport_nf import main_process as us_sendreport_nf
from tests.rq6.ebs_alarmdevice_sendheartbeat_nf import main_process as us_sendheartbeat_nf
from tests.rq6.ebs_alarmdevice_sendalarm_nf import main_process as us_sendalarm_nf
from tests.rq6.ebs_alarmdevice_sendreport_ef_b import main_process as us_sendreport_ef_b
from tests.rq6.ebs_alarmdevice_sendreport_ef_c_d import main_process as us_sendreport_ef_c_d
from tests.rq6.ebs_alarmdevice_sendreport_nf import set_run_all as sendreport_set_run_all
from tests.rq6.ebs_alarmdevice_sendreport_nf import set_reinit_flag as sendreport_set_reinit_flag
from tests.rq6.ebs_alarmdevice_sendheartbeat_nf import set_run_all as sendheartbeat_set_run_all
from tests.rq6.ebs_alarmdevice_sendheartbeat_nf import set_reinit_flag as sendheartbeat_set_reinit_flag
from tests.rq6.ebs_alarmdevice_sendheartbeat_ef_b import main_process as us_sendheartbeat_ef_b
from tests.rq6.ebs_alarmdevice_sendheartbeat_ef_c_d import main_process as us_sendheartbeat_ef_c_d
from tests.rq6.ebs_alarmdevice_sendalarm_nf import set_run_all as sendalarm_set_run_all
from tests.rq6.ebs_alarmdevice_sendalarm_nf import set_reinit_flag as sendalarm_set_reinit_flag
from tests.rq6.ebs_alarmdevice_sendalarm_ef_b import main_process as us_sendalarm_ef_b
from tests.rq6.ebs_alarmdevice_sendalarm_ef_c import main_process as us_sendalarm_ef_c


class Test(BaseTest):
    """
     Run all ebs test cases
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("Run TC0108042.001 - EBS_AlarmDevice_CheckNetwork_NF.")
        us_checknetwork_nf(test)

        test.log.step("Run TC0108051.001 - EBS_AlarmDevice_CheckNetwork_ErrorHandling_B.")
        us_checknetwork_errorhanding_b(test)

        test.log.step("Run TC0108053.001 - EBS_AlarmDevice_CheckNetwork_ErrorHandling_C.")
        us_checknetwork_errorhanding_c(test)

        test.log.step("Run TC0108054.001 - EBS_AlarmDevice_CheckNetwork_ErrorHandling_D.")
        us_checknetwork_errorhanding_d(test)

        test.log.step("Run TC0108058.001 - EBS_AlarmDevice_UpdateApplication_NF.")
        us_updateapplication_nf(test)

        test.log.step("Run TC0108060.001 - EBS_AlarmDevice_UpdateApplication_B_C_D.")
        us_updateapplication_b_c_d(test)

        test.log.step("Run TC0108055.001 - EBS_AlarmDevice_ReceiveConfigration_NF.")
        us_receiveconfigration_nf(test)

        test.log.step("Run TC0108059.001 - EBS_AlarmDevice_ReceiveConfigration_ErrorHandling_B_C_D.")
        us_receiveconfigration_errorhanding_b_c_d(test)

        test.log.step("Run TC0108049.001 - EBS_AlarmDevice_SendReport_NF.")
        us_sendreport_nf(test)

        test.log.step("Run TC0108050.001 - EBS_AlarmDevice_SendReport_EF_B.")
        sendreport_set_run_all(True)
        us_sendreport_ef_b(test)
        sendreport_set_reinit_flag(False)
        sendreport_set_run_all(False)

        test.log.step("Run TC0108052.001 - EBS_AlarmDevice_SendReport_EF_C_D.")
        sendreport_set_run_all(True)
        us_sendreport_ef_c_d(test)
        sendreport_set_reinit_flag(False)
        sendreport_set_run_all(False)

        test.log.step("Run TC0108046.001 - EBS_AlarmDevice_SendHeartBeat_NF.")
        us_sendheartbeat_nf(test)

        test.log.step("Run TC0108047.001 - EBS_AlarmDevice_SendHeartBeat_EF_B.")
        sendheartbeat_set_run_all(True)
        us_sendheartbeat_ef_b(test)
        sendheartbeat_set_reinit_flag(False)
        sendheartbeat_set_run_all(False)

        test.log.step("Run TC0108048.001 - EBS_AlarmDevice_SendHeartBeat_EF_C_D.")
        sendheartbeat_set_run_all(True)
        us_sendheartbeat_ef_c_d(test)
        sendheartbeat_set_reinit_flag(False)
        sendheartbeat_set_run_all(False)

        test.log.step("Run TC0108043.001 - EBS_AlarmDevice_SendAlarm_NF.")
        us_sendalarm_nf(test)

        test.log.step("Run TC0108044.001 - EBS_AlarmDevice_SendAlarm_EF_B.")
        sendalarm_set_run_all(True)
        us_sendalarm_ef_b(test)
        sendalarm_set_reinit_flag(False)
        sendalarm_set_run_all(False)

        test.log.step("Run TC0108045.001 - EBS_AlarmDevice_SendAlarm_EF_C.")
        sendalarm_set_run_all(True)
        us_sendalarm_ef_c(test)
        sendalarm_set_reinit_flag(False)
        sendalarm_set_run_all(False)

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
