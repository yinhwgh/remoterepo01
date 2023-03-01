#responsible: agata.mastalska@globallogic.com
#location: Wroclaw
#TC0104601.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.serial_interface import config_baudrate

class Test(BaseTest):
    """
    TC0104601.001 Asc0IprBasic_Linux
    Checking basic of AT+IPR command on Linux OS
    responsible: agata.mastalska@globallogic.com
    location: Wroclaw
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step('1. Check that test command response contains all supported bitrates. Use AT+IPR=?')
        atspec_bitrates = test.dut.dstl_get_supported_baudrate_list_atspec()
        test.expect(atspec_bitrates == test.dut.dstl_get_supported_baudrate_list())
        test.log.step('2. Check read command using AT+IPR?')
        test.expect(test.dut.at1.send_and_verify('at+ipr?', 'OK', timeout=30))
        test.log.step('3. Set another bitrate using e.g AT+IPR=230400')
        test.expect(test.dut.dstl_set_baudrate('230400',test.dut.at1))
        test.os.execute('stty -F {} 230400'.format(test.dut.at1.port))
        test.sleep(2)
        test.expect("230400" == test.dut.dstl_get_baudrate(test.dut.at1))
        test.log.step('5. Send "AT" command.')
        test.expect(test.dut.at1.send_and_verify('at', 'OK', timeout=30))
        test.log.step('6. Set AT+IPR=115200.')
        test.expect(test.dut.dstl_set_baudrate('115200',test.dut.at1))
        test.log.step('7. Set appropriate baudrate in Terminal.')
        test.os.execute('stty -F {} 115200'.format(test.dut.at1.port))

    def cleanup(test):
        test.expect(test.dut.dstl_set_baudrate('115200',test.dut.at1))
        test.os.execute('stty -F {} 115200'.format(test.dut.at1.port))


if "__main__" == __name__:
    unicorn.main()
