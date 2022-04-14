# responsible hongwei.yin@thalesgroup.com
#location: Dalian
#TC0108062.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.packet_domain import pdp_context_operation
from dstl.packet_domain import pdp_activate_deactivate
import time

class Test(BaseTest):
    """
     TC0108062.001-Ingenico_PDPContext_Activate_Deactivate_with_CGACT
    """
    def setup(test):
        test.dut.dstl_detect()
        test.context_contents = test.dut.dstl_backup_pdp_context()
        test.expect(test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*', timeout=100), critical=True)
        test.dut.dstl_clear_contexts()

    def run(test):
        test.log.step("1. Define all the PDP contexts.")
        for cid in range(7):
            test.expect(test.dut.at1.send_and_verify(f'at+cgdcont={cid+1},ipv4v6,test{cid+1}', 'OK'))
        test.log.step("2. Activate all PDP contexts using at+cgact one by one, and check state with at+cgact?")
        for cid in range(7):
            test.dut.dstl_pdp_activate(cid+1)
            test.sleep(1)
        test.log.step("3. Deactivate all PDP contexts using at+cgact one by one, and check state with at+cgact?")
        for cid in range(7):
            test.dut.dstl_pdp_deactivate(cid + 1)
        test.log.step("4. Repeat step 2-3, Stress test for 4 hours")
        for i in range(480):
            time_start = time.time()
            test.log.step("2. Activate all PDP contexts using at+cgact one by one, and check state with at+cgact?")
            for cid in range(7):
                test.dut.dstl_pdp_activate(cid + 1)
                test.sleep(1)
            test.log.step("3. Deactivate all PDP contexts using at+cgact one by one, and check state with at+cgact?")
            for cid in range(7):
                test.dut.dstl_pdp_deactivate(cid + 1)
            time_end = time.time()
            every_loop_time = time_end - time_start
            test.log.info('loop {} times cost is {}'.format(i, every_loop_time))
            if every_loop_time > 30:
                test.log.info('last loop time cost more than 30s , directly go to next loop')
            else:
                test.log.info("need to sleep {}".format(30 - every_loop_time))
                test.sleep(30 - every_loop_time)

    def cleanup(test):
        try:
            test.expect(test.dut.at1.send_and_verify('at+cgatt=0', '.*OK.*', timeout=100))
            test.dut.dstl_clear_contexts()
            for context_content in test.context_contents:
                test.expect(test.dut.at1.send_and_verify(f'at+cgdcont={context_content}', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgatt=1', '.*OK.*'))
        except Exception:
            test.expect(test.dut.dstl_restart())


if "__main__" == __name__:
    unicorn.main()