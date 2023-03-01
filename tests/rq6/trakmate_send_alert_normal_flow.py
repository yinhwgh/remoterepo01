# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107873.001
import time

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.sms import send_sms_message
from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.sms import configure_sms_text_mode_parameters, select_sms_format, list_sms_message
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init

stop_run = False
step_list = ['NF_1_set_sms_format', 'NF_2_send_sms_to_r1', 'NF_3_check_sms_receive']
timex = time.time()


class Test(BaseTest):
    '''
     TC0107873.001 - Trakmate_TrackingUnit_SendAlert_NF
     This case mainly test RQ6000077.001 normal flow
     need 2 module with SIM card

    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r1.dstl_select_sms_message_format('Text')
        test.r1.dstl_configure_sms_event_reporting("2", "1")
        uc_init.whole_flow(test, uc_init.step_list)

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
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_1_set_sms_format(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_2_send_sms_to_r1(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                                 ".*>.*", wait_for=".*>.*", timeout=20, handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify(f"TEST SMS{timex}", end="\u001A", expect=".*OK.*", timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                                      ".*>.*", wait_for=".*>.*", timeout=20, handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify(f"TEST SMS{timex}", end="\u001A", expect=".*OK.*", timeout=20,
                                                      handle_errors=True))
    return r1 & r2


def NF_3_check_sms_receive(test, force_abnormal_flow=False):
    global stop_run
    test.sleep(5)
    result = test.expect(test.r1.at1.send_and_verify("AT^SMGL=\"REC UNREAD\"", f"SMGL: \d+,.*TEST SMS{timex}.*",
                                                     timeout=20, handle_errors=True))
    if result:
        stop_run = True
    else:
        error_handle_1(test)


if "__main__" == __name__:
    unicorn.main()
