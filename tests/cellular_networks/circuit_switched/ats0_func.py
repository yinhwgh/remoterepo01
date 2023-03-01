# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0000127.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call.setup_voice_call import dstl_is_data_call_supported

import time
import re


class Test(BaseTest):
	def setup(test):
		test.expect(test.dut.dstl_restart())
		test.dut.dstl_detect()
		test.expect(test.dut.dstl_register_to_network())
		test.expect(test.r1.dstl_register_to_network())

	def run(test):
		test.log.step("1.Check default values: ATS0?")
		test.expect(test.dut.at1.send_and_verify("ats0?", "000"))
		
		test.log.step("2. Check all correct values")
		for i in range(0,256):
			if str(i).__len__() == 1:
				test.expect(test.dut.at1.send_and_verify("ATS0=00"+str(i), "OK"))
				test.expect(test.dut.at1.send_and_verify("ATS0?", "00" + str(i)))
			elif str(i).__len__() == 2:
				test.expect(test.dut.at1.send_and_verify("ATS0=0" + str(i), "OK"))
				test.expect(test.dut.at1.send_and_verify("ATS0?", "0" + str(i)))
			else:
				test.expect(test.dut.at1.send_and_verify("ATS0=" + str(i), "OK"))
				test.expect(test.dut.at1.send_and_verify("ATS0?", str(i)))
				
		test.log.step("3. Set value t=1")
		test.expect(test.check_ring_number(1))
		
		test.log.step("4. Set value t=2")
		test.expect(test.check_ring_number(2))

		test.log.step("5. Set value t=5")
		test.expect(test.check_ring_number(5))
		
		test.log.step("6. Test wrong parameters:")
		wrong_values=['-1','256','*','at','^','\\','=','+']
		test.expect(test.dut.at1.send_and_verify("at+cmee=2", "OK"))
		for item in wrong_values:
			test.expect(test.dut.at1.send_and_verify("ats0="+item, "\+CME ERROR:.*"))

	
	def cleanup(test):
		test.log.step("7.Restore default value with ats0=0")
		test.expect(test.dut.at1.send_and_verify("ATS0=0", "OK"))
		test.expect(test.dut.at1.send_and_verify("at&v", "S0:000"))
		
	def check_ring_number(test,expect_value):
		test.expect(test.dut.at1.send_and_verify("ATS0=00"+str(expect_value), "OK"))
		test.expect(test.dut.at1.send_and_verify("ATS0?", "00"+str(expect_value)))
		test.expect(test.r1.at1.send_and_verify('atd{};'.format(test.dut.sim.nat_voice_nr), 'OK'))
		test.attempt(test.r1.at1.send_and_verify, "AT+CLCC", expect="\+CLCC: 1,0,0,.*", retry=10, sleep=5)
		test.dut.at1.read()
		ring_number = re.findall("RING", test.dut.at1.last_response).__len__()
		test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,.*"))
		test.expect(test.dut.at1.send_and_verify("ATH", "OK"))
		if ring_number != expect_value:
			test.log.error('Number of ring is wrong')
			return False
		else:
			return True
		
		
			


if "__main__" == __name__:
	unicorn.main()

