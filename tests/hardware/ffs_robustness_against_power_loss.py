# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0094735.001,TC0094735.002

import time
import random

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.security.lock_unlock_sim import dstl_unlock_sim

run_duration = 5400  # 1.5hours

class Test(BaseTest):
	ok_to_send = True
	
	def setup(test):
		test.log.step('Get DUT information')
		test.dut.dstl_detect()
		test.dut.dstl_get_imei()
		test.log.step('unlock sim pin')
		test.dut.dstl_unlock_sim()
		test.log.step('set message mode to text')
		test.dut.dstl_select_sms_message_format(sms_format='Text')
		test.log.step('set sms storage to ME')
		test.dut.dstl_set_preferred_sms_memory('ME')
		test.log.step('clean up ME before test')
		test.dut.dstl_delete_all_sms_messages()
		test.dut.devboard.send_and_verify("mc:asc0?", 'OK')  # to test MC connection.
		return
	
	def run(test):
		for loop in range(1,31):
			test.log.step('Repeat times '+str(loop))
			start = time.time()
			test.log.info('StartTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
			while (((time.time() - start) < run_duration)):
				test.log.step('1.1 Switch off power supply during module is in idle state.')
				thread_switch_off_power_supply(test)
				test.log.step('1.2 Switch on power supply.')
				power_on_and_init(test)
				
				test.log.step('2.1 Switch off power supply during writing SMS into module memory in loop.')
				test.thread(thread_switch_off_power_supply, test)
				while test.ok_to_send:
					send_at(test, test.dut.at1.send, f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
					send_at(test, test.dut.at1.wait_for, '>', 1)
					send_at(test, test.dut.at1.send, 'aaaaaaaaaa\x1A')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
				test.log.step('2.2 Switch on power supply.')
				power_on_and_init(test)
				
				test.log.step('3.1 Switch off power supply during erasing SMS from module memory..')
				test.thread(thread_switch_off_power_supply, test)
				i = 1
				while test.ok_to_send and i < 255:
					send_at(test, test.dut.at1.send, f'AT+CMGD={str(i)}')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
					i += 1
				test.log.step('3.2 Switch on power supply.')
				power_on_and_init(test)
				test.dut.dstl_delete_all_sms_messages()
				
				test.log.step('4.1 Switch off power supply during module is in idle state.')
				thread_decrease_power_supply(test)
				test.log.step('4.2 Switch on power supply.')
				power_on_and_init(test)
				
				test.log.step('5.1 Switch off power supply during writing SMS into module memory in loop.')
				test.thread(thread_decrease_power_supply, test)
				while test.ok_to_send:
					send_at(test, test.dut.at1.send, f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
					send_at(test, test.dut.at1.wait_for, '>', 1)
					send_at(test, test.dut.at1.send, 'aaaaaaaaaa\x1A')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
				test.log.step('5.2 Switch on power supply.')
				power_on_and_init(test)
				
				test.log.step('6.1 Switch off power supply during erasing SMS from module memory..')
				test.thread(thread_decrease_power_supply, test)
				i = 1
				while test.ok_to_send and i < 255:
					send_at(test, test.dut.at1.send, f'AT+CMGD={str(i)}')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
					i += 1
				test.log.step('6.2 Switch on power supply.')
				power_on_and_init(test)
				test.dut.dstl_delete_all_sms_messages()
			test.log.info('EndTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		
	def cleanup(test):
		pass

def send_at(test, fun_name, param_1=None, param_2=None):
	if test.ok_to_send:
		if param_2 == None:
			return fun_name(param_1)
		else:
			return fun_name(param_1, param_2)
	else:
		return None


def thread_switch_off_power_supply(test):
	wait = random.randint(0, 40)
	test.log.step('Thread:Sleep time is ' + str(wait))
	test.sleep(wait)
	test.log.step('Thread:switch off power supply')
	test.dut.devboard.send("mc:vbatt=off")
	test.ok_to_send = False
	test.dut.devboard.wait_for(r'OK', timeout=3)
	test.log.step('Thread:power supply is disconnected')
	return

def thread_decrease_power_supply(test):
	wait = random.randint(0, 10)
	test.log.step('Thread:Sleep time is ' + str(wait))
	test.sleep(wait)
	test.log.step('Thread:decrease power supply')
	voltage=4500
	while voltage>0:
		test.dut.devboard.send_and_verify(f"mc:vbatt={voltage}",'OK')
		if 'URC:  VEXT: 0' in test.dut.devboard.last_response:
			test.ok_to_send = False
			break
		voltage-=100
	test.log.step('Thread:power supply is disconnected')
	return

def power_on_and_init(test):
	time.sleep(3)
	test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
	test.dut.devboard.send_and_verify("mc:vbatt=3800", ".*OK.*")
	test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
	test.dut.at1.wait_for('SYSSTART', 60)
	time.sleep(5)
	test.dut.dstl_select_sms_message_format(sms_format='Text')
	test.ok_to_send = True
	return

if (__name__ == "__main__"):
	unicorn.main()
