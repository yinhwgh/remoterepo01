# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107875.001
import time

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
from dstl.auxiliary.generate_data import dstl_generate_data

step_list = ['NF_1_cell_monitor', 'NF_2_check_signal', 'NF_4_active_sica', 'NF_8_open_service_0',
             'NF_9_check_sisw_urc', 'NF_10_send_data', 'NF_11_check_sisi_0',
             'NF_12_close_service_0', 'NF_18_open_service_2', 'NF_19_check_sisw_urc',
             'NF_20_send_data', 'NF_21_check_sisi_2', 'NF_22_close_service_2',
             'NF_30_open_service_3', 'NF_32_check_sisw_urc', 'NF_33_send_data',
             'NF_34_check_sisi_3', 'NF_35_close_service_3']

stop_run = False
data_500 = dstl_generate_data(500)
duration = 5 * 60 * 60


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000079.001
     -- Trakmate_TrackingUnit_SendTrackingData_NF

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
    start_time = time.time()
    while (time.time() - start_time < duration):
        test.expect(test.dut.at1.send_and_verify(f'AT^SISC=0', 'OK', timeout=20,
                                                 handle_errors=True))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISO=0', 'OK', timeout=20, wait_for='SISW',
                                                 handle_errors=True))
        r1 = test.dut.at1.send_and_verify(f'AT^SISW=0,500', 'SISW:', wait_for='SISW:', timeout=20,
                                          handle_errors=True)
        if r1:
            test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:'))
            r2 = test.expect(
                test.dut.at1.send_and_verify_retry(f'AT^SISI=0', 'SISI: 0,4,0,500', retry=2,
                                                   sleep=3, handle_errors=True))
        else:
            r2 = False
        if r2:
            return True
    test.log.info(f'===Still send fail after {duration}s, will reset module===')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART', 20))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


def error_handle_3(test):
    test.log.info('Start Error handle step 3')
    start_time = time.time()
    while (time.time() - start_time < duration):
        test.expect(test.dut.at1.send_and_verify(f'AT^SISC=2', 'OK', timeout=20,
                                                 handle_errors=True))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISO=2', 'OK', timeout=20, wait_for='SISW',
                                                 handle_errors=True))
        r1 = test.dut.at1.send_and_verify(f'AT^SISW=2,500', 'SISW:', wait_for='SISW:', timeout=20,
                                          handle_errors=True)
        if r1:
            test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:'))
            r2 = test.expect(
                test.dut.at1.send_and_verify_retry(f'AT^SISI=2', 'SISI: 2,4,0,500', retry=2,
                                                   sleep=3, handle_errors=True))
        else:
            r2 = False
        if r2:
            return True
    test.log.info(f'===Still send fail after {duration}s, will reset module===')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART', 20))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


def error_handle_4(test):
    test.log.info('Start Error handle step 4')
    start_time = time.time()
    while (time.time() - start_time < duration):
        test.expect(test.dut.at1.send_and_verify(f'AT^SISC=3', 'OK', timeout=20,
                                                 handle_errors=True))
        test.expect(test.dut.at1.send_and_verify(f'AT^SISO=3', 'OK', timeout=20, wait_for='SISW',
                                                 handle_errors=True))
        r1 = test.dut.at1.send_and_verify(f'AT^SISW=3,500', 'SISW:', wait_for='SISW:', timeout=20,
                                          handle_errors=True)
        if r1:
            test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:'))
            r2 = test.expect(
                test.dut.at1.send_and_verify_retry(f'AT^SISI=3', 'SISI: 3,4,0,500', retry=2,
                                                   sleep=3, handle_errors=True))
        else:
            r2 = False
        if r2:
            return True
    test.log.info(f'===Still send fail after {duration}s, will reset module===')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART', 20))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test, step_list)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_1_cell_monitor(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SMONI', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SMONI', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_2_check_signal(test, force_abnormal_flow=False):
    test.sleep(5)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT+CSQ', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_4_active_sica(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_8_open_service_0(test, force_abnormal_flow=False):
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', timeout=20, handle_errors=True)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=0', 'OK', timeout=20, handle_errors=True),
                           msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=0', 'OK', timeout=20, handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_9_check_sisw_urc(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        result = test.expect(test.dut.dstl_check_urc('SISW: 0,1', timeout=20), msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.dstl_check_urc('SISW: 0,1', timeout=20))
    if result:
        return True
    else:
        max_retry = 10
        i = 0
        while i < max_retry:
            test.log.info(f'Start reopen socket the {i + 1}th time')
            test.dut.at1.send_and_verify('AT^SISC=0')
            test.sleep(1)
            test.dut.at1.send_and_verify('AT^SISO=0')
            result = test.dut.dstl_check_urc('SISW: 0,1')
            if result:
                return True
            else:
                i = i + 1
        return False


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_10_send_data(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=0,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=0,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))

    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_2'))
