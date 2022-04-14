# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0107863.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init

from dstl.configuration import shutdown_smso
from dstl.network_service import register_to_network
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.configuration import scfg_urc_ringline_config
from tests.rq6.use_case_aux import step_with_error_handle, generate_hash_file
from tests.rq6 import trakmate_init_module_normal_flow as uc_init
from tests.rq6 import trakmate_download_config_normal_flow as uc_download
from tests.rq6 import trakmate_send_trackingdata_normal_flow as uc_send_data

step_list = []
stop_run = False
app_firmware = '500k.usf'
download_address = 'http://114.55.6.216:10080/'


class Test(BaseTest):
    '''
     The case is intended to test the exception flow according to RQ6000074.001
     -- Trakmate - TrackingUnit - UpdateApplication

    '''

    def setup(test):
        test.dut.dstl_detect()
        uc_init.whole_flow(test, uc_init.step_list)
        test.dut.dstl_activate_urc_ringline_to_local()
        test.dut.dstl_set_urc_ringline_active_time('2')

    def run(test):
        whole_flow(test)

    def cleanup(test):
        pass


def error_handle_1(test):
    test.log.info('Start Error handle step 1')
    test.expect(test.dut.dstl_shutdown_smso())
    test.sleep(3)
    test.expect(test.dut.devboard.send_and_verify('MC:IGT=300'))
    test.expect(test.dut.at1.wait_for('^SYSSTART'))


@step_with_error_handle(max_retry=2, step_if_error=eval('error_handle_1'))
def restart_module(test, force_abnormal_flow=False):
    return test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK', timeout=20,
                                        handle_errors=True)


def whole_flow(test):
    crc = generate_hash_file(test, app_firmware)
    test.log.step('1.Download Hash')
    test.expect(
        test.dut.at1.send_and_verify(f'AT^SISS=1,"address","{download_address}crc_value"', 'OK'))
    uc_download.whole_flow(test, uc_download.step_list)

    test.log.step('2.Download application firmware')
    test.expect(
        test.dut.at1.send_and_verify(f'AT^SISS=1,"address","{download_address}{app_firmware}"', 'OK'))
    uc_download.whole_flow(test, uc_download.step_list)

    test.log.step('3. Check if match, skip')
    test.log.step('4. Application firmware swup, skip')

    test.log.step('5. Soft reset the module, force error 2 times')
    restart_module(test, True)
    test.log.step('6. Initialize the module')
    uc_init.whole_flow(test, uc_init.step_list)
    test.log.step('7. Send report to task server')
    uc_send_data.whole_flow(test, uc_send_data.step_list)


if "__main__" == __name__:
    unicorn.main()
