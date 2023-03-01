#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0000331.001

import unicorn

from core.basetest import BaseTest

from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard import devboard
from dstl.call import switch_to_command_mode
from dstl.auxiliary import check_urc
from dstl.call import setup_voice_call

import re

class sind_service_basic_check(BaseTest):
    '''
    TC0000331.001 -- SindRssi

    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT+CRC=1", "OK"))

    def run(test):
        ok_or_error = "\s+(OK|ERROR)"
        test.log.info("Step 1. Check and enable rssi URC")
        test.expect(test.dut.at1.send_and_verify("AT^SIND=?",".*\(rssi,\(0-5,99\)\).*"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",2","\^SIND: rssi,0,[^9]+\s+"))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",1","\^SIND: rssi,1,[^9]+\s+", wait_for=ok_or_error))
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",2","\^SIND: rssi,1,[1-5]\s+"))

        test.log.info("Step 2. Check indicator rssi during voice call")
        test.expect(test.r1.at1.send_and_verify("AT+COPS?", "\+COPS: 0,\d,\".+\",[023679]", wait_for=ok_or_error, timeout=30))
        test.r1.at1.send("ATD{};".format(test.dut.sim.int_voice_nr))
        test.expect(test.dut.at1.wait_for("\+CRING: VOICE"))
        test.check_rssi_status(error_msg="No URC or incorrect URC when receiving voice call.")
        test.expect(test.dut.at1.send_and_verify("ATA", "OK", wait_for=ok_or_error))
        test.check_rssi_status(error_msg="No URC or incorrect URC when answering voice call.")
        test.log.info("connect the antenna to the DSB by Subscriber1")
        test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "ON1"))
        test.check_rssi_status(error_msg="No URC or incorrect URC when connecting the antenna to the DSB by Subscriber1.")
        test.expect(test.r1.dstl_release_call())
        test.log.info("disconnect the antenna from the DSB by Subscriber1")
        test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "OFF1"))
        test.check_rssi_status(error_msg="No URC or incorrect URC when disconnecting the antenna from the DSB by Subscriber1.")

        test.log.info("Step 3. Check indicator rssi during data call")
        test.dut.at1.send("ATD{}".format(test.r1.sim.int_data_nr))
        test.sleep(5)
        response = test.dut.at1.read()
        if "operation not supported" in response:
            test.log.info("Module does not support data call function, skipped.")
        else:
            test.log.error("Data call steps are not implemented.")
        

    def cleanup(test):
        test.expect(test.dut.dstl_release_call())
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",0","\^SIND: rssi,0,\d+\s+", wait_for="(OK|ERROR)"))

    def check_rssi_status(test, error_msg):
        test.expect(test.dut.dstl_check_urc("\+CIEV: rssi,[1-5]"), msg=error_msg)
        find_rssi = re.findall("\+CIEV: rssi,([1-5])\s+", test.dut.at1.last_response)
        if find_rssi:
            rssi_value = find_rssi[-1]
        else:
            rssi_value = "[1-5]"
        test.expect(test.dut.at1.send_and_verify("AT^SIND=\"rssi\",2","\^SIND: rssi,1," + rssi_value))
        test.expect(test.dut.at1.send_and_verify("AT+CSQ", "\+CSQ: ([0-9]|[12][0-9]|[3][01]),\d+"))


if __name__=='__main__':
    unicorn.main()
