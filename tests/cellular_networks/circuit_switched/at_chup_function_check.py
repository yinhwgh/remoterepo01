#responsible: xiaolin.liu@thalesgroup.com
#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0000125.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.phonebook import phonebook_handle
from dstl.call import setup_voice_call

class Test(BaseTest):
    '''
    TC0000125.002 - TpCChup
    Intention: This test is provided to test command: Hang Up Call AT+CHUP, which was designed to disconnect the remote user.
        '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SLCC=1', expect='OK'))

    def run(test):
        dut_phone_num = test.dut.sim.nat_voice_nr
        r1_num = test.r1.sim.nat_voice_nr
        test.log.step('1. Add the entry into phonebook')
        test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"SM\""), "OK")
        test.expect(test.dut.at1.send_and_verify("AT+CPBW=2,\"{}\",129,\"dut_2\"".format(r1_num)))
        test.expect(test.r1.at1.send_and_verify("AT+CPBS=\"SM\""), "OK")
        test.expect(test.r1.at1.send_and_verify("AT+CPBW=1,\"{}\",129,\"r1_1\"".format(dut_phone_num)))

        test.log.step('2. Defined the phone number with different type')
        simple_number = r1_num
        r1_int_num = test.r1.sim.int_voice_nr
        number_with_ignored_char =r1_num[0:3]+"@"+r1_num[3:6]+"@"+r1_num[6:9]+"W,"+r1_num[9:11]
        number_with_activated_CLIR = r1_num+"I"
        number_with_activated_CLIR_int = r1_int_num + "I"
        number_with_suppressed_CLIR = r1_num + "i"
        number_with_suppressed_CLIR_int = r1_int_num + "i"
        number_with_activated_CLIR_via_31 = "#31#"+r1_num
        number_with_activated_CLIR_via_31_int ="#31#"+r1_int_num
        number_with_suppressed_CLIR_via_31 ="*31#"+ r1_num
        number_with_suppressed_CLIR_via_31_int ="*31#"+ r1_int_num
        number_with_DTMF_sequence = r1_num + "p9##12345"
        pb_entry_mem_index=">SM2"
        pb_entry_index = ">2"
        pb_entry_str = ">dut_2"
        dialing_string=[simple_number,r1_int_num,number_with_ignored_char,
                        number_with_activated_CLIR,
                        number_with_activated_CLIR_int,
                        number_with_suppressed_CLIR,
                        number_with_suppressed_CLIR_int,
                        number_with_activated_CLIR_via_31,
                        number_with_activated_CLIR_via_31_int,
                        number_with_suppressed_CLIR_via_31,
                        number_with_suppressed_CLIR_via_31_int,
                        pb_entry_mem_index,pb_entry_index,pb_entry_str]

        test.log.step('3. Make voice call with different type for MOC')
        for i in range(len(dialing_string)):
            ring_num = dialing_string[i]
            test.log.step('3.'+str(i+1)+'.1 Dialing state of call')
            test.expect(test.dut.at1.send_and_verify(f"ATD{ring_num};", expect='.*OK.*',wait_for='SLCC: 1,0,2,0,0,0'))
            test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
            test.expect(test.r1.dstl_release_call())
            test.sleep(5)

            test.log.step('3.'+str(i+1)+'.2 Alerting state of call')
            test.expect(test.dut.at1.send_and_verify(f"ATD{ring_num};", expect='.*OK.*',wait_for='SLCC: 1,0,3,0,0,0'))
            test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
            test.expect(test.r1.dstl_release_call())
            test.sleep(5)

            test.log.step('3.'+str(i+1)+'.3 Active - MOC state of call')
            test.expect(test.dut.at1.send_and_verify(f"ATD{ring_num};"))
            test.expect(test.r1.at1.wait_for("RING"))
            test.expect(test.r1.at1.send_and_verify('ATA', expect='.*OK.*',wait_for='SLCC: 1,0,0,0,0,0'))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ',wait_for='SLCC: '))
            test.expect(test.r1.dstl_release_call())
            test.sleep(5)

            test.log.step('3.'+str(i+1)+'.4 Held - MOC state of call')
            test.expect(test.dut.at1.send_and_verify(f"ATD{ring_num};"))
            test.expect(test.r1.at1.wait_for("RING"))
            test.expect(test.r1.at1.send_and_verify('ATA', expect='.*OK.*'))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='.*OK.*',wait_for='SLCC: 1,0,1,0,0,0'))
            test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
            test.expect(test.r1.dstl_release_call())
            test.sleep(5)

        test.log.step('4. Make voice call with different type for MTC')
        test.log.step('4.1 Incoming state of call')
        test.expect(test.r1.at1.send_and_verify(f"ATD{dut_phone_num};"))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,1,4,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
        test.expect(test.r1.dstl_release_call())
        test.sleep(5)

        test.log.step('4.2 Active - MTC state of call')
        test.expect(test.r1.at1.send_and_verify(f"ATD{dut_phone_num};"))
        test.expect(test.dut.at1.wait_for("RING"))
        test.expect(test.dut.at1.send_and_verify('ATA', expect='.*OK.*',wait_for='SLCC: 1,1,0,0,0,0'))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
        test.expect(test.r1.dstl_release_call())
        test.sleep(5)

        test.log.step('4.3 Held - MTC state of call')
        test.expect(test.r1.at1.send_and_verify(f"ATD{dut_phone_num};"))
        test.expect(test.dut.at1.wait_for("RING"))
        test.expect(test.dut.at1.send_and_verify('ATA', expect='.*OK.*'))
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='.*OK.*',wait_for='SLCC: 1,1,1,0,0,0'))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
        test.expect(test.r1.dstl_release_call())
        test.sleep(5)

        test.log.step('5. Make voice call with different type for DTMF')
        test.log.step('5.1 Active - MOC state of DTMF call')
        test.expect(test.dut.at1.send_and_verify(f"ATD{number_with_DTMF_sequence};",expect='',wait_for=''))
        test.expect(test.r1.at1.wait_for("RING"))
        test.expect(test.r1.at1.send_and_verify('ATA', expect='.*OK.*'))
        test.expect(test.dut.at1.wait_for("\^SLCC: 1,0,0,0,0,0.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
        test.expect(test.r1.dstl_release_call())
        test.sleep(5)

        test.log.step('5.2 Held - MOC state of DTMF call')
        test.expect(test.dut.at1.send_and_verify(f"ATD{number_with_DTMF_sequence};",expect='',wait_for=''))
        test.expect(test.r1.at1.wait_for("RING"))
        test.expect(test.r1.at1.send_and_verify('ATA', expect='.*OK.*'))
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify('AT+CHLD=2', expect='.*OK.*',wait_for='SLCC: 1,0,1,0,0,0'))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='SLCC: ', wait_for='SLCC: '))
        test.expect(test.r1.dstl_release_call())
        test.sleep(5)
        # Data Call: Not implemented since Viper does not support.

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='.*OK.*'))


if '__main__' == __name__:
    unicorn.main()
