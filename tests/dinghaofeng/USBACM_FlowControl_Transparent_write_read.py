#responsible: hongwei.yin@thales.com
#location: Dalian
#TC0108423.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses

data_1500 = dstl_generate_data(1500)


class Test(BaseTest):
    """Intention:
        Basic check the USB ACM flow control in transparent mode."""

    def setup(test):
        dstl_detect(test.dut)

    def run(test):
        # define the number of loops
        loops = 1000
        for l in range(loops):
            test.log.info(f"This is in repeat{l + 1} loop !")
            test.log.step("1) Config module as a TCP transparent client")
            test.expect(test.dut.at1.send_and_verify('AT^SISS=1,srvType,"Socket"', ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT^SISS=1,conId,1', ".*OK.*"))
            test.expect(
                test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://114.55.6.216:50000;etx;timer=200"', ".*OK.*"))

            test.log.step("2) Open service and connect server.")
            test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT^SISO=1', 'SISW', wait_for='SISW'))

            test.log.step("3) Send data to the server :1500 characters.")
            test.expect(test.dut.at1.send_and_verify('AT^SIST=1', "CONNECT", wait_for="CONNECT"))
            start_time = time.time()
            test.dut.at1.send(data_1500, end='')

            test.log.step("4) Check data size from the remote server.")
            test.expect(test.dut.at1.wait_for(data_1500), critical=True)
            end_time = time.time()
            echo_time = end_time - start_time
            print('echo_time is: '+str(echo_time))
            test.sleep(3)
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

            test.log.step("5) Close the service.")
            test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
