# responsible hongwei.yin@thalesgroup.com
#location: Dalian
#TC0108063.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
import time

class Test(BaseTest):
    """
     TC0108063.001-Ingenico_Smonp_With_Network_Change
    """
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step("1. Register module to LTE network.")
        test.expect(test.dut.dstl_register_to_lte(), critical=True)
        test.log.step("2. Monitoring Neighbour Cells.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", "4G:.*\d+,-?\d+,-?\d+,\d+,\d+,"))
        test.log.step("3. Register module to 2G network.")
        test.expect(test.dut.dstl_register_to_gsm(), critical=True)
        test.log.step("4. Monitoring Neighbour Cells.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONP", "2G:.*\d+,,-?\d+"))
        for i in range(480):
            time_start = time.time()
            test.log.step("3. Register module to 2G network.")
            test.expect(test.dut.dstl_register_to_gsm())
            test.log.step("4. Monitoring Neighbour Cells.")
            test.expect(test.dut.at1.send_and_verify("AT^SMONP", "2G:.*\d+,,-?\d+"))
            time_end = time.time()
            every_loop_time = time_end - time_start
            test.log.info('loop {} times cost is {}'.format(i, every_loop_time))
            if every_loop_time > 30:
                test.log.info('last loop time cost more than 30s , directly go to next loop')
                pass
            else:
                test.log.info("need to sleep {}".format(30 - every_loop_time))
                test.sleep(30 - every_loop_time)

    def cleanup(test):
        try:
            test.dut.at1.send_and_verify("AT+COPS=2")
            test.dut.at1.send_and_verify("AT+COPS=0")
        except Exception:
            test.expect(test.dut.dstl_restart())


if "__main__" == __name__:
    unicorn.main()