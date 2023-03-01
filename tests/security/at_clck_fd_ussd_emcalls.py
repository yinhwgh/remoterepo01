# responsible: christoph.dehm@thalesgroup.com
# author: christoph.dehm@thalesgroup.com
# location: Berlin, Beijing
# TC0091841.001
# info: converted from former Pegasus script: \it\sim\TpAtClckFdUssdEmC.java

""" description:
    Check FD-Lock for USSD-, *#- commands and emergency calls
    1. check USSD action if they work generally
    2. Lock FD
    3. try some voice calls to check if lock is working
    4. ALL USSD actions should be prohibited now
    5. ALL EM-CALLs should work
    6. ALL *  # -sequences should be prohibited
    7. write USSD string to FD-PB
    8. lock FD-PB again
    9. only one USSD action should work, the other should not
    10. all emergency calls should work
    11. only one  *# -sequence should work, others are prohibited

    Taken from old MIT-STP: fd_lock_other_all_01.stp
    wm1: DUT_ASC0
"""

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.supplementary_services import lock_unlock_facility
from dstl.phonebook import phonebook_handle
from dstl.network_service import network_monitor


class Test(BaseTest):

    exp_resp_call_barred = '\\+CME ERROR: 320'
    atc_monitoring = 'at^SMONI'
    exp_resp_clcc = '\+CLCC: 1,0,0,0,0,"911",'

    def setup(test):
        test.tln_dut_nat = test.dut.sim.nat_voice_nr

        test.dut.dstl_detect()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_enter_pin()
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=False)

        # delete phonebook FD
        test.dut.dstl_clear_select_pb_storage('FD')
        # change to SM phonebook
        test.dut.dstl_set_pb_memory_storage('SM')
        test.dut.dstl_get_supported_pb_memory_list()

        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))

        global exp_resp_call_barred
        global exp_resp_clcc
        global atc_monitoring
        if test.dut.platform == 'XGOLD':
            exp_resp_call_barred = '\\+CME ERROR: 257'  # Kingston/Dublin and others
            exp_resp_clcc = '\+CLCC: 1,0,0,0,0\s+'
            atc_monitoring = 'at^MONI'
        pass

    def run(test):
        star109hash = '*109#'
        star100hash = '*100#'
        global exp_resp_call_barred
        global exp_resp_clcc

        test.log.step(' 1. check if USSD action work in general ')
        test.expect(test.dut.at1.send_and_verify('at+CUSD=1', 'OK'))
        test.expect(test.dut.at1.send_and_verify(f'ATD"{star109hash}";', 'OK', timeout=15))

        ret = test.dut.at1.wait_for_strict(".*\\+CUSD: [0|2],\"UNKNOWN APPLICATION\".*", 20)
        if ret is False:
            test.dut.at1.send_and_verify('ati', 'OK')
            test.expect(test.dut.at1.send_and_verify(f'ATD{star100hash};', 'OK', timeout=15))
            ret = test.dut.at1.wait_for_strict(".*\\+CUSD: [0|2],\"UNKNOWN APPLICATION\".*", 20)

            if ret is False:
                test.dut.at1.close()
                test.sleep(3)
                test.dut.at1.open()
                test.expect(test.dut.at1.send_and_verify(f'ATD{star109hash};', 'OK', timeout=15))
                ret = test.dut.at1.wait_for_strict(".*\\+CUSD: [0|2],\"UNKNOWN APPLICATION\".*", 60)

        resp = test.dut.at1.last_response
        if 'CUSD: 0' in resp or 'CUSD: 2' in resp:
            print('do nothing0 = No further user action required, 2 = terminated by network')
            # wait approx 10 sec. to let the module get back from CSFB to LTE
            test.sleep(10)
        else:
            test.dut.at1.send_and_verify('at+CUSD=2', 'OK')

        test.log.step(' 2. lock FD PB ')
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=True)
        test.dut.dstl_get_supported_pb_memory_list()  # SM PB should not appear anymore!

        test.log.step(' 3. try some voice calls if lock is really enabled')
        ret = test.expect(test.dut.at1.send_and_verify(f'ATD{test.tln_dut_nat};', exp_resp_call_barred, timeout=15))
        if ret is False:
            test.expect(False, critical=True,
                        msg="some important condition not met yet: voice calls should be barred here!")
        # wait approx 10 sec. to let the module get back from CSFB to LTE
        test.sleep(10)

        test.log.step(' 4. first real test: all USSD actions should be prohibited now ')
        ret = test.expect(test.dut.at1.send_and_verify(f'ATD"{star109hash}";', exp_resp_call_barred, timeout=15))
        if ret is False:
            test.sleep(10)
            test.dut.at1.send_and_verify('at+CLCC', 'OK')
        ret = test.expect(test.dut.at1.send_and_verify(f'ATD{star100hash};', exp_resp_call_barred, timeout=15))
        if ret is False:
            test.sleep(10)
            test.dut.at1.send_and_verify('at+CLCC', 'OK')

        test.log.step(' 5. all emergency calls should work')

        global atc_monitoring
        # check first, if module is registered to Ericsson test network, otherwise ignore Emergency Calls!
        test.expect(test.dut.at1.send_and_verify(atc_monitoring))

        resp = test.dut.at1.last_response
        if ',262,95,' in resp or ' 262  95 ' in resp:
            test.expect(test.dut.at1.send_and_verify('atd911;'))
            test.attempt(test.dut.at1.send_and_verify, 'at+clcc', exp_resp_clcc, retry=5, sleep=1)
            test.dut.at1.send_and_verify('at+chup')
            test.sleep(7)  # in case CSFB switch back to 4G takes some time
        else:
            test.expect(False, msg="step 5/emergency calls: no Ericsson test network found - check manually!")

        test.log.step(' 6. ALL *  # -sequences should be prohibited')
        test.expect(test.dut.at1.send_and_verify('atd*#43#;', exp_resp_call_barred))
        test.expect(test.dut.at1.send_and_verify('atd*43#;', exp_resp_call_barred))
        test.expect(test.dut.at1.send_and_verify('atd#43#;', exp_resp_call_barred))

        # BUT: such AT-Cmds should work (they do the same as *#43 does!
        test.expect(test.dut.at1.send_and_verify('at+CCWA?', "\+CCWA: 0.*OK"))
        test.expect(test.dut.at1.send_and_verify('at+CCWA=1'))
        test.expect(test.dut.at1.send_and_verify('at+CCWA?', "\+CCWA: 1.*OK"))

        test.log.step(' 7. write USSD string to FD-PB')
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=False)
        test.dut.dstl_set_pb_memory_storage('FD')
        test.dut.dstl_write_pb_entries(1, '*109#', text='USSDTN')
        test.dut.dstl_write_pb_entries(2, '*43#', text='CCWATN')
        test.expect(test.dut.at1.send_and_verify('at+CPBR=1,10', '109.*USSDTN.*43.*CCWATN'))
        test.dut.dstl_set_pb_memory_storage('SM')
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))   # is changed in dstl_set_pb_memory_storage()

        test.log.step(' 8. lock FD-PB again')
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=True)

        test.log.step(' 9. one USSD action should work now, the other should not ')
        test.expect(test.dut.at1.send_and_verify(f'ATD{star109hash};', 'OK', timeout=15))
        test.dut.at1.wait_for_strict(".*\\+CUSD: [0|2],\"UNKNOWN APPLICATION\".*", 20)
        test.sleep(7)
        test.expect(test.dut.at1.send_and_verify(f'ATD{star100hash};', exp_resp_call_barred, timeout=15))

        test.log.step(' 10. all emergency calls should work')
        # check first, if module is registered to Ericsson test network, otherwise ignore Emergency Calls!
        test.expect(test.dut.at1.send_and_verify(atc_monitoring))
        resp = test.dut.at1.last_response
        if ',262,95,' in resp or ' 262  95 ' in resp:
            test.expect(test.dut.at1.send_and_verify('atd911;'))
            test.attempt(test.dut.at1.send_and_verify, 'at+clcc', exp_resp_clcc, retry=5, sleep=1)
            test.dut.at1.send_and_verify('at+chup')
            test.sleep(7)  # in case CSFB switch back to 4G takes some time
        else:
            test.expect(False, msg="step 10/emergency calls: no Ericsson test network found - check manually!")

        test.log.step(' 11. only one  *# -sequences should work, others are prohibited')
        test.expect(test.dut.at1.send_and_verify('atd*#43#;', exp_resp_call_barred))
        test.expect(test.dut.at1.send_and_verify('atd*43#;', '\\+CCWA: '))
        test.expect(test.dut.at1.send_and_verify('atd#43#;', exp_resp_call_barred))

        pass

    def cleanup(test):
        test.log.info('***Test End, clean up***')
        test.dut.dstl_lock_unlock_facility(facility='FD', lock=False)

        # delete phonebook FD
        test.dut.dstl_clear_select_pb_storage('FD')
        # change to SM phonebook
        test.dut.dstl_set_pb_memory_storage('SM')
        test.dut.at1.send_and_verify('at+CCWA=0')
        test.dut.at1.send_and_verify('at+CUSD=0')
        pass


if "__main__" == __name__:
    unicorn.main()
