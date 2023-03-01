# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0010536.002,TC0010536.003

import time
import random

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.phonebook.phonebook_handle import *

run_duration = 86400  # 24 hours


class Test(BaseTest):
	ok_to_send = True
	capacity_sms = 0
	capacity_pb = 0
	
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
		test.log.step('get ME capacity')
		test.capacity_sms = test.dut.dstl_get_sms_memory_capacity(2)
		test.log.step('clean up ME before test')
		test.dut.dstl_delete_all_sms_messages()
		test.log.step('set phonebook storage to SM and cleanup SM')
		test.dut.dstl_clear_select_pb_storage('SM')
		test.log.step('get SM capacity')
		test.capacity_pb = test.dut.dstl_get_pb_storage_max_location('SM')
		test.dut.devboard.send_and_verify("mc:asc0?",'OK')#to test MC connection.
		return
	
	def run(test):
		start = time.time()
		test.log.info('StartTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
		while (((time.time() - start) < run_duration)):
			test.log.step('1.Write,read,delete short message storage.')
			test.log.step(
				'2.During these operations the power supply is disconnected at random intervals (between 0 and 180 seconds).')
			sms_storage_not_full = check_sms_storage(test)
			test.thread(thread_start_timer, test)
			while test.ok_to_send:
				if sms_storage_not_full:
					while test.ok_to_send and (f'+CMGW: {int(test.capacity_sms)-1}' not in test.dut.at1.last_response):
						# test.dut.dstl_write_sms_to_memory('a'*10)
						send_at(test,test.dut.at1.send,f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
						send_at(test,test.dut.at1.wait_for,'>',1)
						send_at(test,test.dut.at1.send,'aaaaaaaaaa\x1A')
						send_at(test,test.dut.at1.wait_for,'OK',1)
				i = 0
				while test.ok_to_send and i <= 254:
					send_at(test,test.dut.at1.send,f'AT+CMGR={str(i)}')
					send_at(test,test.dut.at1.wait_for,'OK',1)
					i += 1
				i=254
				while test.ok_to_send and i > 0:
					send_at(test,test.dut.at1.send,f'AT+CMGD={str(i)}')
					send_at(test,test.dut.at1.wait_for,'OK',1)
					i -= 1
			test.log.step(
				'3.Module is restarted by ignition after randomly chosen intervals (between 0 and 60 seconds).')
			power_on_and_init(test)
			
			test.log.step('4.Write,read,delete phonebook storage.')
			test.log.step('5.During these operations the power supply is disconnected at random intervals (between 0 and 180 seconds).')
			
			test.thread(thread_start_timer, test)
			while test.ok_to_send:
				i = 1
				while test.ok_to_send and i <= int(test.capacity_pb):
					send_at(test,test.dut.at1.send,f'AT+CPBW={i},"{test.dut.sim.int_voice_nr}"')
					send_at(test,test.dut.at1.wait_for,'OK',1)
					i += 1
				i = 1
				while test.ok_to_send and i <= int(test.capacity_pb):
					send_at(test,test.dut.at1.send,f'AT+CPBR={i}')
					send_at(test,test.dut.at1.wait_for,'OK',1)
					
					i += 1
				send_at(test,test.dut.at1.send,f'AT+CPBR=1,{test.capacity_pb}')
				send_at(test,test.dut.at1.wait_for,'OK',1)
				i = 1
				while test.ok_to_send and i <= int(test.capacity_pb):
					send_at(test,test.dut.at1.send,f'at+cpbw={i}')
					send_at(test,test.dut.at1.wait_for,'OK',1)
					i += 1
				send_at(test,test.dut.at1.send,f'AT+CPBR=1,{test.capacity_pb}')
				send_at(test,test.dut.at1.wait_for,'\+CME ERROR: not found',1)
			test.log.step(
				'6.Module is restarted by ignition after randomly chosen intervals (between 0 and 60 seconds).')
			power_on_and_init(test)
			test.log.step('Repeat step1 to 6 for 24hours')
		
		test.log.info('EndTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
	
	def cleanup(test):
			pass


def check_sms_storage(test):
	test.expect(test.dut.at1.send_and_verify("at+cpms?", 'OK'))
	result = re.search(r'CPMS: "\w+",\d+,\d+,"\w+",(\d+),(\d+),"\w+",\d+,\d+', test.dut.at1.last_response)
	if int(result.group(1)) < int(result.group(2)):
		return True
	elif int(result.group(1)) == int(result.group(2)):
		return False
	else:
		test.log.error('please check response of at+cpms?')


def send_at(test, fun_name, param_1=None,param_2=None):
	if test.ok_to_send:
		if param_2 == None:
			return fun_name(param_1)
		else:
			return fun_name(param_1,param_2)
	else:
		return None


def thread_start_timer(test):
	wait = random.randint(0, 180)
	test.log.step('Thread:random interval is ' + str(wait))
	test.sleep(wait)
	test.log.step('Thread:switch off power supply')
	test.dut.devboard.send("mc:vbatt=off")
	test.ok_to_send = False
	test.dut.devboard.wait_for(r'OK',timeout=3)
	return
def power_on_and_init(test):
	test.sleep(random.randint(0, 60))
	test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
	test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
	test.dut.at1.wait_for('SYSSTART', 60)
	time.sleep(5)
	test.dut.dstl_select_sms_message_format(sms_format='Text')
	test.ok_to_send = True

if (__name__ == "__main__"):
	unicorn.main()
