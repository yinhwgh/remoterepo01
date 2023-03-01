# responsible: lijuan.li@thalesgroup.com
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
#run_duration = 1800  # 24 hours

class Test(BaseTest):

	def check_timing(test, teststep="", maxduration=10):
		if teststep == "":
			teststep = "general time measuring"

		time2 = time.perf_counter()
		# print("T1", time1, "T2", time2, "diff", (time2-time1) )
		duration = time2 - test.time1
		resultmsg = teststep, "was: {:.1f} sec.".format(duration)
		if duration > maxduration:
			resultmsg = resultmsg, "is bigger than " + str(maxduration) + " sec. - FAILED"
			test.log.critical(resultmsg)
			return -1
		else:
			resultmsg = resultmsg, "is lower than " + str(maxduration) + " sec. as expected."
			test.log.info(resultmsg)
		return 0

	ok_to_send = True
	capacity_sms = 0
	wforsysstarttimer = 60
	time1 = 0
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
		test.dut.devboard.send_and_verify("mc:asc0?",'OK')#to test MC connection.
		# enable URCs on MCT to see which serial lines are changing
		test.dut.devboard.send_and_verify('mc:URC=SER')
		test.dut.devboard.send_and_verify('mc:URC=PWRIND')
		test.dut.devboard.send_and_verify('mc:URC=on')

		return

	def run(test):

		test.dut.devboard.send('mc:gpiocfg=3,outp')
		test.sleep(0.3)
		test.dut.devboard.send_and_verify('mc:gpio3=1')
		test.sleep(0.3)
		test.dut.dstl_turn_on_igt_via_dev_board()
		test.sleep(test.wforsysstarttimer)
		test.dut.at1.send('ATi')
		test.dut.devboard.send_and_verify('mc:pwrind?')

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
					test.log.step('unlock sim pin')
					test.dut.dstl_unlock_sim()
					test.log.step('set message mode to text')
					test.dut.dstl_select_sms_message_format(sms_format='Text')
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

			test.log.step('Repeat step1 to 3 for 24hours')
		
		test.log.info('EndTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

		start = time.time()
		test.log.info('StartTime is : ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
		while (((time.time() - start) < run_duration)):
			test.log.step('1.Write,read,delete short message storage.')
			test.log.step(
				'2.During these operations the power supply is disconnected at random intervals (between 0 and 180 seconds).')
			sms_storage_not_full = check_sms_storage(test)
			test.thread(thread_start_timer2, test)
			while test.ok_to_send:
				if sms_storage_not_full:
					test.log.step('unlock sim pin')
					test.dut.dstl_unlock_sim()
					test.log.step('set message mode to text')
					test.dut.dstl_select_sms_message_format(sms_format='Text')
					while test.ok_to_send and (
							f'+CMGW: {int(test.capacity_sms) - 1}' not in test.dut.at1.last_response):
						# test.dut.dstl_write_sms_to_memory('a'*10)
						send_at(test, test.dut.at1.send, f'AT+CMGW="{test.dut.sim.int_voice_nr}"')
						send_at(test, test.dut.at1.wait_for, '>', 1)
						send_at(test, test.dut.at1.send, 'aaaaaaaaaa\x1A')
						send_at(test, test.dut.at1.wait_for, 'OK', 1)
				i = 0
				while test.ok_to_send and i <= 254:
					send_at(test, test.dut.at1.send, f'AT+CMGR={str(i)}')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
					i += 1
				i = 254
				while test.ok_to_send and i > 0:
					send_at(test, test.dut.at1.send, f'AT+CMGD={str(i)}')
					send_at(test, test.dut.at1.wait_for, 'OK', 1)
					i -= 1
			test.log.step(
				'3.Module is restarted by ignition after randomly chosen intervals (between 0 and 60 seconds).')
			power_on_and_init(test)

			test.log.step('Repeat step1 to 3 for 24hours')

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
	test.dut.devboard.send('mc:gpio3=0')
	test.time1 = time.perf_counter()
	test.expect(test.dut.devboard.wait_for(".*PWRIND: 1.*", timeout=5))
	ret = test.check_timing("4. GPIO-Shutdown without PIN", maxduration=1)
	test.dut.devboard.send_and_verify('mc:gpio3=1')
	test.ok_to_send = False
	test.dut.devboard.wait_for(r'OK',timeout=3)
	return


def power_on_and_init(test):
	test.sleep(random.randint(0, 60))
	test.dut.devboard.send_and_verify("mc:vbatt=off", ".*OK.*")
	test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
	test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
	test.dut.at1.wait_for('SYSSTART', 60)
	time.sleep(5)
	test.dut.dstl_select_sms_message_format(sms_format='Text')
	test.ok_to_send = True

if (__name__ == "__main__"):
	unicorn.main()
