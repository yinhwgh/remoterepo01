#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0083760.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.call import setup_voice_call
from dstl.call import get_release_cause
from dstl.network_service import customization_network_types

import re

class Test(BaseTest):
    '''
    TC0083760.001 - RejectionCauseForWaitingMTCall
    Intention: Disconnect all waiting voice, data, fax calls with AT^SHUP with different rejection causes.
    Subscriber: 3
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_enter_pin()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.r2.dstl_detect()
        test.expect(test.r2.dstl_register_to_network())

    def run(test):
        test.dut_voice_num = test.dut.sim.nat_voice_nr
        test.r1_voice_num = test.r1.sim.nat_voice_nr
        test.r2_voice_num = test.r2.sim.nat_voice_nr

        test.release_cause_map = {
                            1: '(.*Unassigned \\(unallocated\\) number.*|.*Unassigned/unallocated number.*)',
                            16: '(.*normal call clearing.*|.*Normal call clearing.*)',
                            17: '.*User busy.*',
                            18: '.*No user responding.*',
                            21: '.*Call rejected.*',
                            27: '.*Destination out of order.*',
                            31: '.*Normal, unspecified.*',
                            88: '(.*incompatible destination.*|.*Incompatible destination.*)',
                            128: '(.*Normal call clearing.*|.*Call rejected.*)'}

        release_causes =test.dut.dstl_get_supported_release_cause()
        rats_dict = test.dut.dstl_customized_network_types()
        rats = ['GSM', 'UMTS', 'LTE']
        for rat in rats:
            if rats_dict[rat] != True:
                rats.remove(rat)
        test.log.info(f"Module supports {rats}.")
        
        test.init_device(test.dut)
        test.init_device(test.r1)
        test.init_device(test.r2)

        release_call_number = '0'
        for rat in rats:
            test.log.step(f"Testing for rat {rat}.")
            register_to_network = eval(f"test.dut.dstl_register_to_{rat.lower()}")
            registered = test.expect(register_to_network())
            if not registered:
                test.log.error(f"Cannot register to {rat}, skip tests for network {rat}.")
            for cause in release_causes:
                network_response = "NO CARRIER"
                ceer_response = f'\+CEER: {test.release_cause_map[cause]}'
                test.log.step('1. Disconnect one call')
                test.log.step('1.a.1  Disconnect Active call (MO)')
                test.release_voice_active_call(cause, network_response, ceer_response, is_mo=True)
                
                test.log.step('1.a.2  Disconnect Active call (MT)')
                test.release_voice_active_call(cause, network_response, ceer_response, is_mo=False)

                test.log.step('1.b  Disconnect held call -> Active call')
                test.release_voice_held_or_waiting_call_active_call_in_order(cause, network_response,
                                                                         ceer_response, is_held=True)

                test.log.step("1.c Disconnect dialing call")
                test.expect(test.dut.at1.send_and_verify(f'ATD"{test.r1_voice_num}";', 'OK'))
                test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: 1,0,2,0,0'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},0'))
                test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
                test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
                test.expect(test.r1.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))

                test.log.step("1.d Disconnect alerting call")
                test.expect(test.dut.at1.send_and_verify(f'ATD{test.r1_voice_num};', 'OK'))
                test.expect(test.r1.at1.wait_for("RING"))
                test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: 1,0,3,0,0,"{test.r1_voice_num}"'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},0'))
                test.expect(test.r1.at1.wait_for(network_response, timeout=10))
                test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
                test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
                test.expect(test.r1.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))

                test.log.step("1.e Disconnect incoming call")
                test.expect(test.r1.at1.send_and_verify(f'ATD"{test.dut_voice_num}";', 'OK'))
                test.expect(test.dut.at1.wait_for("RING"))
                test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: 1,1,4,0,0,"{test.r1_voice_num}"'))
                test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},0'))
                test.expect(test.r1.at1.wait_for(network_response))
                test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
                test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
                test.expect(test.r1.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))

                test.log.step("1.f Disconnect waiting call -> active")
                test.release_voice_held_or_waiting_call_active_call_in_order(cause, network_response,
                                                                         ceer_response, is_held=False)

                test.log.step('2. Disconnect two calls the same time.')
                test.log.step("2.a Disconnect active call & waiting call")
                test.release_voice_held_or_waiting_call_active_call_in_parallel(cause, network_response,
                                                                        ceer_response, is_held=False)

                test.log.step("2.a Disconnect active call & held call")
                test.release_voice_held_or_waiting_call_active_call_in_parallel(cause, network_response,
                                                                        ceer_response, is_held=True)


    def cleanup(test):
        test.log.info('***Test End***')
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        test.r2.dstl_release_call()
        test.log.info("In case that module cannot make calls any more, restart is necessary.")
        test.dut.dstl_restart()
    
    def init_device(test, device):
        test.log.h3(f"Initiating device {device.name}.")
        device.at1.send_and_verify("AT+CMEE=2")
        device.at1.send_and_verify("AT+CCWA=1,1")
        device.at1.send_and_verify("AT+CCWA=1,2")
        device.at1.send_and_verify("ATX4")
        device.at1.send_and_verify("AT+CLIR=2")

    def release_voice_active_call(test, cause, network_response, ceer_response, is_mo=False):
        if is_mo == True:
            test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr, "OK"))
            mode = 0
        else:
            test.expect(test.r1.dstl_voice_call_by_number(test.dut, test.dut.sim.nat_voice_nr, "OK"))
            mode = 1
        test.sleep(1)
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: 1,{mode},0,0,0'))
        test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},1'))
        test.expect(test.r1.at1.wait_for(network_response))
        test.r1.dstl_release_call()
        test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
    
    def release_voice_held_or_waiting_call_active_call_in_order(test, cause, network_response,
                                                            ceer_response, is_held):
        active_index, held_or_wait_index, \
        active_interface, held_or_wait_interface = test.setup_voice_active_and_held_or_waiting_calls(is_held)
        if held_or_wait_index > 0:
            test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},{held_or_wait_index}'))
            test.expect(held_or_wait_interface.wait_for(network_response))
            test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
            test.expect(held_or_wait_interface.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
            test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: \d,0,0,0,0'))
        else:
            held_or_wait = "held" if is_held == True else "wait"
            test.expect(held_or_wait_index > 0, msg=f"No {held_or_wait} call found.")
        if active_index > 0:
            test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},{active_index}'))
            test.expect(active_interface.wait_for(network_response))
            test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
            test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
            test.expect(active_interface.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
        else:
            test.expect(active_index > 0, msg="No active call found.")
            test.dut.dstl_release_call()
            test.r1.dstl_release_call()
            test.r2.dstl_release_call()

    def release_voice_held_or_waiting_call_active_call_in_parallel(test, cause, network_response, ceer_response, is_held=True):
        active_index, held_or_wait_index, active_interface, held_or_wait_interface= test.setup_voice_active_and_held_or_waiting_calls(is_held)
        test.expect(active_index > 0, msg= "No active call found in AT+CLCC.")
        test.expect(held_or_wait_index > 0, msg= "No held or waiting call found in AT+CLCC.")
        test.expect(test.dut.at1.send_and_verify(f'AT^SHUP={cause},0'))
        test.expect(test.r1.at1.wait_for(network_response))
        test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
        test.expect(test.r2.at1.wait_for(network_response))
        test.expect(test.dut.at1.send_and_verify("AT+CEER", ceer_response))
        test.expect(test.dut.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
        test.expect(test.r1.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))
        test.expect(test.r2.at1.send_and_verify("AT+CLCC", "^((?!CLCC:).)*$"))


    def setup_voice_active_and_held_or_waiting_calls(test, is_held=True):
        mo_mode = '0'
        mt_mode = '1'
        active_state = '0'
        held_state = '1'
        wait_state = '5'
        
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1_voice_num, "OK"))
        test.sleep(1)
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', f'\+CLCC: 1,0,0,0,0'))
        test.sleep(1)
        test.expect(test.r2.at1.send_and_verify(f'ATD{test.dut_voice_num};', 'OK'))
        test.dut.at1.wait_for(f'\+CCWA: "{test.r2_voice_num}",\d+,1,,0')
        if is_held == True:
            test.expect(test.dut.at1.send_and_verify('AT+CLCC'))
            test.log.info("****** Hold current active call and answer new coming call. ******")
            test.expect(test.dut.at1.send_and_verify("AT+CHLD=2", "OK"))
            call_state = held_state
            active_mode = mt_mode
            active_number = test.r2_voice_num
            held_or_wait_mode = mo_mode
            held_or_wait_number = test.r1_voice_num
            active_interface = test.r2.at1
            held_or_wait_interface = test.r1.at1
        else:
            test.log.info("****** Keep call with r1 active, call with r2 waiting.")
            call_state = wait_state
            active_mode = mo_mode
            active_number = test.r1_voice_num
            held_or_wait_mode = mt_mode
            held_or_wait_number = test.r2_voice_num
            active_interface = test.r1.at1
            held_or_wait_interface = test.r2.at1
        test.sleep(1)
        test.expect(test.dut.at1.send_and_verify('AT+CLCC', 'OK'))
        clcc_response = test.dut.at1.last_response
        active_index = test.find_index_from_clcc_response(mode=active_mode, state=active_state,
                                                          number=active_number,
                                                          clcc_response=clcc_response)
        held_or_wait_index = test.find_index_from_clcc_response(held_or_wait_mode, call_state,
                                                                held_or_wait_number,
                                                                clcc_response=clcc_response)
        return active_index, held_or_wait_index, active_interface, held_or_wait_interface
    
    def find_index_from_clcc_response(test, mode, state, number, clcc_response):
        index = 0
        find_clcc = re.search(f'\+CLCC: (\d),{mode},{state},0,0,"{number}"', clcc_response)
        if find_clcc:
            index = int(find_clcc.group(1))
        else:
            test.log.info(f'No "\+CLCC: (\d),{mode},{state},0,0,\"{number}\"" found in CLCC response.')
        return index

    def clear_release_cause(test):
        test.dut.at1.send_and_verify("AT+CEER=0")
        test.expect(test.dut.at1.send_and_verify("AT+CEER", "No cause information available"),
                    msg="Fail to clear release cause.")

if "__main__" == __name__:
    unicorn.main()

