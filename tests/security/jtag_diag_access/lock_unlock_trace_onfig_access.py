#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC

import unicorn

import time

from core.basetest import BaseTest
from dstl.security import lock_unlock_trace
from dstl.network_service import register_to_network

class LockUnlcokTraceConfigAccess(BaseTest):

    def setup(test):
        test.password = ""
        test.fake_password = ""

    def run(test):
        test.log.info("1.Lock Debug access without password")
        test.expect(test.dut.dstl_lock_trace())
        test.expect(test.dut.dstl_is_trace_locked())
        test.expect(test.is_trace_locked())

        time.sleep(20)

        test.log.info("2.Unlock debug access without password")
        test.expect(not test.dut.dstl_unlock_trace())
        test.expect(test.dut.dstl_is_trace_locked())
        test.expect(test.is_trace_locked())

        test.log.info("3.Within 5 seconds, unlock debug access with correct password")
        test.expect(not test.dut.dstl_unlock_trace(test.password))
        test.expect(test.dut.dstl_is_trace_locked())
        test.expect(test.is_trace_locked())

        test.log.info("4.Wait at least 5 seconds.Unlock access with incorrect password")
        time.sleep(5)
        test.expect(not test.dut.dut.dstl_unlock_trace(test.fake_password))
        test.expect(test.dut.dstl_is_trace_locked())
        test.expect(test.is_trace_locked())

        test.log.info("5.Wait at least 5 seconds. Unlock access with incorrect password")
        time.sleep(5)
        test.expect(not test.dut.dut.dstl_unlock_trace(test.fake_password))
        test.expect(test.dut.dstl_is_trace_locked())
        test.expect(test.is_trace_locked())

        test.log.info("6. Wait at least 30 seconds. Unlock access with correct password")
        time.sleep(30)
        test.expect(test.dut.dut.dstl_unlock_trace(test.password))
        test.expect(not test.dut.dstl_is_trace_locked())
        test.expect(not test.is_trace_locked())

    def cleanup(test):
        pass

    def is_trace_locked(test):
        pass


if __name__ == "__main__":
    unicorn.main()
