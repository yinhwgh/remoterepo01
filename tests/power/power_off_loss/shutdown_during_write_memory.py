# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
#

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect

from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory
import time
import random


class Test(BaseTest):
    """
    1. power on with IGN
    2.The short message storage is written, read and deleted in succession for houdrous of message items.
    3.During these operations (step2), send SMSO  to shutdown the module at random intervals (between 0 and 180 seconds).
    4. After the Shutdown URC,  turn off the VBAT after a delay*.
    5. Repeat 0~4 at lease 10 times for every delay. And the delay*  would increase from 10ms to 5500ms with a step of 10ms.

    repeat 1~5 overnight or for days.

    """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CGSN", ".*OK.*"))
        test.log.step('1. Prepare module')
        test.log.step('Unlock sim pin')
        test.dut.dstl_unlock_sim()
        test.log.step('Preconfig SMS')
        test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,167,0,0", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"GSM\"", ".*OK.*"))
        test.dut.dstl_set_preferred_sms_memory('ME')
        test.dut.devboard.send_and_verify("mc:URC=off", ".*OK.*")
        test.capacity = 255
        test.max_delay = 5500

    def run(test):

        delay = 0
        while delay < test.max_delay:
            test.log.info(f'Start test with delay {delay} ms')
            for i in range(1, 31):
                test.log.info(f'Start loop {i} with delay {delay} ms')
                write_time = random.randint(30, 120)
                test.log.step(f'2. write memory by SMS for {write_time}s')
                test.write_read_delete_sms(write_time)

                test.log.step(f'3. Send SMSO to shutdown module, then turn off with vbatt after {delay} ms')
                #test.dut.at1.send_and_verify("AT^SMSO", ".*OK.*", wait_for="SHUTDOWN")
                test.dut.at1.send_and_verify("AT^SMSO", ".*OK.*")
                time_now = time.time()
                test.sleep(delay / 1000)
                test.dut.devboard.send_and_verify("mc:vbatt=off", ".*OK.*")

                time_interval = time.time() - time_now
                test.log.info(f'Time interval is {time_interval}s')
                test.sleep(2)

                test.log.step(f'4. Power on module, and repeat 2-3')
                test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
                test.sleep(2)
                test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
                test.dut.at1.wait_for('SYSSTART', 60)
                test.sleep(15)
                test.attempt(test.dut.at1.send_and_verify, "AT+CPMS=?", expect="OK", retry=5, sleep=5)
            test.log.info(f'End test with delay {delay} ms')
            delay += 10

    def cleanup(test):
        pass

    def write_read_delete_sms(test, write_duration):
        start_time = time.time()
        # write random count sms
        start_index = random.randint(1, 100)
        test.expect(dstl_select_sms_message_format(test.dut, 'Text'))
        while ((time.time() - start_time) < write_duration) and start_index < test.capacity:
            # if sms memoryy is full, delete all
            me_sms_count = test.dut.dstl_get_sms_count_from_memory()[1]
            if me_sms_count == 255:
                test.expect(test.dut.at1.send_and_verify('AT+CMGD=1,4', 'OK'))

            test.log.info(f'Write message No.{start_index}')
            test.expect(dstl_write_sms_to_memory(test.dut, f'Test SMS message Test SMS message {start_index}'))
            start_index += 1
        test.expect(test.dut.at1.send_and_verify('at+cmgl="ALL"', 'OK'))

        # delete some sms with index interval 10
        while start_index < test.capacity:
            test.log.info(f'Delete message No.{start_index}')
            test.expect(test.dut.at1.send_and_verify(f'AT+CMGD={start_index}'))
            start_index += 10
        test.expect(test.dut.at1.send_and_verify('at+cmgl="ALL"', 'OK'))


if "__main__" == __name__:
     unicorn.main()
