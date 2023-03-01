# responsible: marcin.drozd@globallogic.com
# location: Wroclaw
# TC0104599.002

import unicorn
from core.basetest import BaseTest
from dstl.serial_interface.config_baudrate import dstl_get_supported_baudrate_list
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from dstl.serial_interface.config_baudrate import dstl_get_baudrate
from dstl.serial_interface.config_baudrate import dstl_find_current_baudrate
from dstl.identification.check_identification_ati import dstl_check_ati1_response
from dstl.auxiliary.init import dstl_detect


class Test(BaseTest):
    """
    Checking functionality of bitrate AT+IPR on Linux OS
    """

    def setup(test):
        test.expect(dstl_detect(test.dut))

    def run(test):
        test.log.step("1. Check supported bitrates AT+IPR=?")

        supported_baudrates = test.expect(dstl_get_supported_baudrate_list(test.dut))
        for bitrate in supported_baudrates:

            test.log.step("2. Set supported bitrate on module. bitrate {}".format(bitrate))
            test.expect(dstl_set_baudrate(test.dut, bitrate, test.dut.at1))
            test.expect(dstl_get_baudrate)

            test.log.step("3. Send some AT commands e.g. AT, ATI")
            test.expect(dstl_check_ati1_response(test.dut))

            test.log.step("4. Repeat steps 2-3 increasing bitrate value according with "
                          "documentation and finish on the highest value.")

        test.log.step('5. Set AT+IPR=115200.')
        test.expect(dstl_set_baudrate(test.dut, 115200, test.dut.at1))

    def cleanup(test):
        test.expect(dstl_find_current_baudrate(test.dut, [], test.dut.at1))
        test.expect(dstl_set_baudrate(test.dut, 115200, test.dut.at1))


if "__main__" == __name__:
    unicorn.main()
