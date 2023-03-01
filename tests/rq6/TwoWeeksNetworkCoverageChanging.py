# responsible: hongwei.yin@thalesgroup.com
# location: Dalian
# TC0087756.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.call.setup_voice_call import dstl_voice_call_by_number, dstl_release_call
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_check_network_status
import time
import datetime


class Test(BaseTest):
    """
       TC0087756.001 - TwoWeeksNetworkCoverageChanging
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.sleep(2)

    def run(test):
        now_time = datetime.datetime.now()
        while datetime.datetime.now() <= now_time+datetime.timedelta(days=14):
            main_process(test)
            print("runtime has elapsed:")
            print(datetime.datetime.now()-now_time)

    def cleanup(test):
        pass


def main_process(test):
    test.log.step("1. Attached first module to the network")
    test.expect(test.dut.dstl_register_to_network())

    test.log.step("2. Make a voice call to second module")
    test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr, "OK"))

    test.log.step("3. After 30[s] release established connection")
    test.sleep(30)
    test.expect(test.dut.dstl_release_call())

    test.log.step("4. Stop any activities for 30 min, but check periodically (every 1 min) if module is attached")
    for i in range(30):
        test.expect(test.dut.dstl_check_network_status())
        test.sleep(60)

    test.log.step("5.  Using McTest disconnect antenna(airplane mode instead)")
    time_start = time.time()
    test.dut.at1.send("AT+CFUN=4")
    test.expect(test.dut.at1.wait_for('^SYSSTART AIRPLANE MODE', 300), critical=True)
    time_end = time.time()
    every_loop_time = time_end - time_start
    test.sleep(1800 - every_loop_time)

    test.log.step("6.  Check periodically (every 1 min) if module is not attached to the network")
    for i in range(30):
        test.expect(test.dut.at1.send_and_verify("at+creg?", "\+CREG:\d,0"))
        test.sleep(60)

    test.log.step("7.  Connect antenna back to the module (after 30 min)")
    time_start = time.time()
    test.dut.at1.send("AT+CFUN=1")
    test.expect(test.dut.at1.wait_for('^SYSSTART', 300), critical=True)
    time_end = time.time()
    every_loop_time = time_end - time_start
    test.sleep(1800 - every_loop_time)


if "__main__" == __name__:
    unicorn.main()
