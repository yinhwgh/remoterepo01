#responsible: jin.li@thalesgroup.com
#location: Dalian
#TC0105036.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.serial_interface import config_baudrate
import re

class Test(BaseTest):
    '''
    "TC0105036.001
     Intention:AT cmd will not crash or block the UART interface before ^SYSSTART for all support baudrate.
     subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1. Check if test command response contains all supported bite rates.")
        test.expect(test.dut.at1.send_and_verify('AT+IPR=?', 'OK'))
        test.log.step("2. Set another bit rate.")
        other_bitrate = re.findall("(\d+)",test.dut.at1.last_response)
        for i in range(len(other_bitrate)):
            test.expect(test.dut.dstl_set_baudrate(other_bitrate[i],test.dut.at1))
            test.expect(test.dut.at1.send_and_verify("at+cfun=1,1", "OK"))
            character_set_loop = ("at", "AT","*#%&")
            for i in range(0, len(character_set_loop)):
                char_set = character_set_loop[i]
                test.dut.at1.send(f"{char_set}")
                test.sleep(5)

    def cleanup(test):
        test.expect(test.dut.dstl_set_baudrate('115200',test.dut.at1))


if '__main__' == __name__:
    unicorn.main()
