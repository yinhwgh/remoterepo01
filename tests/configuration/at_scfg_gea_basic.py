#responsible: ding.ling@thalesgroup.com
#location: Dalian
#TC0104058.002

import unicorn
from core.basetest import BaseTest

import re
from dstl.auxiliary import restart_module
from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network

class ScfgSecurityGeaBasic(BaseTest):
	"""
		   TC0104058.002 - TpScfgGeaBasic
		   This case is mainly designed for Viper
		   Basic check not function check for AT^SCFG="Security/GEA".

		   Test need one dut, need one sim
	"""
	def setup(test):
		test.log.info("init the test ")
		test.dut.dstl_detect()
		test.expect(test.dut.dstl_lock_sim())
		test.dut.dstl_restart()

	def run(test):
		test.log.info("*****************1.check this should be an internal command******************")
		test.expect(test.dut.at1.send_and_verify("at^scfg=?", "[^Security/GEA]"))
		test.expect(test.dut.at1.send_and_verify("at^scfg?", "[^Security/GEA]"))
		test.log.info("*****************2.check default value, should be 6******************")
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*6.*"))
		test.log.info("*****************3.without pin******************")
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",2", "OK"))
		test.log.info("*****************4.with pin******************")
		test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
		test.expect(test.dut.dstl_enter_pin())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*2.*"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",4", "OK"))
		test.log.info("*****************5.in airplane mode******************")
		test.expect(test.dut.at1.send_and_verify("AT+CFUN=4", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",1", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT+CFUN=1", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*1.*"))
		test.log.info("*****************6.setting all valid parameters******************")
		test.log.info("-------------------------------6.1 after set a new value, check value---")
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",0", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*0.*"))
		test.log.info("-------------------------------6.2 after at&F, check value---")
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*0.*"))
		test.log.info("-------------------------------6.3 After restart module and check value---")
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*0.*"))
		test.log.info("-------------------------------6.4 repeat step6.1 to step6.3--")
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",1", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*1.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*1.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*1.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",2", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*2.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*2.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*2.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",4", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*4.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*4.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*4.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",3", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*3.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*3.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*3.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",5", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*5.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*5.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*5.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",6", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*6.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*6.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*6.*"))

		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",7", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*7.*"))
		test.expect(test.dut.at1.send_and_verify("at&f", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*7.*"))
		test.expect(test.dut.dstl_restart())
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\"", ".*7.*"))
		test.log.info("*****************6.setting invalid parameters******************")
		test.expect(test.dut.at1.send_and_verify("at+cmee=2", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",8", "ERROR: invalid index"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",-1", "ERROR: invalid index"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",A", "ERROR: invalid index"))
		test.expect(test.dut.at1.send_and_verify("at+cmee=1", "OK"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",8", "ERROR: 21"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",-1", "ERROR: 21"))
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",A", "ERROR: 21"))
	def cleanup(test):
		test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Security/GEA\",6", "OK"))

if (__name__ == "__main__"):
	unicorn.main()