def NF_11_check_sisi_0(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=0', 'SISI: 0,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=0', 'SISI: 0,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_12_close_service_0(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISC=0', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISC=0', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_18_open_service_2(test, force_abnormal_flow=False):
    test.dut.at1.send_and_verify('AT^SISC=2', 'OK', timeout=20, handle_errors=True)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=2', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=2', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_19_check_sisw_urc(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        result = test.expect(test.dut.dstl_check_urc('SISW: 2,1', timeout=20), msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.dstl_check_urc('SISW: 2,1', timeout=20))
    if result:
        return True
    else:
        max_retry = 10
        i = 0
        while i < max_retry:
            test.log.info(f'Start reopen socket the {i + 1}th time')
            test.dut.at1.send_and_verify('AT^SISC=2')
            test.sleep(1)
            test.dut.at1.send_and_verify('AT^SISO=2')
            result = test.dut.dstl_check_urc('SISW: 2,1')
            if result:
                return True
            else:
                i = i + 1
        return False


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_20_send_data(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=2,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=2,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))

    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_3'))
def NF_21_check_sisi_2(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=2', 'SISI: 2,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=2', 'SISI: 2,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_22_close_service_2(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISC=2', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISC=2', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_30_open_service_3(test, force_abnormal_flow=False):
    test.dut.at1.send_and_verify('AT^SISC=3', 'OK', timeout=20, handle_errors=True)
    if force_abnormal_flow:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=3', 'OK', timeout=20,
                                                        handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(test.dut.at1.send_and_verify(f'AT^SISO=3', 'OK', timeout=20,
                                                        handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_32_check_sisw_urc(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        result = test.expect(test.dut.dstl_check_urc('SISW: 3,1', timeout=20), msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.dstl_check_urc('SISW: 3,1', timeout=20))
    if result:
        return True
    else:
        max_retry = 10
        i = 0
        while i < max_retry:
            test.log.info(f'Start reopen socket the {i + 1}th time')
            test.dut.at1.send_and_verify('AT^SISC=3')
            test.sleep(1)
            test.dut.at1.send_and_verify('AT^SISO=3')
            result = test.dut.dstl_check_urc('SISW: 3,1')
            if result:
                return True
            else:
                i = i + 1
        return False


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_33_send_data(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=3,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True), msg="force_abnormal_flow")
    else:
        r1 = test.expect(test.dut.at1.send_and_verify(f'AT^SISW=3,500', 'SISW:', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))
        r2 = test.expect(test.dut.at1.send_and_verify(data_500, 'OK', wait_for='SISW:', timeout=20,
                                                      handle_errors=True))

    return r1 & r2


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_4'))
def NF_34_check_sisi_3(test, force_abnormal_flow=False):
    if force_abnormal_flow:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=3', 'SISI: 3,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True), msg="force_abnormal_flow")
    else:
        return test.expect(
            test.dut.at1.send_and_verify_retry(f'AT^SISI=3', 'SISI: 3,4,0,500', retry=2, timeout=5, sleep=3,
                                               handle_errors=True))


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_35_close_service_3(test, force_abnormal_flow=False):
    global stop_run
    if force_abnormal_flow:
        result = test.expect(test.dut.at1.send_and_verify(f'AT^SISC=3', 'OK', timeout=20,
                                                          handle_errors=True), msg="force_abnormal_flow")
    else:
        result = test.expect(test.dut.at1.send_and_verify(f'AT^SISC=3', 'OK', timeout=20,
                                                          handle_errors=True))
    if result:
        stop_run = True
    return result


if "__main__" == __name__:
    unicorn.main()
