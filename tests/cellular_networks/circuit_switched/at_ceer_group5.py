#author: haofeng.ding@thalesgroup.com
#location: Dalian
#TC0000188.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported

class Test(BaseTest):
    '''
        TC0000188.001 - IndCeerRelCauseGroup5
        Check presentation of  indicators "ceer" if parameter <CeerRelCauseGroup> is set to 5
        5 = CS network cause
        Extended Error Report indicator "ceer" delivers an extended error / release cause report as a single line containing the cause information given by the network in textual format.
        Subscriber: 2
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.dut.dstl_restart()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r1.dstl_register_to_network()
        test.dut.dstl_register_to_network()
        test.log.info('Enable error reporting')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))

    def run(test):
        r1_phone_num = test.r1.sim.int_voice_nr
        test.log.info('Check presentation of  indicators "ceer" if parameter <CeerRelCauseGroup> is set to 3 via ^SIND command for different scenarios')
        test.expect(test.dut.at1.send_and_verify('AT^SIND="ceer",1,5', expect='.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SIND="ceer",2', expect='.*5*'))
        test.log.info('Test 1: Subscriber1 tries to make a voice call with a not existing number')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('ATD931234567890;', expect='.*\+CIEV: ceer,2,"Unassigned/unallocated number".*||.*\+CIEV: ceer,2,"Normal call clearing".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Unassigned/unallocated number.*||.*\+CEER: Normal call clearing.*'))
        test.log.info('Test 2: Subscriber1 makes a voice call to Subscriber2. Subscriber2 is ringing. Subscriber1 goes on hook.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*\+CIEV: ceer,1,"Client ended call"*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Client ended call*'))
        test.log.info('Test 3: Subscriber1 tries to make a voice call to his own number')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(test.dut.sim.int_voice_nr), expect='.*\+CIEV: ceer,2,"User busy".*||.*\+CIEV: ceer,2,"Call rejected".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: User busy.*||.*\+CEER: Call rejected.*'))
        test.log.info('Test 4 Subscriber2 is not registered to the network. Subscriber1 tries to make a voice call to Subscriber2')
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', expect='(?s)AT\+CREG=2.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', expect='.*\+CREG: 0.*'))
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), expect='.*\+CIEV: ceer,2,"No user responding".*||.*\+CIEV: ceer,2,"Normal, unspecified".*||.*\+CIEV: ceer,2,"Normal call clearing".*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='(?s)AT\+COPS=0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CREG: 1,".*",".*".*'))
        test.log.info('Test 7: Subscriber1 tries to make a call with an incomplete number')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('ATD01632584;', expect='.*\+CIEV: ceer,2,"Invalid/incomplete number"'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Invalid/incomplete number.*||.*\+CEER: Normal call clearing.*||.*\+CEER: Normal, unspecified.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*||.*NO CARRIER.*', wait_for='.*OK.*||.*NO CARRIER.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*OK.*||.*NO CARRIER.*', wait_for='.*OK.*||.*NO CARRIER.*'))
        test.log.info('Test 6: Subscriber2 makes a voice call to Subscriber1. Subscriber1 is ringing. Subscriber2 goes on hook.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.r1.at1.send_and_verify(f"ATD{test.dut.sim.int_voice_nr};"))
        test.dut.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*\+CIEV: ceer,2,"Normal call clearing".*||.*\+CIEV: ceer,2,"Invalid/incomplete number".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Normal call clearing.*'))
        test.log.info('Test 9: Subscriber2 makes a voice call to Subscriber1. Subscriber1 is ringing. Subscribe1 not answered the call. Wait time exceeded from the network.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.r1.at1.send_and_verify(f"ATD{test.dut.sim.int_voice_nr};"))
        test.expect(test.dut.at1.wait_for('.*\+CIEV: ceer,2,"Normal, unspecified"'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Normal, unspecified.*'))
        test.log.info('Test 10: Subscriber1 makes a voice call to Subscriber2 and goes on hook.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), '', wait_for=''))
        test.r1.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*\+CIEV: ceer,1,"Client ended call"'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Client ended call.*'))
        test.log.info('Test 11: Subscriber1 selects FD (fixed dialing) phonebook. Subscribe2 phone number do not added to "FD" phone book. Subscriber1 makes a voice call to Subscriber2.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCK="FD",1,"0000"', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+CPBS="FD"', expect='(?s)AT\+CPBS="FD".*OK.*'))
        test.expect(test.dut.at1.send_and_verify('atd{};'.format(r1_phone_num), expect='.*\+CIEV: ceer,6,"Call barred".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Call barred.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CLCK="FD",0,"0000"', expect='.*OK*'))
        test.log.info('Test 12: Subscriber2 makes a voice call to Subscriber1. Subscriber1 is ringing. Subscriber1 goes on hook.')
        test.expect(test.dut.at1.send_and_verify('AT^SBLK', expect='.*OK*'))
        test.expect(test.r1.at1.send_and_verify(f"ATD{test.dut.sim.int_voice_nr};"))
        test.dut.at1.wait_for('RING')
        test.expect(test.dut.at1.send_and_verify('AT+CHUP', expect='.*NO CARRIER', wait_for='.*NO CARRIER'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: Client rejected incoming call.*'))
        test.log.info('Test 13: Subscriber1 tries to change network to not allowed PLMN via COPS command')
        test.expect(test.dut.at1.send_and_verify('AT+CREG=2', expect='(?s)AT\+CREG=2.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='(?s)AT\+COPS\?.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^scfg?', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=1,2,26201', expect='.*\+CIEV: ceer,3,"PLMN not allowed".*'))
        test.expect(test.dut.at1.send_and_verify('AT+CEER', expect='.*\+CEER: PLMN not allowed.*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', expect='(?s)AT\+COPS=0.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT+CREG=0', expect='.*OK*'))
        test.expect(test.dut.at1.send_and_verify('AT+COPS?', expect='(?s)AT\+COPS\?.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('AT^SIND="ceer",0', expect='(?s)AT\^SIND="ceer",0.*OK.*'))

    def cleanup(test):
        test.log.info('***Test End***')


if '__main__' == __name__:
    unicorn.main()
