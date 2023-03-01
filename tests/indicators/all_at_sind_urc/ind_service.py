# author: feng.han@thalesgroup.com
# responsible: feng.han@thalesgroup.com
# location: Dalian
# TC0065649.001,TC0095611.001
# removing antenna does not work on Berlin LTe testnetwork, best to use official networks

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.auxiliary import check_urc
from dstl.network_service import register_to_network
from dstl.supplementary_services import lock_unlock_facility
from dstl.auxiliary.devboard.devboard import dstl_remove_sim, dstl_insert_sim, dstl_switch_antenna_mode_via_dev_board
# from dstl.network_service.attach_to_network import dstl_enter_pin


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_unlock_facility(facility="SC", lock=True)
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        pass

    def run(test):
        test.log.h2(" Check the status of indicator <service> in following situations:")
        test.expect(test.dut.at1.send_and_verify('at^sind=service,1', expect='\^SIND: service,1.*'))
        test.expect(test.dut.at1.send_and_verify('at^sind=service,2', expect='\^SIND: service,1.*'))

        test.log.h2("1. status after shutdown and startup with/wqithout registering")
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.at1.send_and_verify('at^sind=service,1', expect='\^SIND: service,1.*'))
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_check_urc('\+CIEV: service,1'))
        test.sleep(5)

        test.log.step("1.1 manually deregister from network")
        test.expect(test.dut.at1.send_and_verify('at+cops=2', expect='OK'))
        test.expect(test.dut.dstl_check_urc('\+CIEV: service,0'))
        test.log.step("1.2 manually reregister to the network")
        test.expect(test.dut.at1.send_and_verify('at+cops=0', expect='OK'))
        test.expect(test.dut.dstl_check_urc('\+CIEV: service,1'))

        test.log.h2("2. remove / insert the SIM with PIN disabled")
        test.dut.dstl_lock_unlock_facility(facility="SC", lock=False)
        test.expect(test.dut.at1.send_and_verify('at^sind=service,1', expect='\^SIND: service,1.*'))

        test.log.step("2.1 remove the SIM")
        test.dut.dstl_remove_sim(check_with_module=False)
        test.dut.at1.wait_for_strict('\+CIEV: service,0', timeout=15)
        test.expect(test.dut.at1.send_and_verify('at^sind=service,2', expect='\^SIND: service,1,0.*'))

        test.log.step("2.2 insert the SIM")
        test.dut.dstl_insert_sim(check_with_module=False)
        test.expect(test.dut.at1.verify_or_wait_for('\+CIEV: service,1', timeout=15))

        test.log.h2("3. remove / insert the SIM with PIN enabled")
        test.dut.dstl_lock_unlock_facility(facility="SC", lock=True)
        test.expect(test.dut.at1.send_and_verify('at^sind=service,1', expect='\^SIND: service,1.*'))

        test.log.step("3.1 remove the SIM")
        test.dut.dstl_remove_sim(check_with_module=False)
        test.dut.at1.wait_for_strict('\+CIEV: service,0', timeout=15)
        test.expect(test.dut.at1.send_and_verify('at^sind=service,2', expect='\^SIND: service,1,0.*'))

        test.log.step("3.2 insert the SIM")
        test.dut.dstl_insert_sim(check_with_module=False)
        test.expect(test.dut.at1.send_and_verify('at^sind=service,2', expect='\^SIND: service,1,0.*'))
        test.dut.dstl_enter_pin()
        test.expect(test.dut.at1.verify_or_wait_for('\+CIEV: service,1', timeout=15))

        test.log.h2("4. remove/attach the antennas")
        # does not work on the Berlin LTE testnetwork - all signals are too strong!
        # but it works on official providers, here Vodafone Germany was good
        test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=1, mode="OFF")
        test.expect(test.dut.at1.wait_for_strict('\+CIEV: service,0', timeout=50))
        test.sleep(3)
        test.dut.dstl_switch_antenna_mode_via_dev_board(ant_nr=1, mode="ON1")
        test.expect(test.dut.at1.wait_for_strict('\+CIEV: service,1', timeout=50))
        pass

    def cleanup(test):
        test.dut.dstl_insert_sim(check_with_module=False)
        test.sleep(2)
        test.dut.dstl_lock_unlock_facility(device_sim=test.dut.sim, facility="SC", lock=True)
        pass


if '__main__' == __name__:
    unicorn.main()
