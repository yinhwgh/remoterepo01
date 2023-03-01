# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0092519.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call.setup_voice_call import dstl_is_data_call_supported,dstl_release_call


class Test(BaseTest):
    '''
    TC0092519.001 - Ats0forVoiceAndDataCall
    Intention: 	Test command: ATS0 for Data Call and Voice Call.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.sleep(3)
        test.dut.dstl_register_to_network()
        test.r1.dstl_register_to_network()

    def run(test):

        test.log.info('***Test Start***')
        test.log.info('1. Check default values: ATS0? ')
        test.expect(test.dut.at1.send_and_verify('AT&f', 'OK'))
        test.expect(test.dut.at1.send_and_verify('ATS0?', '000'))

        test.log.info('2. Check all correct values ')
        test.step2()

        test.log.info('3. Function test n=1,2,5 ')
        test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", "OK"))
        test.step3(1)
        test.step3(2)
        test.step3(5)

        test.log.info('4. Test wrong parameters')
        test.expect(test.dut.at1.send_and_verify('ATS0=', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATS0=?', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATS0=-1', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('ATS0=256', 'ERROR'))


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('ATS0=0', 'OK'))

    def step2(test):
        test.log.info('Set and Read n from 001 to 255')
        for i in range(1,256):
            test.expect(test.dut.at1.send_and_verify(f'ATS0={i}','OK'))
            if len(str(i))<3:
                read_value = '0'*(3-len(str(i)))+str(i)
            else:
                read_value = str(i)
            test.expect(test.dut.at1.send_and_verify('ATS0?', read_value))



    def step3(test,value):
        if test.dut.dstl_is_data_call_supported():
            test.log.info('Not implemented for current product not support.')

        test.log.info(f'Test voice call with parameter ATS0={value}')
        dut_phone_num = test.dut.sim.nat_voice_nr
        test.expect(test.dut.at1.send_and_verify(f'ATS0={value}'))
        test.r1.at1.send_and_verify(f"ATD{dut_phone_num};")
        test.expect(test.dut.at1.wait_for("(RING\s+){%d}.*SLCC: 1,1,0,0,0.*"%value, timeout=60))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,1,0,0,0.*"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "\+CLCC: 1,0,0,0,0.*"))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())



if "__main__" == __name__:
    unicorn.main()
