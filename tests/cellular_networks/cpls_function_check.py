#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0087882.001


import unicorn

from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network

class cpls_function_check(BaseTest):
    def setup(test):
        test.dut.dstl_detect()


    def run(test):
        test.log.info("1. test: check test and exec command without PIN")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=?', '.*\\+CME ERROR: SIM PIN required.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPLS?', '.*\\+CME ERROR: SIM PIN required.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=0', '.*\\+CME ERROR: SIM PIN required.*'))

        test.log.info("2. test: check test and exec command with PIN authentication")
        test.expect(test.dut.at1.send_and_verify('AT+CMEE=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', '.*OK.*'))
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(15)
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', '.*\\+CREG: 2,1,.*,.*,[079].*'))
        test.log.info("AT+CPLS=? - <Test command> requests the list of supported plmn-sector(s) "
                      "Response: list with number of supported plmn-sector(s)")
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=?', '.*\\+CPLS: [\\(0,1,2\\)]|[\\(0\\-2\\)].*OK.*'))
        test.log.info("AT+CPLS=<index> - <Write command> requests the entry of <index>-position from the preferred operator list "
                      "Response: ok")
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=0', '.*OK.*'))
        test.log.info("AT+CPOL? - (list of supported <index>s), (list of supported <format>s) "
                      "Response: ok")
        test.expect(test.dut.at1.send_and_verify('AT+CPOL?', '.*OK.*'))
        test.log.info("AT+CPLS=<index> - <Write command> requests the entry of <index>-position from the preferred operator list "
                      "Response: ok" )
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=1', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPOL?', '.*OK.*'))
        test.log.info("AT+CPLS=<index> - <Write command> requests the entry of <index>-position from the preferred operator list "
                      "Response: ok" )
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPOL?', '.*OK.*'))

        test.log.info("3. test: check AT+CPLS command with invalid parameters ")
        test.expect(test.dut.at1.send_and_verify('AT+CPLS=99999', '.*\\+CME ERROR: invalid index.*'))

        test.expect(test.dut.at1.send_and_verify('AT&F', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', '.*OK.*'))


    def cleanup(test):
        pass

if(__name__ == "__main__"):
    unicorn.main()
