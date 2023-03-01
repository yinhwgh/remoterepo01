# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107845.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.sms import send_sms_message
from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init

step_list = ['NF_1_set_ER_mode', 'NF_2_restart', 'NF_3_enable_creg_urc',
             'NF_4_get_information_for_setup_menu', 'NF_5_confirm_success',
             'NF_6_get_information_for_setup_event_list', 'NF_7_confirm_success',
             'NF_8_menu_selection', 'NF_9_get_information_for_select_item', 'NF_10_request_imsi',
             'NF_11_select_one_sim_profile', 'NF_12_get_information_for_fresh',
             'NF_13_refresh_with_polling_off', 'NF_14_check_mno', 'NF_15_request_imsi']
stop_run = False


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000080.001
     GOAL: To switch SIM profile to be always online.

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        whole_flow(test, step_list)

    def cleanup(test):
        pass


def whole_flow(test, test_step_list, fail_step=0, restart_step=1):
    global stop_run
    if not stop_run:
        for i in range(len(test_step_list)):
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
    test.expect(test.dut.at1.wait_for('^SYSSTART'))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_1_set_ER_mode(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify('AT^SSTA=1,0', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_2_restart(test, force_abnormal_flow=False):
    return test.expect(test.dut.dstl_restart())


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_3_enable_creg_urc(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT+CREG=2", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_4_get_information_for_setup_menu(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTGI=37", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_5_confirm_success(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTR=37,0", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_6_get_information_for_setup_event_list(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTGI=5", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_7_confirm_success(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTR=5,0", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_8_menu_selection(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify("AT^SSTR=211,0,128", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_9_get_information_for_select_item(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTGI=36", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_10_request_imsi(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT+CIMI", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_11_select_one_sim_profile(test, force_abnormal_flow=False):
    return test.expect(
        test.dut.at1.send_and_verify("AT^SSTR=36,0,2", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_12_get_information_for_fresh(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTGI=1", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_13_refresh_with_polling_off(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT^SSTR=1,4", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_14_check_mno(test, force_abnormal_flow=False):
    return test.expect(test.dut.at1.send_and_verify("AT+COPS?", timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def NF_15_request_imsi(test, force_abnormal_flow=False):
    global stop_run
    result = test.expect(test.dut.at1.send_and_verify('AT+CIMI', timeout=20, handle_errors=True))
    if result:
        stop_run = True
    return result


if "__main__" == __name__:
    unicorn.main()
