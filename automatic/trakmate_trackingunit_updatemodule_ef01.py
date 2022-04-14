# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107883.001
import time

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.sms import configure_sms_text_mode_parameters, select_sms_format
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.init import dstl_detect
import random

timex = time.time()
stop_run = False
address_1 = 'http://114.55.6.216:10080/test.bin'
address_3 = 'mqtt://114.55.6.216:2020'
step_list1 = ['NF_1_set_apn', 'NF_2_activate_internet_connection_http', 'NF_3_config_server_type_http',
              'NF_4_config_service_conid_http', 'NF_5_config_service_address_http', 'NF_6_config_service_hcmethod_get',
              'NF_7_config_service_parameter', 'NF_8_open_internet_service_http', 'NF_9_wait_for_sisr',
              'NF_10_read_from_server', 'NF_11_close_internet_service_http', 'NF_12_config_module_with_snfota',
              'NF_13_download_module_with_snfota']

step_list2 = ['NF_14_monitor_download_progress', 'NF_15_power_off', 'NF_16_power_on_and_init',
              'NF_17_send_alert_message', 'NF_18_set_sms_format', 'NF_19_send_sms_to_r1',
              'NF_20_check_sms_receive']

step_list3 = ['NF_21_trigger_fw_swap', 'NF_22_wait_for_systart', 'NF_23_check_firmware',
              'NF_24_init_module', 'NF_25_config_server_type_mqtt', 'NF_26_config_service_conid_mqtt',
              'NF_27_config_service_address_mqtt', 'NF_28_config_service_hcmethod_publish',
              'NF_29_config_service_client_id_mqtt',
              'NF_30_config_service_topic_mqtt', 'NF_31_activate_internet_connection_mqtt',
              'NF_32_open_internet_service_mqtt',
              'NF_33_set_dns_ttl_zero', 'NF_34_wait_for_sisw', 'NF_35_send_tracking_data',
              'NF_36_check_data', 'NF_37_close_internet_service_mqtt']


