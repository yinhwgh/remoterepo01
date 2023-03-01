# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0092515.001, TC0104620.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.auxiliary import restart_module
from dstl.serial_interface import config_baudrate
from dstl.security import lock_unlock_sim
from dstl.network_service.register_to_network import dstl_enter_pin


class IprConfigAsc(BaseTest):
    """

    NOTE: this file should not be called directly by Unicorn.
            please call this file only over a single campaign file as it is done by:
            tests/interface/serial/ipr_config_asc0.cfg  or by:
            tests/interface/serial/ipr_config_asc1.cfg

    Checking functionality of AT+IPR command.
    0. Check if dut.at1 is really a serial port - otherwise abort with error/warning
    0. Extract current baud rate - maybe local device.cfg operates on a different one
    1. Check if test command response contains all supported bitrates.
    2. Check if IPR is not protected by PIN.
    3. Set another bitrate.
    4. Restart ME and check if value is stored in non-volatile memory.
    9. CleanUp:
        change back to original baud rate from step 0.
    """

    original_baudrate_str = ''
    dut_at1_original_settings = None

    def setup(test):
        # if this TS is called by tests/interface/serial/ipr_config_asc1.cfg which changed dut.at1 to dut.asc_1
        if 'asc_1' in test.dut.at1.name:
            test.log.h1(' ASC1 found on at1 - test can go on')
        elif 'asc_0' in test.dut.at1.name:
            test.log.h1(' ASC0 found on at1 - test can go on')
        else:
            test.expect(False, critical=True, msg=" ASC0/1 is not on AT1 - test has to be performed on ASC0/1, ABORT")

        # save original settings from device.cfg as stated in IPIS100333554
        test.dut_at1_original_settings = dict(test.dut.at1.settings)
        test.original_baudrate_str = test.dut_at1_original_settings['baudrate']
        test.log.h2('original baud rate from config: {}'.format(test.dut_at1_original_settings['baudrate']))

        # test.DEFAULT_BITRATE = "115200"
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.supported_baudrates_atc = test.dut.dstl_get_supported_baudrate_list_atspec()
        pass

    def run(test):
        test.log.step("1. Check if test command response contains all supported bitrates.")
        test.expect(test.check_test_command())

        test.log.step("2. Check if IPR is not protected by PIN.")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*OK.*"))
        if "READY" in test.dut.at1.last_response:
            test.expect(test.dut.dstl_lock_sim())
            test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
        test.expect(test.dut.at1.send_and_verify("AT+IPR?", ".*OK.*"))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify("AT+IPR?", ".*OK.*"))

        test.log.step("3. Set another bitrate.")
        other_bitrate = str(test.supported_baudrates_atc[1])
        test.expect(test.dut.dstl_set_baudrate(other_bitrate, test.dut.at1))

        test.log.step("4. Restart ME and check if value is stored in non-volatile memory ")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_get_baudrate(test.dut.at1) == other_bitrate)
        pass

    def cleanup(test):
        if test.dut_at1_original_settings is None:
            #  do nothing, no settings stored so far
            return

        # test.expect(test.dut.dstl_set_baudrate(test.DEFAULT_BITRATE, test.dut.at1))
        baudrate_from_config = test.dut_at1_original_settings['baudrate']
        test.log.step('9. Set back to original baudrate AT+IPR={}.'.format(baudrate_from_config))
        test.expect(test.dut.dstl_set_baudrate(baudrate_from_config, test.dut.at1))

        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        pass

    def check_test_command(test):
        test.dut.at1.send_and_verify("AT+IPR=?", ".*OK.*")
        ipr_response = test.dut.at1.last_response
        for bitrate in test.supported_baudrates_atc:
            if str(bitrate) in ipr_response:
                pass
            else:
                test.log.error("{} bitrate not found in AT+IPR=? response".format(bitrate))
                return False
        return True


if "__main__" == __name__:
    unicorn.main()
