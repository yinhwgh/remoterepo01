#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0095491.001
#

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.sms.sms_functions import dstl_send_sms_message
from dstl.call.setup_voice_call import dstl_is_voice_call_supported

class Test(BaseTest):
    '''
    TC0095491.001 - SmokeAT4Automation
    Intention :Simple check of the ATc which are needed for automation (describe in RQ1001340.001) are available.
     No check,if the function works fine
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()

    def run(test):
        test.expect(test.dut.at1.send_and_verify('ATE0','OK'))
        test.expect(test.dut.at1.send_and_verify('at^siekret=0','OK|ERROR'))
        test.expect(test.dut.at1.send_and_verify('ati','OK'))
        test.expect(test.dut.at1.send_and_verify('ATE1','OK'))
        test.expect(test.dut.at1.send_and_verify('at^sos=ver','OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmee=2','OK'))
        test.expect(test.dut.at1.send_and_verify('at+cfun=0', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
        test.sleep(10)
        test.dut.dstl_register_to_network()
        test.expect(test.dut.at1.send_and_verify('at+cpin?','READY'))
        test.expect(test.dut.at1.send_and_verify('at^spic','OK'))
        test.expect(test.dut.at1.send_and_verify('at^sset=1','OK'))
        test.expect(test.dut.at1.send_and_verify('at+creg=0','OK'))
        test.expect(test.dut.at1.send_and_verify('at+creg?','CREG: 0,1.*OK'))
        test.expect(test.dut.at1.send_and_verify('at+cops?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cops=3,2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cops=3,0','OK'))
        test.expect(test.dut.at1.send_and_verify('at+cimi', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^smoni', '\^SMONI: .*OK'))
        test.expect(test.dut.at1.send_and_verify('at+cclk?', 'CCLK: .*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=242', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgsn', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cgact?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ctzu=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sind?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('AT+CEMODE?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cscs?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ceer', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpol?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at^sind?', 'OK'))

        if(test.dut.dstl_is_voice_call_supported()):
            test.expect(test.dut.at1.send_and_verify('at+cpbs=?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpbr=?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cpbw=?', 'OK'))

        test.expect(test.dut.at1.send_and_verify('at+cpms?', 'OK'))

        # Serval03+04 do not support +CGQ.. cmds
        if test.dut.project == 'SERVAL':
            test.expect(test.dut.at1.send_and_verify('at+cgqreq?', '+CME ERROR: unknown'))
            test.expect(test.dut.at1.send_and_verify('at+cgqmin?', '+CME ERROR: unknown'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', '+CME ERROR: unknown'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqmin?', '+CME ERROR: unknown'))
        else:
            test.expect(test.dut.at1.send_and_verify('at+cgqreq?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgqmin?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqreq?', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at+cgeqmin?', 'OK'))

        test.expect(test.dut.at1.send_and_verify('at+cnmi=2,1', 'OK'))
        test.log.info('Send sms to itself.')
        test.dut.at1.send_and_verify('AT+CSMP=17,167,0,0', '.*OK.*', timeout=10)
        sms_message = 'Test SMS SMS SMS.'
        dstl_send_sms_message(test.dut, test.dut.sim.int_voice_nr, sms_message, 'Text')
        test.expect(test.dut.at1.wait_for('.*CMTI:.*', timeout=360))
        test.expect(test.dut.at1.send_and_verify('at+cmgl="STO SENT"', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmgr=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cmgd=1', 'OK'))



    def cleanup(test):
       pass



if "__main__" == __name__:
    unicorn.main()

