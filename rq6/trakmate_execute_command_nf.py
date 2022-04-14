# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107826.001

import re
import random
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.configuration import scfg_urc_ringline_config
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms import configure_sms_text_mode_parameters
from tests.rq6.use_case_aux import step_with_error_handle
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6 import trakmate_send_trackingdata_normal_flow as send_data
from tests.rq6 import trakmate_download_config_normal_flow as download_config
from tests.rq6 import trakmate_update_application_normal_flow as update_app

command_list = ['Download Configuration', 'Send Track data', 'Update Application']


class Test(BaseTest):
    '''
    TC0107826.001 - Trakmate_TrackingUnit_ExecuteCommand_NormalFlow
    Subscriber: 2
    at1: dAsc0  at2:dUSBM
    '''

    def setup(test):
        test.expect(test.dut.at2.send_and_verify('AT^SPOW=1,0,0'))
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.r1.dstl_configure_sms_event_reporting("2", "1")
        uc_init.whole_flow(test, uc_init.step_list)
        test.dut.dstl_activate_urc_ringline_to_local()
        test.dut.dstl_set_urc_ringline_active_time('2')
        test.expect(test.dut.at1.send_and_verify('AT^SPOW=2,1000,3'))

    def run(test):
        whole_flow(test)

    def cleanup(test):
        test.expect(test.dut.at2.send_and_verify('AT^SPOW=1,0,0'))


def whole_flow(test, error_flow=False):
    for i in range(3):
        cmd_flow(test, i, error_flow)


def cmd_flow(test, cmd_index, error_flow=False):
    index = get_cmd_sms_index_from_r1(test, command_list[cmd_index])
    read_sms_and_execute_cmd(test, index)
    if error_flow:
        NF_4_send_sms_to_r1(test, True)
    else:
        NF_4_send_sms_to_r1(test, False)
        NF_5_delete_sms(test, index)
        NF_6_list_unread_sms(test)


def error_handle_1(test):
    test.log.info('Start Error handle step 1')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART'))
    uc_init.whole_flow(test, uc_init.step_list, restart_step=2)
    whole_flow(test)


def get_cmd_sms_index_from_r1(test, command):
    test.log.step('1.Send Command SMS to DUT')
    test.expect(test.r1.dstl_select_sms_message_format())
    test.expect(test.r1.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr),
                                            ".*>.*", wait_for=".*>.*"))
    test.expect(test.r1.at1.send_and_verify(f"{command}", end="\u001A", expect="CMGS: \d+.*OK.*"))
    test.expect(test.dut.at1.wait_for('CMTI:', timeout=150))
    sms_received = re.search(r"CMTI:.*,(\d+)", test.dut.at1.last_response)
    if sms_received:
        sms_index = sms_received.group(1)
        test.log.info(f'Received sms index is {sms_index}.')
        return sms_index
    else:
        test.log.error('Get sms index fail.')
        return 0


def read_sms_and_execute_cmd(test, index):
    test.log.step('2.Read SMS from remote')
    test.dut.at1.send_and_verify(f'AT+CMGR={index}')
    test.log.step('3.Execute command in SMS')
    for i in range(3):
        if command_list[i] in test.dut.at1.last_response:
            test.log.info(f'*** Start {command_list[i]} process ***')
            if i == 0:
                download_config.whole_flow(test, download_config.step_list)
            elif i == 1:
                send_data.whole_flow(test, send_data.step_list)
            else:
                update_app.whole_flow(test)


@step_with_error_handle(max_retry=1, step_if_error=eval('error_handle_1'))
def NF_4_send_sms_to_r1(test, force_abnormal_flow=False):
    test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK', timeout=20, handle_errors=True))
    test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                             ".*>.*", wait_for=".*>.*", timeout=20,
                                             handle_errors=True))
    return test.expect(
        test.dut.at1.send_and_verify(f"Execute done.", end="\u001A", expect="CMGS: \d+.*OK.*",
        timeout=20, handle_errors=True))


def NF_5_delete_sms(test, index):
    return test.expect(
        test.dut.at1.send_and_verify(f'AT+CMGD={index}', 'OK', timeout=20, handle_errors=True))


def NF_6_list_unread_sms(test):
    return test.expect(
        test.dut.at1.send_and_verify('AT+CMGL="REC UNREAD"', 'OK', timeout=20, handle_errors=True))


if "__main__" == __name__:
    unicorn.main()
