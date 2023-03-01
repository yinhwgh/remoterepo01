# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107865.001
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
from tests.rq6 import trakmate_send_trackingdata_normal_flow as send_data

data_30 = dstl_generate_data(30)


class Test(BaseTest):
    '''
     The case is intended to test the normal flow according to RQ6000079.001
     -- Trakmate_TrackingUnit_SendNotification_NormalFlow
     at1: ASC0 at2: USBM

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def send_alert_to_r1(test, step):
    test.log.step(f'{step}.1 Send sms from USB port')
    timex = time.time()
    test.expect(test.dut.at2.send_and_verify('AT+CMGF=1', 'OK'))
    test.expect(test.dut.at2.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                             ".*>.*", wait_for=".*>.*"))
    test.expect(test.dut.at2.send_and_verify(f"TEST SMS{timex}", end="\u001A", expect="CMGS: \d+.*OK.*"))
    # test.expect(test.dut.at2.send_and_verify("AT^SMGL=\"REC UNREAD\"",f"SMGL: \d+,.*TEST SMS{timex}.*"))


def main_process(test):
    test.log.step('1.Send message to server for the alert notification with tcp')
    send_data.whole_flow(test, send_data.step_list[0:5])
    test.expect(test.dut.at1.send_and_verify(f'AT^SISW=0,30', 'SISW:', wait_for='SISW:'))
    send_alert_to_r1(test, 1)
    test.expect(test.dut.at1.send_and_verify(data_30, 'OK', wait_for='SISW:'))
    test.expect(
        test.dut.at1.send_and_verify_retry('AT^SISI=0', 'SISI: 0,4,0,30'))
    send_data.whole_flow(test, send_data.step_list[7:10])
    test.log.step('2.Send message to server for the alert notification with HTTP post')
    test.expect(test.dut.at1.send_and_verify(f'AT^SISW=2,30', 'SISW:', wait_for='SISW:'))
    send_alert_to_r1(test, 2)
    test.expect(test.dut.at1.send_and_verify(data_30, 'OK', wait_for='SISW:'))
    test.expect(
        test.dut.at1.send_and_verify_retry('AT^SISI=2', 'SISI: 2,4,0,30'))
    send_data.whole_flow(test, send_data.step_list[12:15])
    test.log.step('3.Send message to server for the alert notification with MQTT')
    test.expect(test.dut.at1.send_and_verify(f'AT^SISW=3,30', 'SISW:', wait_for='SISW:'))
    send_alert_to_r1(test, 3)
    test.expect(test.dut.at1.send_and_verify(data_30, 'OK', wait_for='SISW:'))
    test.expect(
        test.dut.at1.send_and_verify_retry('AT^SISI=3', 'SISI: 3,4,0,30'))
    send_data.whole_flow(test, send_data.step_list[16:18])


if "__main__" == __name__:
    unicorn.main()
