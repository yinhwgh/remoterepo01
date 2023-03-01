# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107880.001

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
from tests.rq6.use_case_aux import step_with_error_handle, generate_hash_file
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6 import trakmate_download_config_normal_flow as download_config
from tests.rq6 import trakmate_send_trackingdata_normal_flow as send_data
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.fallback import devboard_power_cycle

stop_run = False
up_grade_firmware = 'els62-w_rev00.800_arn01.000.00_lynx_100_030_to_rev00.802_arn01.000.00_lynx_100_032_prod02sign.usf'
down_grade_firmware = 'els62-w_rev00.802_arn01.000.00_lynx_100_032_to_rev00.800_arn01.000.00_lynx_100_030_prod02sign.usf'
download_address = 'http://114.55.6.216:10080/'
up_grade_sw = 'LYNX_100_032'
down_grade_sw = 'LYNX_100_030'
up_grade = False  # if degrade , set up_grade=False, else True

data_30 = dstl_generate_data(30)


class Test(BaseTest):
    '''
    TC0107880.001 - Trakmate_TrackingUnit_UpdateModuleFOTA_NF01
    Subscriber: 1
    at1: dAsc0
    Send message to server for the alert notification with HTTP post
    Please check fota package name and SW version before execute the case.
    '''

    def setup(test):
        uc_init.whole_flow(test, uc_init.step_list)
        test.dut.dstl_activate_urc_ringline_to_local()
        test.dut.dstl_set_urc_ringline_active_time('2')

    def run(test):
        whole_flow(test, up_grade)

    def cleanup(test):
        pass


def whole_flow(test, upgrade, abort=False):
    test.log.step('1.Download Hash')
    download_config.whole_flow(test, download_config.step_list)
    test.log.step('2.Configure SNFOTA feature')
    if upgrade:
        config_snfota(test, up_grade_firmware)
    else:
        config_snfota(test, down_grade_firmware)
    test.log.step('3.Trigger the download')
    trigger_download(test)
    test.log.step('4.Trigger the firmware swup process')
    trigger_swup(test, abort)
    if check_sw(test, upgrade):
        uc_init.whole_flow(test, uc_init.step_list[1:])
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK'))
        # NF_18_open_service_2,NF_19_check_sisw_urc
        send_data.whole_flow(test, send_data.step_list[8:10])
        test.log.step('5.Send message to server for the alert notification with HTTP post')
        test.expect(test.dut.at1.send_and_verify(f'AT^SISW=2,30', 'SISW:', wait_for='SISW:'))
        test.expect(test.dut.at1.send_and_verify(data_30, 'OK', wait_for='SISW:'))
        test.expect(test.dut.at1.send_and_verify_retry('AT^SISI=2', 'SISI: 2,4,0,30'))
        test.log.step('6.Send SMS to server for the alert notification')
        test.expect(test.dut.at1.send_and_verify('AT+CMGF=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr),
                                                 ".*>.*", wait_for=".*>.*"))
        test.expect(test.dut.at1.send_and_verify(f"Update success", end="\u001A", expect="CMGS: \d+.*OK.*"))
    else:
        test.expect(False, msg='Update fail')


def config_snfota(test, module_firmware):
    crc = generate_hash_file(test, module_firmware)
    test.expect(
        test.dut.at1.send_and_verify(f'AT^SNFOTA="url","{download_address}{module_firmware}"', 'OK'))
    test.expect(
        test.dut.at1.send_and_verify(f'AT^SNFOTA="crc","{crc}"', 'OK'))
    test.expect(
        test.dut.at1.send_and_verify(f'AT^SNFOTA="conid","1"', 'OK'))


def trigger_download(test, abort=False):
    test.expect(
        test.dut.at1.send_and_verify('AT^SNFOTA="act",2', 'OK'))
    if abort:
        test.log.info('Abort during download progress')
        test.expect(test.dut.at1.wait_for('SNFOTA:\s?act,2,0,50', timeout=300))
        devboard_power_cycle(test.dut.devboard)
        test.expect(test.dut.at1.wait_for('SYSSTART'))
        uc_init.whole_flow(test, uc_init.step_list[1:])
        whole_flow(test, up_grade, abort=False)
    else:
        test.expect(test.dut.at1.wait_for('SNFOTA:\s?act,0,0,100', timeout=300))


def trigger_swup(test, abort):
    test.expect(
        test.dut.at1.send_and_verify('AT^SFDL=2', 'OK'))
    if abort:
        test.log.info('Abort during swup progress')
        test.sleep(60)
        devboard_power_cycle(test.dut.devboard)
        test.expect(test.dut.at1.wait_for('SYSSTART'))
        uc_init.whole_flow(test, uc_init.step_list[1:])
        whole_flow(test, up_grade, abort=False)
    else:
        test.expect(test.dut.at1.wait_for('SYSSTART', timeout=600))


def check_sw(test, upgrade):
    test.expect(test.dut.at1.send_and_verify('ati1', 'OK'))
    if upgrade:
        return test.expect(test.dut.at1.send_and_verify('at^cicret=swn', up_grade_sw))
    else:
        return test.expect(test.dut.at1.send_and_verify('at^cicret=swn', down_grade_sw))


if "__main__" == __name__:
    unicorn.main()
