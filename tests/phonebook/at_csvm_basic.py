# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0088300.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.security import lock_unlock_sim
from dstl.phonebook import phonebook_handle
from dstl.phonebook import developed_storage
from dstl.configuration import functionality_modes


class Test(BaseTest):
	"""
	TC0088300.001 - TpAtCsvmBasic
	"""

	def setup(test):
		test.log.info("This TC does not check the functionality itself, only the remote control for the ATC is checked.")
		test.dut.dstl_detect()
		test.log.info("********** Check if SIM card support VM storage. **********")
		test.expect(test.dut.dstl_enter_pin())
		test.wait_for_pb_ready()
		test.dut.at1.send_and_verify("AT+CPBS=?")
		if "VM" not in test.dut.at1.last_response:
			raise Exception("Current SIM card does not support VM, skip tests.")

		test.log.info("********** Lock SIM with pin **********")
		test.expect(test.dut.dstl_lock_sim())
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

	def run(test):
		test.log.step("1. Check commands without PIN input")
		# test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
		test.expect(test.dut.at1.send_and_verify_retry("AT+CPIN?", expect="\+CPIN: SIM PIN.*OK", retry=5, timeout=5,
													   retry_expect="SIM not inserted", wait_after_send=2))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=?", "\+CME ERROR: SIM PIN required"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CME ERROR: SIM PIN required"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=5", "\+CME ERROR: SIM PIN required"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM", "\+CME ERROR: \w+"))
		
		test.log.step("2. Check commands with PIN ready")
		test.expect(test.dut.dstl_enter_pin())
		test.wait_for_pb_ready()
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=?", "\+CSVM: \(0-1\),\(128-255\)"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 0,\"\",128"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM", "\+CME ERROR: \w+"))

		test.log.step("3. Check invalid commands with PIN ready")

		test.log.info("******* 3.1. Check invalid commands - parameter 1 *******")
		invalid_params = ['2', '11', '""', '"0"', '', '-0', '-1', '-2']
		for param in invalid_params:
			test.expect(test.dut.at1.send_and_verify(f"AT+CSVM={param}", "\+CME ERROR: invalid index"))
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=000", "OK"))

		test.log.info("******* 3.2. Check invalid commands - parameter 2 *******")
		num_20_digits = test.generate_number(20)
		num_40_digits = test.generate_number(40)
		num_41_digits = test.generate_number(41)
		num_45_digits = test.generate_number(45)
		num_80_digits = test.generate_number(80)
		num_81_digits = test.generate_number(81)
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,\"\"", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,\"\",145", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,\"99az\"", "\+CME ERROR: unknown"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,1234", "\+CME ERROR: unknown"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,\"1234\"", "\+CME ERROR: unknown"))
		test.log.info("******* Try number with 20 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_20_digits}\"", "OK"))
		test.log.info("******* Try number with 40 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_40_digits}\"", "OK"))
		test.log.info("******* Try number with 41 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_41_digits}\"", "\+CME ERROR: dial string too long"))
		test.log.info("******* Try number with 45 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_45_digits}\"", "\+CME ERROR: dial string too long"))
		test.log.info("******* Try number with 80 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_80_digits}\"", "\+CME ERROR: dial string too long"))
		test.log.info("******* Try number with 81 chars: OK *******")
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{num_81_digits}\"", "\+CME ERROR: dial string too long"))
		test.log.info("******* 3.3. Check invalid commands - parameter 3 *******")
		invalid_types = ['127', '1', '130', '256']
		for t in invalid_types:
			test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=0,\"1234\",{t}", "\+CME ERROR: \w+"))

		test.log.step("4. Do normal settings")
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",128", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"1234\",128"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",129", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"1234\",129"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",145", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"\+1234\",145"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"+\",145", "\+CME ERROR: \w+"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"\+1234\",145"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"++\",145", "\+CME ERROR: \w+"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"\+1234\",145\s+OK"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"+441522400032*#49#\",145", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"\+441522400032\*#49#\",145\s+OK"))

		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0,\"+\",145", "\+CME ERROR: \w+"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"\+441522400032\*#49#\",145"))
		
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",161"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 1,\"1234\",161.*OK.*"))
		
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"+2345\",128"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 1,\"\+2345\",145.*OK.*"))
		
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",255"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 1,\"1234\",255.*OK.*"))

		test.dut.at1.send_and_verify('at^cicret=swn')
		res = test.dut.at1.last_response
		if '100_' in res:
			test.log.info('For Viper, "IPIS100328760 Type 209 is not supported by CSVM command" is not to fix')
		else:
			test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"1234\",209"))
			test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 1,\"1234\",209.*OK.*"))

		test.log.step("5. Do conflict cases")
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"2345\",161;+csvm=0"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 0,\"\",128.*OK.*"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=1,\"2345\",161;+csvm=1,\"1234\",129"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"1234\",129.*OK.*"))

		test.log.step("6. Check ATC within airplane mode - should work")
		test.expect(test.dut.dstl_set_airplane_mode())
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", "\+CSVM: 1,\"1234\",129.*OK.*"))
		test.expect(test.dut.at1.send_and_verify(f"AT+CSVM=1,\"{test.r1.sim.int_voice_nr}\""))
		r1_number_in_resp = test.r1.sim.int_voice_nr.replace('+', '\+')
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", f"\+CSVM: 1,\"{r1_number_in_resp}\",145\s+OK"))
		test.expect(test.dut.dstl_set_full_functionality_mode())
		test.wait_for_pb_ready()
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", f"\+CSVM: 1,\"{r1_number_in_resp}\",145\s+OK"))

		test.log.step("7. Check influence of AT&F - should not")
		test.expect(test.dut.at1.send_and_verify("AT&F"))
		test.expect(test.dut.at1.send_and_verify("ATZ"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", f"\+CSVM: 1,\"{r1_number_in_resp}\",145\s+OK"))

		test.log.step("8. Check settings after restart")
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.dstl_enter_pin())
		test.wait_for_pb_ready()
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", f"\+CSVM: 1,\"{r1_number_in_resp}\",145\s+OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0"))
		test.expect(test.dut.at1.send_and_verify("AT+CSVM?", ".*\+CSVM: 0,\"\",128.*OK.*"))

	def cleanup(test):
		test.dut.at1.send_and_verify("AT+CFUN=1")
		test.sleep(3)
		test.expect(test.dut.at1.send_and_verify("AT+CSVM=0"))
	
	def generate_number(test, length):
		number = ""
		for i in range(length):
			number += str(i)[-1]
		return number
	
	def wait_for_pb_ready(test):
		test.log.info("******* Run AT+CPBS multiple times until OK is returned. ********")
		test.attempt(test.dut.at1.send_and_verify, "AT+CPBS?", "OK", retry=5, sleep=5)


if __name__ == "__main__":
	unicorn.main()
