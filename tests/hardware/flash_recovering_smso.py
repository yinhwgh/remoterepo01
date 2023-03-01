# responsible: lijuan.li@thalesgroup.com
# location: Beijing
# TC0010536.002,TC0010536.003

import time
import random
import threading
import re
import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board, dstl_turn_on_vbatt_via_dev_board, \
    dstl_turn_on_igt_via_dev_board
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.get_sms_count_from_memory import dstl_get_sms_count_from_memory


class Test(BaseTest):
    def setup(test):
        test.log.step('Get DUT information')
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.log.step('set message mode to text')
        dstl_select_sms_message_format(test.dut, sms_format='Text')
        test.log.step('set sms storage to ME')
        dstl_set_preferred_sms_memory(test.dut, 'ME')
        test.log.step('get ME capacity')
        test.capacity_sms = dstl_get_sms_memory_capacity(test.dut, 2)
        test.log.step('clean up ME before test')
        dstl_delete_all_sms_messages(test.dut)
        test.dut.devboard.send_and_verify("MC:urc=off common", ".*OK.*")
        test.dut.devboard.send_and_verify("MC:time=on", ".*OK.*")
        test.wforsysstarttimer = 60
        test.modules_on = 1
        test.totaltime1 = 0
        test.totaltime2 = 0
        test.counts = 0
        test.run_duration = 86400 * 3  # 24 hours

    def smso_thread(test, start_ts, stop_ts):
        timeout = random.randint(start_ts, stop_ts)
        test.sleep(timeout)

        test.dut.at2.send('AT^SMSO')
        test.modules_on = 0
        test.dut.devboard.wait_for('PWRIND: 1')

        try:
            response = test.dut.devboard.last_response
            begin_str = 'ASC1: AT^SMSO'
            end_str = 'PWRIND: 1'
            index1 = response.index(begin_str) - 11
            index2 = response.index(end_str) + len(end_str)
            response = response[index1:index2]
            # test.log.info('*****response is\n' + response)
            response = response.replace("\n", "")
            response_list = response.split()
            new_response = ''.join(response_list)
            test.log.info('*****new response is\n' + new_response)
            startTime = re.search(r'(\d+)>ASC1:AT\^SMSO', new_response).group(1)
            estimatedTime1 = re.search(r'(\d+)>ASC1:\^SHUTDOWN', new_response).group(1)
            interval1 = int(estimatedTime1) - int(startTime)
            estimatedTime2 = re.search(r'(\d+)>URC:PWRIND:1', new_response).group(1)
            interval2 = int(estimatedTime2) - int(estimatedTime1)

            test.log.info("Time spent for URC SHUTDOWN : {}".format(interval1))
            test.log.info("Time spent from SHUTDOWN to Power off : {}".format(interval2))

            test.counts = test.counts + 1
            test.totaltime1 = test.totaltime1 + interval1
            test.totaltime2 = test.totaltime2 + interval2
        except:
            test.log.error("Can't count time this loop, please check the log")

        test.power_on_and_init()

    def run(test):
        test.dut.devboard.send('mc:gpiocfg=3,outp')
        test.sleep(0.3)
        test.dut.devboard.send_and_verify('mc:gpio3=1')
        test.sleep(0.3)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.sleep(test.wforsysstarttimer)
        test.dut.at1.send('ATi')
        test.dut.devboard.send_and_verify('mc:pwrind?')

        start = time.time()
        test.log.info('StartTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
        loop = 0
        while (time.time() - start) < test.run_duration:
            loop += 1
            test.log.info("Loop {} :".format(loop))
            test.log.step('1.Write,read,delete short message storage.')
            test.log.step(
                '2.During these operations the power supply is disconnected at random intervals (between 0 and 180 seconds).')
            test.log.step('Enter sim pin')
            test.expect(dstl_enter_pin(test.dut))
            test.log.step('set message mode to text')
            dstl_select_sms_message_format(test.dut, sms_format='Text')
            sms_storage_not_full = test.check_sms_storage()
            test.log.step("Start smso thread. ")
            test.smso_thr = threading.Thread(target=test.smso_thread, args=(0, 180,))
            test.smso_thr.start()
            while test.modules_on == 1:
                if sms_storage_not_full:
                    while (test.modules_on == 1) and \
                            (f'+CMGW: {int(test.capacity_sms)}' not in test.dut.at1.last_response):
                        test.send_at(test.dut.at1.send, f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
                        test.send_at(test.dut.at1.wait_for, '>', 1)
                        test.send_at(test.dut.at1.send, 'aaaaaaaaaa\x1A')
                        test.send_at(test.dut.at1.wait_for, 'OK', 1)

                i = 1
                while test.modules_on == 1 and i <= int(test.capacity_sms):
                    test.send_at(test.dut.at1.send, f'AT+CMGR={str(i)}')
                    test.send_at(test.dut.at1.wait_for, 'OK', 1)
                    i += 1

                i = int(test.capacity_sms)
                while test.modules_on == 1 and i > 0:
                    test.send_at(test.dut.at1.send, f'AT+CMGD={str(i)}')
                    test.send_at(test.dut.at1.wait_for, 'OK', 1)
                    i -= 1

            test.smso_thr.join()
            # test.sleep(500)
        test.log.info('EndTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

    def cleanup(test):
        averagetime1 = test.totaltime1 / test.counts
        averagetime2 = test.totaltime2 / test.counts

        test.log.info("Average time for URC pop is {}".format(averagetime1))
        test.log.info("Average time for power down is {}".format(averagetime2))

    def check_sms_storage(test):
        sms_capacity = dstl_get_sms_memory_capacity(test.dut, 2)
        sms_count = dstl_get_sms_count_from_memory(test.dut)[1]

        print("sms capacity: {}".format(sms_capacity))
        print("sms_count: {}".format(sms_count))

        return_result = False
        if int(sms_count) < int(sms_capacity):
            return_result = True
        elif int(sms_count) == int(sms_capacity):
            return_result = False
        else:
            test.log.error('Error to get sms storage status')

        return return_result

    def send_at(test, fun_name, param_1=None, param_2=None):
        return_result = None
        if test.modules_on == 1:
            if param_2 is None:
                return_result = fun_name(param_1)
            else:
                return_result = fun_name(param_1, param_2)
        return return_result

    def power_on_and_init(test):
        test.sleep(random.randint(0, 60))
        dstl_turn_off_vbatt_via_dev_board(test.dut)
        test.sleep(5)
        dstl_turn_on_vbatt_via_dev_board(test.dut)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.dut.at1.wait_for('SYSSTART', 60)
        time.sleep(5)
        dstl_select_sms_message_format(test.dut, sms_format='Text')
        test.modules_on = 1


if __name__ == "__main__":
    unicorn.main()
