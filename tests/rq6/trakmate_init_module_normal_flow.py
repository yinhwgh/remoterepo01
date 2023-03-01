# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107871.001
import time
import re
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.fallback import devboard_power_cycle
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.configuration import shutdown_smso
from dstl.usim.get_imsi import dstl_get_imsi
from tests.rq6.use_case_aux import step_with_error_handle

step_list = ['NF_1_power_on', 'NF_2_check_at_communication', 'NF_3_check_sim_iccid',
             'NF_4_check_imsi', 'NF_5_deregister_network', 'NF_6_register_to_network',
             'NF_7_check_if_registered', 'NF_8_get_currnet_time', 'NF_9_get_operator_name',
             'NF_10_enable_at_echo', 'NF_11_set_full_function_mode', 'NF_12_set_apn',
             'NF_13_config_service_0_type_tcp', 'NF_14_config_service_0_conid',
             'NF_15_config_service_0_address', 'NF_16_config_service_1_type_http',
             'NF_17_config_service_1_conid', 'NF_18_config_service_1_address',
             'NF_19_config_service_1_hcmethod', 'NF_20_config_service_1_parameter',
             'NF_21_config_service_2_type_http', 'NF_22_config_service_2_conid',
             'NF_23_config_service_2_address', 'NF_24_config_service_2_hcmethod',
             'NF_25_config_service_2_parameter', 'NF_26_config_service_3_type_mqtt',
             'NF_27_config_service_3_conid', 'NF_28_config_service_3_address',
             'NF_29_config_service_3_mqtt_cmd', 'NF_30_config_service_3_mqtt_client_id',
             'NF_31_config_service_3_mqtt_topic', 'NF_32_check_sica', 'NF_33_set_sms_format',
             'NF_34_open_sms_urc', 'NF_35_list_unread_sms']

stop_run = False

address_0 = 'socktcp://114.55.6.216:50000'
address_1 = 'http://114.55.6.216:10080/test.bin'
address_2 = 'http://www.httpbin.org/post'
address_3 = 'mqtt://114.55.6.216:2010'


class Test(BaseTest):
    '''
     TC0107871.001 - Trakmate_TrackingUnit_InitModule_NF
     This case mainly test the RQ6000076.001 normal flow

    '''

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        whole_flow(test, step_list)

    def cleanup(test):
        pass


def whole_flow(test, test_step_list, fail_step=0, restart_step=1):
    global stop_run
    stop_run = False

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
    test.expect(test.dut.at1.wait_for('^SYSSTART', 20))
    whole_flow(test, step_list)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_1_power_on(test, force_abnormal_flow=False):
    devboard_power_cycle(test.dut.devboard)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.wait_for('^SYSSTART', 20), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.wait_for('^SYSSTART', 20))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_2_check_at_communication(test, force_abnormal_flow=False):
    test.sleep(5)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_3_check_sim_iccid(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+CCID', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+CCID', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_4_check_imsi(test, force_abnormal_flow=False):
    test.dut.at1.send_and_verify("AT+CIMI", 'OK', timeout=20, handle_errors=True)
    last_resp = test.dut.at1.last_response
    pattern = r".*\b\d{15}\b.*"
    match = re.search(pattern, last_resp, re.M)
    imsi = ''
    if match:
        value = match.group()
        imsi = str(value).strip()
    if imsi:
        test.log.info(f'Get IMSI: {imsi}')
        return test.expect(True)
    elif force_abnormal_flow:
        return test.expect(False, msg="force_abnormal_flow")
    else:
        return test.expect(False)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_5_deregister_network(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS=2', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_6_register_to_network(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS=0', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_7_check_if_registered(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify_retry('AT+CREG?', 'CREG: \d,1', retry=2,
                                                              wait_after_send=5, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify_retry('AT+CREG?', 'CREG: \d,1', retry=2,
                                                              wait_after_send=5, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_8_get_currnet_time(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SIND="nitz",2', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SIND="nitz",2', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_9_get_operator_name(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+COPS?', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_10_enable_at_echo(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('ATE1', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('ATE1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_11_set_full_function_mode(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+CFUN=1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_12_set_apn(test, force_abnormal_flow=False):
    if test.dut.sim.apn_v4 == 'None':
        apn = 'airtelgprs.com'
    else:
        apn = test.dut.sim.apn_v4
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,IPV4V6,{apn}', 'OK',
                                                        timeout=20, handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT+CGDCONT=1,IPV4V6,{apn}', 'OK',
                                                        timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_13_config_service_0_type_tcp(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"srvType","socket"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"srvType","socket"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_14_config_service_0_conid(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_15_config_service_0_address(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=0,"address","{address_0}"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=0,"address","{address_0}"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_16_config_service_1_type_http(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvType","http"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"srvType","http"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_17_config_service_1_conid(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conid","1"', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_18_config_service_1_address(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=1,"address","{address_1}"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=1,"address","{address_1}"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_19_config_service_1_hcmethod(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd","get"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"cmd","get"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_20_config_service_1_parameter(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"hcProp","Content-Type: \'text/plain\'"', 'OK',
                                                        timeout=20, handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=1,"hcProp","Content-Type: \'text/plain\'"', 'OK',
                                                        timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_21_config_service_2_type_http(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"srvtype","http"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"srvtype","http"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_22_config_service_2_conid(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_23_config_service_2_address(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=2,"address","{address_2}"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=2,"address","{address_2}"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_24_config_service_2_hcmethod(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"cmd","post"', 'OK', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"hcContLen","500"', 'OK', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"cmd","post"', 'OK', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"hcContLen","500"', 'OK', timeout=20,
                                                      handle_errors=True))
    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_25_config_service_2_parameter(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"hcProp","Content-Type: \'text/plain\'"', 'OK',
                                                        timeout=20, handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=2,"hcProp","Content-Type: \'text/plain\'"', 'OK',
                                                        timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_26_config_service_3_type_mqtt(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"srvType","Mqtt"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"srvType","Mqtt"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_27_config_service_3_conid(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"conid","1"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_28_config_service_3_address(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=3,"address","{address_3}"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISS=3,"address","{address_3}"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_29_config_service_3_mqtt_cmd(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"cmd","publish"', 'OK', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify('AT^siss=3,hcContLen,500', 'OK', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"cmd","publish"', 'OK', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify('AT^siss=3,hcContLen,500', 'OK', timeout=20,
                                                      handle_errors=True))
    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_30_config_service_3_mqtt_client_id(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"clientid","Lynx"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"clientid","Lynx"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_31_config_service_3_mqtt_topic(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"topic","auth"', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISS=3,"topic","auth"', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_32_check_sica(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SICA?', 'OK', handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SICA?', 'OK', handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_33_set_sms_format(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_34_open_sms_urc(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK', timeout=20, handle_errors=True),
            msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_35_list_unread_sms(test, force_abnormal_flow=False):
    global stop_run
    if force_abnormal_flow:
        result = test.expect(test.dut.at1.send_and_verify('AT+CMGL="REC UNREAD"', timeout=20, handle_errors=True),
                             msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.at1.send_and_verify('AT+CMGL="REC UNREAD"', timeout=20, handle_errors=True))
    if result:
        stop_run = True
    return result


if "__main__" == __name__:
    unicorn.main()
