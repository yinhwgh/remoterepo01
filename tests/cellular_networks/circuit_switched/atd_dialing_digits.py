#Responsible: xiaolin.liu@thalesgroup.com
#Location: Dalian
#TC0000087.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.call import setup_voice_call
from dstl.phonebook import phonebook_handle

class Test(BaseTest):
    '''
    TC0000087.001 - TpCAtd
    Intention: This test is provided to test command: Dial Command ATD.
    The V.24ter dial command D lists characters that may be used in a dialing string for making a
    call or controlling supplementary services in accordance with GSM02.30 and initiates the indicated kind of call.
    No further commands may follow in the command line.
    Subscriber: 2, dut and remote module
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', expect='OK'))

    def run(test):
        test.log.step('1. Define the mod_ifier_character with different type')
        memory_list = test.r1.dstl_get_supported_pb_memory_list()
        if "RC" in memory_list:
            test.rc_mem = True
        else:
            test.rc_mem = False
        r1_phone_num = test.r1.sim.nat_voice_nr
        r1_phone_num_with_international_access_code=test.r1.sim.int_voice_nr
        mod_ifier_character_begin=",T!W@"+r1_phone_num
        mod_ifier_character_end = r1_phone_num+",T!W@"
        mod_ifier_character_4random =r1_phone_num[0:3]+"@"+r1_phone_num[3:6]+"@"+r1_phone_num[6:9]+\
                                     "W,"+r1_phone_num[9:11]
        mod_ifier_character_withoutplus = r1_phone_num
        mod_ifier_character_withplus = r1_phone_num_with_international_access_code
        mod_ifier_character_withplus_andrandom = r1_phone_num_with_international_access_code[0:8]+ \
                                                 "@T"+"!"+r1_phone_num_with_international_access_code[8:14]
        dialing_string = [mod_ifier_character_begin,
                          mod_ifier_character_end,
                          mod_ifier_character_4random,
                          mod_ifier_character_withoutplus,
                          mod_ifier_character_withplus,
                          mod_ifier_character_withplus_andrandom]

        test.log.step('2. Make a call by using the ring number with different character.')
        for i in range(len(dialing_string)):
            ring_num = dialing_string[i]
            test.log.step('2.'+ str(i + 1)+' Using the ring number: "'+ring_num+'"')
            test.expect(test.dut.dstl_voice_call_by_number(test.r1, ring_num, "OK"))
            test.sleep(3)
            test.check_status_and_num(ring_num)
            test.expect(test.dut.dstl_voice_call_by_number(test.r1, 'L', "OK"))
            test.sleep(3)
            test.check_status_and_num(ring_num)

            # Data Call: Not implemented since Viper does not support.
            if test.dut.dstl_is_data_call_supported():
                test.expect(False, msg="Data call is not implemented.")

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))

    def check_status_and_num(test, num):
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(True, 0))
        test.expect(test.r1.dstl_check_voice_call_status_by_clcc(False, 0))
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=LD", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPBR=1", f'\+CPBR: 1,.*{test.r1.sim.nat_voice_nr}.*'))
        if test.rc_mem:
            test.expect(test.r1.at1.send_and_verify("AT+CPBS=RC", ".*OK.*"))
            test.expect(test.r1.at1.send_and_verify("AT+CPBR=1", f'\+CPBR: 1,.*{test.dut.sim.nat_voice_nr}.*'))
        else:
            test.log.info("Remote module or SIM does not support RC memory, skip checking RC phonebook.")
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.sleep(3)




if '__main__' == __name__:
    unicorn.main()
