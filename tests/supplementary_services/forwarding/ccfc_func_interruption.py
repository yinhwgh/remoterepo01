#responsible: wen.liu@thalesgroup.com
#location: Dalian
#TC0095822.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call import setup_voice_call
from dstl.auxiliary import check_urc


class CcfcFuncInterruption(BaseTest):
    '''
    TC0095822.001 - CcfcFuncInterruption
    Intention: AT command cascade and SMS interruption for ccfc function
    Subscriber: 4
    '''


    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        test.r1.dstl_detect()
        test.r1.dstl_restart()
        test.sleep(3)
        test.r2.dstl_detect()
        test.r2.dstl_restart()
        test.sleep(3)
        test.r3.dstl_detect()
        test.r3.dstl_restart()
        test.sleep(3)
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r2.dstl_register_to_network())
        test.expect(test.r3.dstl_register_to_network())


    def run(test):
        int_dut_phone_num = test.dut.sim.int_voice_nr
        int_r1_phone_num = test.r1.sim.int_voice_nr
        int_r2_phone_num = test.r2.sim.int_voice_nr
        int_r3_phone_num = test.r3.sim.int_voice_nr
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', 'OK'))
        test.log.step('1. Set the at command covering ccfc, then check if every atc is set and works well')
        test.log.step('1.1. Start test unconditional call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=0,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect=f'\+CCFC: 0,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', expect='\+CCFC: 0,1\s+OK'))
        test.log.step('1.2. Start test busy call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=1,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2', expect=f'\+CCFC: 0,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2', expect='\+CCFC: 0,1\s+OK'))
        test.log.step('1.3. Start test no reply call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=2,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2', expect=f'\+CCFC: 0,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2', expect='\+CCFC: 0,1\s+OK'))
        test.log.step('1.4. Start test not reachable call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=3,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2', expect=f'\+CCFC: 0,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2', expect=f'\+CCFC: 1,1,"\\{int_r1_phone_num}".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,4', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2', expect='\+CCFC: 0,1\s+OK'))
        test.log.step('1.5. Start test all call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=4,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,2', expect='.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,4', expect='OK'))
        test.log.step('1.6. Start test all conditional call forwarding')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=5,3,{int_r1_phone_num},,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=5,2', expect='.*ERROR.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=5,0', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=5,1', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=5,4', expect='OK'))
        test.log.step('2. Remote2 receive SMS during call forwarding process')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=0,3,{int_r2_phone_num},,1', expect='OK'))
        test.expect(test.r1.at1.send_and_verify('at+cmgf=1', expect='OK'))
        test.expect(test.r2.at1.send_and_verify('at+cnmi=2,1', expect='OK'))
        test.expect(test.r1.at1.send_and_verify(f'ATD{int_dut_phone_num};',expect='OK'))
        test.expect(test.r2.at1.wait_for("RING"))
        test.expect(test.r1.at1.send_and_verify(f'at+cmgs={int_r2_phone_num};', expect=">"))
        test.expect(test.r1.at1.send_and_verify('test',end="\u001A", expect='OK'))
        test.expect(test.r2.at1.wait_for(".*CMTI.*"))
        test.expect(test.r2.at1.wait_for("RING"))
        test.expect(test.r2.at1.send_and_verify('ata', expect='OK'))
        test.sleep(3)
        test.expect(test.r2.at1.send_and_verify('at+clcc', expect='.*CLCC: 1,1,0,0,0,.*OK.*'))
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.log.step('3. Remote2 is in calling status during call forwarding process')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=0,3,{int_r2_phone_num},,1', expect='OK'))
        test.expect(test.r2.at1.send_and_verify(f'ATD{int_r3_phone_num};', expect='OK'))
        test.expect(test.r3.at1.wait_for("RING"))
        test.expect(test.r3.at1.send_and_verify('ata', expect='OK'))
        test.sleep(3)
        test.expect(test.r2.at1.send_and_verify('at+clcc', expect='.*CLCC: 1,0,0,0,0,.*OK.*'))
        test.expect(test.r1.at1.send_and_verify(f'ATD{int_dut_phone_num};', expect='OK'))
        test.expect(test.r2.at1.send_and_verify('at+ccwa?', expect='.*CCWA:.*OK.*'))
        res = test.r2.at1.last_response
        if "1" in res:
            test.expect(test.r2.at1.wait_for(".*?CCWA:.*?"))
        else:
            test.log.info('Remote r1 will hear the tone of busy.')
        test.sleep(5)
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())
        test.expect(test.r3.dstl_release_call())
        test.log.step('4. Remote2 is in power-off status during call forwarding process')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=0,3,{int_r2_phone_num},,1', expect='OK'))
        test.expect(test.r2.at1.send_and_verify('at^smso', expect='OK'))
        test.expect(test.r1.at1.send_and_verify(f'ATD{int_dut_phone_num};', expect='OK'))
        test.log.info('Remote r1 will hear the tone of shutdown.')
        test.expect(test.dut.dstl_release_call())
        test.expect(test.r1.dstl_release_call())
        test.expect(test.r2.dstl_release_call())


    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', 'OK'))


if '__main__' == __name__:
    unicorn.main()