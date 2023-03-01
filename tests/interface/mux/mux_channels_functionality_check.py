# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0095124.001

import unicorn
from core.basetest import BaseTest
from copy import copy
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.gnss import gnss
from dstl.call import switch_to_command_mode
from dstl.network_service import register_to_network
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):
    """
    Check if all supported MUX channels are available and if communication with them is possible.

    1. Connect to 2 MUX channels which supports sending AT commands and send commands on chosen MUX channels. (e.g. ATI1, AT^CICRET=SWN)
    2. Establish data connection (dial-up or ip services) on appropriate MUX channel.
    3. If supported - enable GNS engine and check if GNS frames are received correctly on appropriate MUX channel.
    """

    ORIGINAL_INTERFACE = None

    def setup(test):
        test.ORIGINAL_INTERFACE = copy(test.dut.at1)
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_enter_pin()
        test.dut.at1.close()
        test.sleep(10)

    def run(test):
        test.log.step("1. Connect to 2 MUX channels which supports sending AT commands and send commands on chosen MUX channels. (e.g. ATI1, AT^CICRET=SWN)")
        open_mux_channels(test)
        send_commands(test, test.dut.mux_1)
        send_commands(test, test.dut.mux_2)

        test.log.step("2. Establish data connection (dial-up or ip services) on appropriate MUX channel.")
        establish_data_connection(test, test.dut.mux_1)
        establish_data_connection(test, test.dut.mux_2)

        test.log.step("3. If supported - enable GNS engine and check if GNS frames are received correctly on appropriate MUX channel.")
        check_gns_engine(test, test.dut.mux_1)
        test.sleep(10)
        check_gns_engine(test, test.dut.mux_2)

    def cleanup(test):
        test.dut.at1 = test.ORIGINAL_INTERFACE
        close_mux_channels(test)
        test.dut.at1.open()
        test.sleep(10)
        test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","off"', ".*OK.*")
        test.dut.dstl_switch_off_engine()
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')


def check_gns_engine(test, device):
    test.dut.at1 = device
    test.expect(test.dut.dstl_switch_on_engine())
    test.expect(test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","on"', ".*OK.*"))
    test.expect(test.dut.mux_3.wait_for('GP'))
    test.expect(test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","off"', ".*OK.*"))
    test.expect(test.dut.dstl_switch_off_engine())
    test.dut.at1 = test.ORIGINAL_INTERFACE


def establish_data_connection(test, device):
    test.dut.at1 = device
    test.expect(test.dut.at1.send_and_verify('ATD*99#', '.*CONNECT.*', wait_for="CONNECT"))

    if not test.dut.dstl_switch_to_command_mode_by_dtr():
        test.expect(False, "Did not leave command mode using DTR toggle. Trying using +++")
        test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
    else:
        test.expect(True)

    test.dut.at1 = test.ORIGINAL_INTERFACE


def open_mux_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.dut.mux_3.open()
    test.sleep(10)


def close_mux_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.dut.mux_3.close()
    test.sleep(10)


def send_commands(test, device):
    test.expect(device.send_and_verify("AT", ".*OK.*"))
    test.expect(device.send_and_verify("ATI", ".*OK.*"))
    test.expect(device.send_and_verify("AT^SCFG?", ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