class Test(BaseTest):
    """
     TC0107883.001 - Trakmate_TrackingUnit_UpdateModule_EF01
     This case mainly test RQ6000082.001 normal flow
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
        whole_flow(test, step_list1)
        whole_flow(test, step_list2)
        whole_flow(test, step_list1)
        whole_flow(test, step_list3)

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
        else:
            pass


def whole_flow(test, test_step_list, fail_step=0, restart_step=1):
    global stop_run
    # stop_run = False

    for i in range(len(test_step_list)):
        if not stop_run:
            if restart_step > i + 1:
                continue
            elif f'NF_{fail_step}_' in test_step_list[i]:
                eval(test_step_list[i])(test, True)
                break
            else:
                eval(test_step_list[i])(test, False)
        else:
            test.log.info('Test Case finished.')


def error_handle_1(test):
    test.log.info('Start Error handle step')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART', 34))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    test.run()


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_1_set_apn(test, force_abnormal_flow=False):
    if test.dut.sim.apn_v4 == 'None':
        apn = 'test1'
    else:
        apn = test.dut.sim.apn_v4
    return test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,IPV4V6,{apn}', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_2_activate_internet_connection_http(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SICA=1,1", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_3_config_server_type_http(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvType","http"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_4_config_service_conid_http(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conid","1"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_5_config_service_address_http(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify(f'AT^SISS=1,"address","{address_1}"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_6_config_service_hcmethod_get(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd","get"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_7_config_service_parameter(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify('AT^SISS=1,"hcProp","Content-Type: \'text/plain\'"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_8_open_internet_service_http(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SISO=1", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_9_wait_for_sisr(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.wait_for('^SISR: 1,1', 20))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_10_read_from_server(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SISR=1,1000", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_11_close_internet_service_http(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SISC=1", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_12_config_module_with_snfota(test, force_abnormal_flow=False):
    test.expect(test.dut.at1.send_and_verify('at^snfota="urc",1'))
    connection_setup = dstl_get_connection_setup_object(test.dut)
    r1 = test.expect(test.dut.at1.send_and_verify('at^snfota="conid",{}'.format(connection_setup.dstl_get_used_cid())))
    r2 = test.expect(test.dut.at1.send_and_verify(
        'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.800_arn01.000.00_lynx_100_030_to_rev00.802_arn01.000.00_lynx_100_032_prod02sign.usf"'))
    r3 = test.expect(test.dut.at1.send_and_verify(
        'at^snfota="CRC","a2b1509f73318f5cb368c0555febae687c758552989d568ed54b72a78b30ff59"'))
    return r1 & r2 & r3


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_13_download_module_with_snfota(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_14_monitor_download_progress(test, force_abnormal_flow=False):
    download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,2,0,.*")
    if download_succeed:
        return True
    else:
        test.expect(False, critical=True)


def NF_15_power_off(test, force_abnormal_flow=False):
    test.sleep(random.randint(15, 30))
    test.expect(test.dut.devboard.send_and_verify('mc:gpiocfg=3,outp', 'OK', wait_after_send=3))
    test.dut.devboard.send('mc:gpio3cfg=1')
    test.dut.devboard.send('mc:gpio3cfg=0')


def NF_16_power_on_and_init(test, force_abnormal_flow=False):
    test.sleep(2)  # can not ignition after 20ms
    test.dut.devboard.send_and_verify('mc:igt=1000', 'OK')
    test.expect(test.dut.at1.wait_for('^SYSSTART'))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_17_send_alert_message(test, force_abnormal_flow=False):
    return True


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_18_set_sms_format(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_19_send_sms_to_r1(test, force_abnormal_flow=False):
    test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                             ".*>.*", wait_for=".*>.*", timeout=20, handle_errors=True))
    return test.expect(test.dut.at1.send_and_verify(f"TEST SMS{timex}", end="\u001A", expect=".*OK.*", timeout=20,
                                                    handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_20_check_sms_receive(test, force_abnormal_flow=False):
    test.sleep(5)
    return test.expect(test.r1.at1.send_and_verify("AT^SMGL=\"REC UNREAD\"", f"SMGL: \d+,.*TEST SMS{timex}.*",
                                                   timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_21_trigger_fw_swap(test, force_abnormal_flow=False):
    download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
    if download_succeed:
        test.log.info("downlaod successfully")
    else:
        test.expect(False, critical=True)
    return test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_22_wait_for_systart(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_23_check_firmware(test, force_abnormal_flow=False):
    test.sleep(5)
    dstl_detect(test.dut)
    return test.expect(test.dut.software_number == "100_032")


def NF_24_init_module(test, force_abnormal_flow=False):
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_25_config_server_type_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"srvType","Mqtt"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_26_config_service_conid_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"conid","1"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_27_config_service_address_mqtt(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify(f'AT^SISS=3,"address","{address_3}"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_28_config_service_hcmethod_publish(test, force_abnormal_flow=False):
    r1 = test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"cmd","publish"', handle_errors=True))
    r2 = test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"hcContLen",500', handle_errors=True))
    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_29_config_service_client_id_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"clientid","Lynx"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_30_config_service_topic_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"topic","auth"', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_31_activate_internet_connection_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SICA=1,1", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_32_open_internet_service_mqtt(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SISO=3", handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_33_set_dns_ttl_zero(test, force_abnormal_flow=False):
    return True


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_34_wait_for_sisw(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.wait_for('^SISW: 3,1', 20))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_35_send_tracking_data(test, force_abnormal_flow=False):
    send_data = dstl_generate_data(500)
    r1 = test.expect(
        test.dut.at1.send_and_verify("AT^SISW=3,500", expect='^SISW: 3,500,0', wait_for='^SISW', handle_errors=True))
    r2 = test.expect(test.dut.at1.send_and_verify(send_data, expect='^SISW: 3,2', wait_for='^SISW', handle_errors=True))
    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_36_check_data(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SISI=3", expect='500', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_37_close_internet_service_mqtt(test, force_abnormal_flow=False):
    global stop_run
    result = test.expect(test.dut.at1.send_and_verify("AT^SISC=3", handle_errors=True))
    if result:
        stop_run = True
    return result


if "__main__" == __name__:
    unicorn.main()
