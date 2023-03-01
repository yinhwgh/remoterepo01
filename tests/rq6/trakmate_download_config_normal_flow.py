# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107854.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.configuration import scfg_urc_ringline_config
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init

step_list = ['NF_2_active_sica',
             'NF_8_open_serive', 'NF_9_wait_sisr_urc', 'NF_10_read_file', 'NF_11_close_service']

stop_run = False


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000074.001
     -- Trakmate - TrackingUnit - DownLoadConfiguration
     GOAL: To get a-gps file from the ublox web site.

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)
        test.dut.dstl_activate_urc_ringline_to_local()
        test.dut.dstl_set_urc_ringline_active_time('2')

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
    test.log.info('Start Error handle step 1')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART'))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


def error_handle_2(test):
    test.log.info('Start Error handle step 2')
    max_retry = 10
    i = 0
    while i < max_retry:
        test.log.info(f'Start reopen socket the {i + 1}th time')
        test.dut.at1.send_and_verify('AT^SISC=1')
        test.sleep(1)
        test.dut.at1.send_and_verify('AT^SISO=1')
        result = test.dut.dstl_check_urc('SISR: 1,1')
        if result:
            test.dut.at1.send_and_verify('AT^SISC=1')
            return True
        else:
            i = i + 1


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_2_active_sica(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK', timeout=20, handle_errors=True),
            msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_8_open_serive(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SISO=1', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SISO=1', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_2'))
def NF_9_wait_sisr_urc(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.dstl_check_urc('SISR: 1,1'), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.dstl_check_urc('SISR: 1,1'))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_10_read_file(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        result = test.expect(test.dut.at1.send_and_verify('AT^SISR=1,1000', timeout=20, handle_errors=True),
                             msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.at1.send_and_verify('AT^SISR=1,1000', timeout=20, handle_errors=True))
    response = test.dut.at1.last_response
    while (result and 'SISR: 1,-2' not in response):
        result = test.expect(test.dut.at1.send_and_verify('AT^SISR=1,1000', timeout=20, wait_for='OK', handle_errors=True))
        response = test.dut.at1.last_response
    return result


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_11_close_service(test, force_abnormal_flow=False):
    global stop_run
    if force_abnormal_flow:
        result = test.expect(test.dut.at1.send_and_verify('AT^SISC=1', timeout=20, handle_errors=True),
                             msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.at1.send_and_verify('AT^SISC=1', timeout=20, handle_errors=True))
    if result:
        stop_run = True
    return result


if "__main__" == __name__:
    unicorn.main()
