# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0095868.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.supplementary_services import ccfc_set_by_starhash


class Test(BaseTest):
    '''
    TC0095868.001 - StarHash_feat
    Intention: Check if Star Hash Codes are supported - both network services
     and internal commands like IMEI querying.
    Subscriber: 2
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_register_to_network()
        test.sleep(3)
        test.r1.dstl_detect()
        test.r1.dstl_register_to_network()
        test.sleep(3)

    def run(test):
        nat_dut_phone_num = test.dut.sim.nat_voice_nr
        nat_r1_phone_num = test.r1.sim.nat_voice_nr
        net_pin = test.dut.sim.pin1
        semicolon = test.dut.dstl_get_starhash_semicolon()
        test.dut.at1.send_and_verify('at+cmee=2', 'OK')
        test.log.step('1. Query IMEI.')
        test.dut.at1.send_and_verify(f'ATD*#06#{semicolon}', '\d{15}.*OK')
        test.log.step('2. Check status of CLIP.')
        test.dut.at1.send_and_verify(f'ATD*#30#{semicolon}', 'CLIP')
        test.log.step('3. check status of CLIR.')
        test.r1.at1.send_and_verify('at+clip=1', 'OK')
        test.dut.at1.send_and_verify(f'ATD*#31#{semicolon}', 'OK')
        test.log.step('4. suppress CLIR.')
        test.dut.at1.send_and_verify(f'ATD*31#{nat_r1_phone_num}{semicolon}', 'OK')
        test.expect(test.r1.at1.wait_for('RING'))
        test.expect(test.r1.at1.wait_for('CLIP: ".*",.*'))
        test.sleep(4)
        test.dut.dstl_release_call()

        test.log.step('5. activate CLIR.')
        test.expect(test.dut.at1.send_and_verify(f'ATD#31#{nat_r1_phone_num}{semicolon}', 'OK'))
        res = test.r1.at1.wait_for('RING')
        if res:
            test.log.error('Network may not support CLIR')
        test.dut.at1.send_and_verify('at+ceer', 'OK')
        test.dut.dstl_release_call()
        test.sleep(3)

        test.log.step('6. check status of COLP.')
        test.r1.at1.send_and_verify('at+clip=0', 'OK')
        test.expect(test.dut.at1.send_and_verify(f'ATD*#76#{semicolon}', 'OK'))

        test.log.step('7. check status of COLR.')
        test.expect(test.dut.at1.send_and_verify(f'ATD*#77#{semicolon}', 'OK'))

        test.log.step('8. reg/act/deact/int/eras Call Forwading - unconditional (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD**21*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*21*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#21*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#21*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##21*{nat_r1_phone_num}*11#{semicolon}', 'OK'))

        test.log.step('9. reg/act/deact/int/eras CF - busy (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD**67*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*67*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#67*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#67*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##67*{nat_r1_phone_num}*11#{semicolon}', 'OK'))

        test.log.step('10. reg/act/deact/int/eras CF - no reply (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD**61*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*61*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#61*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#61*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##61*{nat_r1_phone_num}*11#{semicolon}', 'OK'))

        test.log.step('11. reg/act/deact/int/eras CF - no reach (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD**62*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*62*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#62*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#62*{nat_r1_phone_num}*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##62*{nat_r1_phone_num}*11#{semicolon}', 'OK'))

        test.log.step('12. reg/act/deact/int/eras CF - all (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD**002*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*002*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#002*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#002*{nat_r1_phone_num}*11*10#{semicolon}', 'OK|ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##002*{nat_r1_phone_num}*11*10#{semicolon}', 'OK|ERROR'))

        test.log.step('13. reg/act/deact/int/eras CF - all conditional')
        test.expect(test.dut.at1.send_and_verify(f'ATD**004*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*004*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#004*{nat_r1_phone_num}*11*10#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#004*{nat_r1_phone_num}*11*10#{semicolon}', 'OK|ERROR'))
        test.expect(test.dut.at1.send_and_verify(f'ATD##004*{nat_r1_phone_num}*11*10#{semicolon}', 'OK|ERROR'))

        test.log.step('14. activation/deactivation/int Call waiting (11=voice)')
        test.expect(test.dut.at1.send_and_verify(f'ATD*43*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD#43*11#{semicolon}', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#43*11#{semicolon}', 'OK'))

        test.log.step('15. act/deact/int Bar All Outgoing Calls')
        test.expect(test.dut.at1.send_and_verify(f'ATD*33*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD#33*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#33*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('16. act/deact/int Bar All Outgoing and Incoming Calls')
        test.expect(test.dut.at1.send_and_verify(f'ATD*331*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD#331*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#331*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('17. Act/deact/int BAOIC exc.home.')
        test.expect(test.dut.at1.send_and_verify(f'ATD*332*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD#332*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#332*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('18. Act/deact/int. BAIC.')
        test.expect(test.dut.at1.send_and_verify(f'ATD*35*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD#35*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#35*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('19. Act/deact/int. BAIC roaming.')
        test.expect(test.dut.at1.send_and_verify(f'ATD*351*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD#351*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))
        test.expect(test.dut.at1.send_and_verify(f'ATD*#351*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('20. Deact All Barring Services.')
        test.expect(test.dut.at1.send_and_verify(f'ATD#330*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('21. Deact All Out Barring Services.')
        test.expect(test.dut.at1.send_and_verify(f'ATD#333*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.log.step('21. Deact. All Inc.Barring Services.')
        test.expect(test.dut.at1.send_and_verify(f'ATD#335*{net_pin}*11#{semicolon}', 'OK|ERROR',timeout=20))

        test.expect(test.dut.at1.send_and_verify(f'ATD##002#{semicolon}', 'OK|ERROR'))


    def cleanup(test):
        pass




if "__main__" == __name__:
    unicorn.main()
