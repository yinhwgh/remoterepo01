#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class generate_ps_data_for_gprs_by_atstest(BaseTest):
    def setup(test):
      pass


    def run(test):
        test.log.info("1. test: Enter PIN code")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(test.dut.dstl_enter_pin())

        test.log.info("2. test: Define two PDP contexts")
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"ip","internet"', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgdcont=2,"ip","internet3"', '.*OK.*'))

        test.log.info("3. test: Register to GSM network")
        test.expect(test.dut.at1.send_and_verify('AT+COPS=1,2,"45406",0', wait_for='.*OK.*', timeout='60'))

        test.log.info("4. test: Activate two PDP contexts")
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,1', wait_for='.*OK.*', timeout='60'))
        test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,2', wait_for='.*OK.*', timeout='60'))

        test.log.info("5. test: Use AT^STEST to generate and send ps data over + CGACT activated PDP context")
        test.expect(test.dut.at1.send_and_verify('AT^STEST="GPRS/IpGen","2","23"', '.*OK.*'))

        test.log.info("6. test: Try to set a  value which is not defined before.")
        test.expect(test.dut.at1.send_and_verify('AT^STEST="GPRS/IpGen","3","23"', '.*NO CARRIER.*'))

        test.log.info("7. test:.Try to set a  value that less than 21")
        test.expect(test.dut.at1.send_and_verify('AT^STEST="GPRS/IpGen","2","20"', '.*CME ERROR: parameters error.*'))


    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
