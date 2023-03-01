# author: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0105058.003

import unicorn
import os
import re
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import *
from dstl.packet_domain.start_public_IPv4_data_connection import *
dict_backup = {'mtu_mode': '', 'mtu_size': '', 'usb_fallback': '', 'service_set_number': ''}
mtu_size={'min': '1280', 'default': '1430', 'max': '1500'}
class Test(BaseTest):
	"""Intention:
	Test intention is to check functionality of different MTU size during WWAN session with ping execution on Linux"""
	
	def setup(test):
		if check_system() == 'Linux':
			test.log.info('PC OS is Linux.')
		else:
			test.log.error('TC is Linux only.')
			os._exit(1)
		test.log.step('product detect.')
		dstl_detect(test.dut)
		test.log.step('backup settings.')
		backup_setting(test)
	
	def run(test):
		test.log.step('1.New setting:usb_fallback=2,service_set_number=1,mtu_mode=1,mtu_size=1430')
		new_setting(test)
		step2_to_step6(test,mtu_size['default'])
		test.log.step('7.Setting mtu_size=1280')
		test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Size",'+mtu_size['min']), 'OK')
		test.log.step('8.Repeat step2 to step6.')
		step2_to_step6(test, mtu_size['min'])
		test.log.step('9.Setting mtu_size=1500')
		test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Size",' + mtu_size['max']), 'OK')
		test.log.step('10.Repeat step2 to step6.')
		step2_to_step6(test, mtu_size['max'])
	
	def cleanup(test):
		test.log.step('restore settings.')
		restore_setting(test)
		pass

def step2_to_step6(test,size):
	test.log.step('2.Restart module')
	dstl_restart(test.dut)
	test.log.step('3.Enter pin and check if the setting is same with step1')
	dstl_enter_pin(test.dut)
	check_setting(test,size)
	test.log.step('4.Module register on network and establish WWAN connection')
	dstl_register_to_network(test.dut)
	test.expect(test.dut.at1.send_and_verify('at^swwan=1,1'), 'OK')
	time.sleep(20)
	set_linux_wwan_device()
	test.log.step('5.Ping host with command "ping -s <packet size> -M do <destination address>"')
	ping_execution(test, size)
	test.log.step('6.Release wwan connection')
	test.expect(test.dut.at1.send_and_verify('at^swwan=0,1'), 'OK')

def set_linux_wwan_device():
	val = os.popen('ifconfig -a')
	for x in val.readlines():
		a = re.search('(enx\w+):\s', x)
		if a:
			device_name = a.group(1)
		print(x)
	print('wwan device name is: '+device_name)
	os.system(f'sudo dhclient -i {device_name}')
	val = os.popen(f'123')
	for x in val.readlines():
		print(x)
	return
def backup_setting(test):
	test.expect(test.dut.at1.send_and_verify('at^scfg?'), 'OK')
	dict_backup['mtu_mode'] = re.search('"GPRS/MTU/Mode",(\d)', test.dut.at1.last_response).group(1)
	dict_backup['mtu_size'] = re.search('"GPRS/MTU/Size",(\d+)', test.dut.at1.last_response).group(1)
	#test.expect(test.dut.at1.send_and_verify('AT^STEST="USB/EnumFallback"'), 'OK')
	#dict_backup['usb_fallback'] = re.search('\^STEST: "USB/EnumFallback", (\d),', test.dut.at1.last_response).group(1)
	test.expect(test.dut.at1.send_and_verify('AT^SSRVSET= "actSrvSet"'), 'OK')
	dict_backup['service_set_number'] = re.search('\^SSRVSET: (\d)', test.dut.at1.last_response).group(1)
	return


def new_setting(test):
	#test.expect(test.dut.at1.send_and_verify('AT^STEST="USB/EnumFallback",2'), 'OK')
	test.expect(test.dut.at1.send_and_verify('AT^SSRVSET= "actSrvSet",1'), 'OK')
	test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Mode",1'), 'OK')
	test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Size",'+mtu_size['default']), 'OK')
	return


def check_setting(test,size):
	#test.expect(test.dut.at1.send_and_verify('AT^STEST="USB/EnumFallback"'), 'OK')
	#test.expect(re.search('\^STEST: "USB/EnumFallback", 2, 2', test.dut.at1.last_response))
	test.expect(test.dut.at1.send_and_verify('AT^SSRVSET= "actSrvSet"'), 'OK')
	test.expect(re.search('\^SSRVSET: 1', test.dut.at1.last_response))
	test.expect(test.dut.at1.send_and_verify('at^scfg?'), 'OK')
	test.expect(re.search('"GPRS/MTU/Mode",1', test.dut.at1.last_response))
	test.expect(re.search('"GPRS/MTU/Size",'+size, test.dut.at1.last_response))


def ping_execution(test, size):
	try:
		ip_address = test.tcp_echo_server_ipv4
	except AttributeError:
		ip_address = test.ssh_server.host
	for j in range (1,3):
		if j==1:
			packet_size = int(size) - 28
			expect_result = 'OK'
		else:
			packet_size = int(size) - 27
			expect_result = 'NOK'
		test.log.info('Ping on Linux with packet size ' + str(packet_size) + ' , expect ' + expect_result + '.')
		for i in range(0, 3):
			result = os.system(f'ping -M do -c 10 -s {packet_size} {ip_address}')
			if expect_result is 'OK':
				if result == 0:
					test.log.info('Ping execute ok')
					break
				else:
					if i == 2:
						test.expect(False)
						test.log.error('Ping should be ok')
			else:
				if result == 0:
					test.expect(False)
					test.log.error('Ping should be failed')
					break
				else:
					test.log.info('Ping execute failed')


def restore_setting(test):
	#test.expect(test.dut.at1.send_and_verify('AT^STEST="USB/EnumFallback",' + dict_backup['usb_fallback']), 'OK')
	test.expect(test.dut.at1.send_and_verify('AT^SSRVSET= "actSrvSet",' + dict_backup['service_set_number']), 'OK')
	test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Mode",' + dict_backup['mtu_mode']), 'OK')
	test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Size",' + dict_backup['mtu_size']), 'OK')


if '__main__' == __name__:
	unicorn.main()


