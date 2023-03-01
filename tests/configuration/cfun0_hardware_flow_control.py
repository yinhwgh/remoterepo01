#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0085392.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.serial_interface import serial_interface_flow_control
from dstl.network_service import register_to_network
from dstl.sms import sms_functions


class Test(BaseTest):
    """
    TC0085392.001 -  TpCfun0hardwareFlowControl
    Checking the functionality of CFUN=0 when Hardware Flow Control is used.
    Subscripbers: dut, remote module
    author: lei.chen@thalesgroup.com
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        # Enable hardware flow control
        test.expect(test.dut.dstl_check_flow_control_number_after_set('3', '3'))
        # Register both modules to network
        test.expect(test.dut.dstl_register_to_network(), critical=True)
        test.expect(test.r1.dstl_register_to_network(), critical=True)

    def run(test):
        test.expect(test.dut.at1.send_and_verify("at+creg=1", "OK"))
        # Enable sms URC, should be replaced to DSTL in future
        test.expect(test.dut.at1.send_and_verify("at+cnmi=2,1", "OK"))
        test.expect(test.dut.at1.connection.cts, msg="CTS line should be enable before CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+cfun=0", "OK"))
        test.sleep(1)
        test.expect(not test.dut.at1.connection.cts, msg="CTS line should be disabled when CFUN:0")
        test.expect(test.r1.dstl_send_sms_message(test.dut.sim.nat_voice_nr))
        test.expect(test.dut.at1.wait_for("\+CMTI:.*"))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify("AT+CREG?", "\+CREG: \d,1"))
        test.expect(test.dut.at1.send_and_verify("AT+CFUN?", "\+CFUN: 1"))
        test.expect(test.dut.at1.connection.cts, msg="CTS line should be activated by sms")

    def cleanup(test):
        test.dut.at1.reopen()
        test.sleep(1)
        test.dut.at1.send("AT")
        test.dut.at1.reopen()
        test.expect(test.dut.dstl_check_flow_control_number_after_set('0', '0'))


if "__main__" == __name__:
    unicorn.main()
