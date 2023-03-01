# responsible: mariusz.wojcik@globallogic.com
# location: Wroclaw
# TC0104870.001

import unicorn
from copy import copy
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.gnss import gnss


class Test(BaseTest):
    """
    Basic check of switching between physical port and MUX channels.

    1. Send the "AT" command on physical port.
    2. Close physical port.
    3. Open all MUX channels.
    4. Send the "AT" command using every MUX channel.
    5. Close all MUX channels.
    6. Open physical port once again.
    7. Send the "AT" command.
    8. Close opened physical port.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step('1. Send the "AT" command on physical port.')
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))

        test.log.step('2. Close physical port.')
        test.dut.at1.close()

        test.log.step('3. Open all MUX channels.')
        open_mux_channels(test)

        test.log.step('4. Send the "AT" command using every MUX channel.')
        test.expect(test.dut.mux_1.send_and_verify("AT", ".*OK.*"))
        test.expect(test.dut.mux_2.send_and_verify("AT", ".*OK.*"))
        if test.dut.project.upper() == "SERVAL":
            test.log.info("MUX 3 on product {} is reserved for NMEA. Checking NMEA output on MUX 3.".format(test.dut.project))
            check_gns_engine(test)
        else:
            test.log.error("MUX 3 behavior is not implemented for product {}".format(test.dut.project))
            test.fail()

        test.log.step('5. Close all MUX channels.')
        close_mux_channels(test)

        test.log.step('6. Open physical port once again.')
        test.dut.at1.open()
        test.sleep(5)

        test.log.step('7. Send the "AT" command.')
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))

    def cleanup(test):
        close_mux_channels(test)
        test.log.step('8. Close opened physical port.')
        test.dut.at1.close()


def check_gns_engine(test):
    original_interface = copy(test.dut.at1)
    test.dut.at1 = test.dut.mux_1
    test.expect(test.dut.dstl_switch_on_engine())
    test.expect(test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","on"', ".*OK.*"))
    test.expect(test.dut.mux_3.wait_for('GP'))
    test.expect(test.dut.at1.send_and_verify('AT^SGPSC="Nmea/Output","off"', ".*OK.*"))
    test.expect(test.dut.dstl_switch_off_engine())
    test.dut.at1 = original_interface


def open_mux_channels(test):
    test.dut.mux_1.open()
    test.dut.mux_2.open()
    test.dut.mux_3.open()
    test.sleep(5)


def close_mux_channels(test):
    test.dut.mux_1.close()
    test.dut.mux_2.close()
    test.dut.mux_3.close()
    test.sleep(5)


if "__main__" == __name__:
    unicorn.main()
