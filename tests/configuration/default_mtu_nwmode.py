# responsible jingxin.shen@thalesgroup.com
# Being
# TC0107110.001
import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.usim.get_imsi import dstl_get_imsi
from dstl.auxiliary.restart_module import dstl_restart

class Test(BaseTest):
	"""
    TC0107110.001 DefaultMtuNwMode
    Intention:
	To check the description in LM0006602.004: The defualt value for AT&T will be "1" and the defualt value for other MNOs will be "0".
    """
	
	def setup(test):
		dstl_detect(test.dut)
		dstl_get_imei(test.dut)
	
	def run(test):
		test.log.step('1. Insert sim card except an AT&T sim card to module.')
		test.log.step('2. Switch on module and input pin code.')
		test.expect(dstl_enter_pin(test.dut))
		if check_att_sim(test):
			return
		test.log.step('3. Check <nwmode> of MTU default value.')
		test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Mode"','\^SCFG: "GPRS/MTU/Mode",0'))
		test.log.step('4. Set at^scfg="MEopMode/Prov/AutoSelect","off"')
		test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/Prov/AutoSelect","off"', 'OK'))
		test.log.step('5. Input ati61 to list supported <provCfg>s.')
		att_name=get_att_name(test)
		test.log.step('6. Set provider profiles to an AT&T profile which list in step5 by AT^SCFG="MEopMode/Prov/Cfg",<provCfg>.')
		test.expect(test.dut.at1.send_and_verify(f'AT^SCFG="MEopMode/Prov/Cfg","{att_name}"', 'OK'))
		test.log.step('7. Reboot module and input pin code.')
		test.expect(dstl_restart(test.dut))
		test.expect(dstl_enter_pin(test.dut))
		test.log.step('8. Check <nwmode> of MTU default value.')
		test.expect(test.dut.at1.send_and_verify('at^scfg="GPRS/MTU/Mode"', '\^SCFG: "GPRS/MTU/Mode",1'))
		test.log.step('9. Set at^scfg="MEopMode/Prov/AutoSelect","on".')
		test.expect(test.dut.at1.send_and_verify('at^scfg="MEopMode/Prov/AutoSelect","on"', 'OK'))
	
	
	def cleanup(test):
		test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
		test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

def check_att_sim(test):
	test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"','OK'))
	test.expect(test.dut.at1.send_and_verify('AT+COPN', 'OK',timeout=20))
	operator_names=test.dut.at1.last_response.split('+COPN: ')
	att_plmn=[]
	for item in operator_names[1:]:
		if item.find('"AT&T"') is not -1:
			att_plmn.append(item.split(',')[0])
	dstl_get_imsi(test.dut)
	imsi = re.search(r'(\d+)', test.dut.at1.last_response).group(1)
	if '"'+imsi[0:5]+'"' in att_plmn or '"'+imsi[0:6]+'"' in att_plmn:
		test.log.error('please insert SIM,which is not AT&T')
		return True
	return False
def get_att_name(test):
	test.expect(test.dut.at1.send_and_verify('ati61', 'OK'))
	providers=test.dut.at1.last_response.splitlines()
	for item in providers:
		result=re.search(r'(.*ATT)\s+\d+',item)
		if result is not None:
			att_name=result.group(1)
			return att_name
	test.log.error('Did not find att in ati61 response.')
	return False
			
	
if "__main__" == __name__:
	unicorn.main()
