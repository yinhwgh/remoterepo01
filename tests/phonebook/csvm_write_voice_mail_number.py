#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0092323.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module

class Test(BaseTest):
    """
    TC0092323.001 - CsvmWriteVoiceMailNumber
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='.*OK.*'))

    def run(test):
        test.expect(test.dut.at1.send_and_verify('AT+CPIN?', expect='\s+\+CPIN: READY\s+OK.*'))
        test.log.info("Waiting for SIM storage ready.")
        test.sleep(30)
        test.expect(test.dut.at1.send_and_verify('AT+CPBS=?', 'VM'))
        if 'VM' not in test.dut.at1.last_response:
            test.log.error("Module dose not support VM storage, cannot test AT+CSVM.")
        else:
            test.log.step("1. Check list of supported modes and types with use AT+CSVM=?")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM=?', expect='\s+\+CSVM: \(0-1\),\(128-255\)\s+OK.*'))
            test.log.step("2. Check current set mode, number and type with use AT+CSVM?")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CSVM: .*OK'))
            types = ['128', '129', '145', '161', '209', '255']
            for num_type in types:
                number = "123456" if num_type != '145' else '+123456'
                res_number = number.replace('+', '\+')
                test.log.step(f"Loop for type {num_type}, 3. Try to write Voice Mail Number with use CSVM write command eg. AT+CSVM=1,\"number\",129")
                test.expect(test.dut.at1.send_and_verify(f'AT+CSVM=1,"{number}",{num_type}', expect='.*OK.*'))
                test.log.step(f"Loop for type {num_type}, 4. Check if this number is written by use read command AT+CSVM?")
                test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect=f'\s+\+CSVM: 1,\"{res_number}\",{num_type}\s+OK.*'))
                if num_type == '209':
                    test.log.info('For Viper 2 failures may be caused by not fix issue "IPIS100328760 Type 209 is not supported by CSVM command."')
                test.log.step(f"Loop for type {num_type}, 5. Try to delete written number with use AT+CSVM=0")
                test.expect(test.dut.at1.send_and_verify('AT+CSVM=0', expect='.*OK.*'))
                test.log.step(f"Loop for type {num_type}, 6. Check if this number is delete with read command AT+CSVM?")
                test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CSVM: 0,\"\",128\s+OK.*'))
            test.log.step("7. Ommit type value, default is 129.")
            test.expect(test.dut.at1.send_and_verify('AT+CSVM=1,"123456"', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CSVM: 1,\"123456\",129\s+OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CSVM=0', expect='.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT+CSVM?', expect='\s+\+CSVM: 0,\"\",128\s+OK.*'))

    def cleanup(test):
        pass


if '__main__' == __name__:
    unicorn.main()
