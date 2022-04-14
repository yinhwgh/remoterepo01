#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0105597.001
#Hints:
#ntp_address should be defined in local.cfg currently,shuch as ntp_address="10.163.27.30"
#apn should be defined in local.cfg currently,shuch as apn="internet"
import unicorn
import re

from core.basetest import BaseTest
from tests.rq6 import smart_meter_init_module_normal_flow
from dstl.serial_interface.config_baudrate import dstl_set_baudrate


class Test(BaseTest):
    def setup(test):
        test.expect(test.dut.at1.send_and_verify('ATV1', ".*OK|.*0"))
        test.expect(test.dut.at1.send_and_verify('ATE1', ".*OK|.*0"))


    def run(test):
        test.log.step('1.try all possible bit rate,and restore it to default value.')
        test.dut.at1.reconfigure({"baudrate": 115200})
        rate_list = ["300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "230400", "460800",
                     "921600"]
        for rate in rate_list:
            test.expect(test.dut.dstl_set_baudrate(rate, test.dut.at1))
            test.expect(test.dut.dstl_set_baudrate("115200", test.dut.at1))
        test.log.step('2.try all possible character framing,and restore it to default value.')
        icf_format_list=['1','2,0','2,1','5,0','5,1']
        for icf_format in icf_format_list:
            test.expect(test.dut.at1.send_and_verify('AT+ICF='+icf_format, "OK"))
            test.expect(test.dut.at1.send_and_verify('AT+ICF=3', "OK"))

        test.log.step('3.try all possible flow control,and restore it to default value.')
        flow_control_list=['0','1','2']
        for n in flow_control_list:
            test.expect(test.dut.at1.send_and_verify('AT\Q'+n, "OK"))
            test.expect(test.dut.at1.send_and_verify('AT\Q3', "OK"))


    def cleanup(test):
        test.expect(test.dut.dstl_set_baudrate("115200", test.dut.at1))
        test.expect(test.dut.at1.send_and_verify('AT+ICF=3', "OK"))
        test.expect(test.dut.at1.send_and_verify('AT\Q3', "OK"))



if "__main__" == __name__:
    unicorn.main()
