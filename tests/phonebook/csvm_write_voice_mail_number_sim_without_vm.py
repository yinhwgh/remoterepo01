#author: cong.hu@thalesgroup.com
#location: Dalian
#TC0092327.001, TC0092327.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step('1.Restart the module.')
        # test.expect(test.dut.dstl_restart())
        test.log.info("Skip restart module since it is not necessary.")

        test.log.step('2.Insert SIM card and enter SIM PIN.')
        test.expect(test.dut.dstl_enter_pin())

        test.log.step('3.Wait for the SIM init.')
        test.sleep(30)
        test.log.info("Checking if SIM matches the requirement: without VM storage.")
        test.attempt(test.dut.at1.send_and_verify,'AT+CPBS=?', 'OK', retry=3, sleep=3)
        test.expect('VM' not in test.dut.at1.last_response, critical=True,
                    msg="SIM card has VM storage.")

        test.log.step('4.Check PIN1 status.')
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: READY\s+OK.*'))

        test.log.step('5.Read EF-MBDN on the SIM card.')
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28615,1,4,38', expect='\s+\+CRSM: 106,130.*'))

        test.log.step('6.Check list of supported modes and types with AT+CSVM=?.')
        test.expect(test.dut.at1.send_and_verify('AT+CSVM=?', expect='\s+\+CSVM: \(0-1\),\(128-255\)\s+OK.*'))

        test.log.step('7.Check current set mode, number and type with use AT+CSVM?.')
        test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))

        types = ['128', '129', '145', '161', '255','209']
        for num_type in types:
            number = "12345678" if num_type != '145' else '+12345678'
            res_number = number.replace('+', '\+')
            test.log.step(
                f"Loop for type {num_type}, 8. Try to write Voice Mail Number with use CSVM write command eg. AT+CSVM=1,\"number\",129")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))

            test.log.step(f"Loop for type {num_type}, 9. Check if this number is written by use read command AT+CSVM?")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))

            test.log.step(f"Loop for type {num_type}, 10. Try to delete written number with use AT+CSVM=0")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM=0', expect='\s+\+CME ERROR: unknown.*'))

            test.log.step(f"Loop for type {num_type}, 11. Check if this number is delete with read command AT+CSVM?")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))

        test.log.step("12. Ommit type value, default is 129.")
        test.expect(test.dut.at1.send_and_verify('AT+CSVM=1,"12345678"', expect='\s+\+CME ERROR: unknown.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSVM=0', expect='\s+\+CME ERROR: unknown.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CME ERROR: unknown.*'))


    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
