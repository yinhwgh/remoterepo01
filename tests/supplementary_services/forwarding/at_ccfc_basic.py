# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091799.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call


class Test(BaseTest):
    """
    TC0091799.001 - TpAtCcfcBasic
    Intention: This procedure provides basic tests for the command at+ccfc.
    Subscriber: 2
    """

    exp_resp_clear_all_cf = "OK"

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.sleep(3)
        global exp_resp_clear_all_cf
        if test.dut.platform == 'XGOLD':
            exp_resp_clear_all_cf = '\+CME ERROR: service option not supported'
            # clearing is performed, but blocked for some classes which are not supported
        pass

    def run(test):
        nat_dut_phone_num = test.r1.sim.nat_voice_nr
        dut_phone_num_regexpr = nat_dut_phone_num
        if dut_phone_num_regexpr.startswith('0'):
            dut_phone_num_regexpr = '.*' + dut_phone_num_regexpr[1:]

        test.log.step('1. Check command without PIN.')
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+cpin?', 'SIM PIN'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=?', '\+CME ERROR: SIM PIN required'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', '\+CME ERROR: SIM PIN required'))

        test.log.step('2. Check command with PIN.')
        test.dut.dstl_enter_pin()
        test.sleep(5)
        global exp_resp_clear_all_cf
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', exp_resp_clear_all_cf))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=?', 'CCFC:(.*).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2',
                                                 '.*\+CCFC: 0,1.*OK.*|.*\+CCFC: 0,7.*OK.*|.*\+CCFC: 0,255.*OK.*'))

        test.log.step('3. Check all parameters and also with invalid values.')
        test.expect(test.dut.at1.send_and_verify('at+ccfc=1,2',
                                                 '.*\+CCFC: 0,1.*OK.*|.*\+CCFC: 0,7.*OK.*|.*\+CCFC: 0,255.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=2,2',
                                                 '.*\+CCFC: 0,1.*OK.*|.*\+CCFC: 0,7.*OK.*|.*\+CCFC: 0,255.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=3,2',
                                                 '.*\+CCFC: 0,1.*OK.*|.*\+CCFC: 0,7.*OK.*|.*\+CCFC: 0,255.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=4,2','ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=5,2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=-1,2', 'ERROR'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,5', 'ERROR'))

        test.log.step('4. Check functionality by activating/registering different cases of CF, '
                      'deactivate and erase them again')
        test.expect(test.dut.at1.send_and_verify(f'at+ccfc=0,3,"{nat_dut_phone_num}",129,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2',
                                                 f'\+CCFC: 1,1,"{dut_phone_num_regexpr}",(129|145).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,0,,,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2',
                                                 f'\+CCFC: 0,1,"{dut_phone_num_regexpr}",(129|145).*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,4,,,1', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+ccfc=0,2', '.*CCFC: (0,1|0,255).*OK.*'))
        pass

    def cleanup(test):
        global exp_resp_clear_all_cf
        test.expect(test.dut.at1.send_and_verify('AT+CCFC=4,4', exp_resp_clear_all_cf))
        pass


if "__main__" == __name__:
    unicorn.main()
