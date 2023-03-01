#responsible: jin.li@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095505.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.configuration import dual_sim_operation

import re

class Test(BaseTest):

    '''
    TC0095505.001 - DualSimMode2Basic
    Intention:
    Tests for Test basic function of dual sim switch mode2
    Subscriber: 1
    '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPIO/Mode/FNS","std"', expect='OK'))

    def run(test):
        test.log.step('1. Try to set AT^SCFG="sim/dualmode","2".')
        test.expect(test.dut.dstl_enable_dual_sim_mode(2))

        test.log.step('2. Change AT^SCFG="GPIO/mode/FNS" to "GPIO" and restart module.')
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPIO/Mode/FNS","gpio"', expect='OK'))
        test.expect(test.dut.dstl_restart())

        test.log.step('3. Set AT^SCFG="sim/dualmode","2" again.')
        test.expect(test.dut.dstl_enable_dual_sim_mode(2))

        test.log.step('4. Query the SIM card1 IMSI via AT+CIMI.')
        test.expect(test.dut.dstl_enter_pin(test.dut.sim))
        test.sleep(2)
        find_imsi = test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect='\s\d{15}\s'))
        if find_imsi:
            imsi_1 = re.search('\d{15}', test.dut.at1.last_response).group(0)
        else:
            imsi_1 = None

        test.log.step(' 5. Switch to SIM slot2 via AT^SCFG= "SIM/CS,"3".')
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.sleep(2)
        # SIM card 2 may be not inserted to Module
        if hasattr(test.dut, "sim2") and test.dut.sim2:
            test.expect(test.dut.dstl_enter_pin(test.dut.sim2))
            test.sleep(2)

        test.log.step('6. Query the SIM card2 IMSI via AT+CIMI.')
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', expect='(OK|SIM not inserted)'))
        imsi_2 = re.search('\d{15}', test.dut.at1.last_response)
        if imsi_2:
            imsi_2 = imsi_2.group(0)
        test.expect(imsi_1 != imsi_2, msg="IMSI number is same, switching slot does not work.")

    def cleanup(test):
        test.log.step('7. Try to set AT^SCFG="GPIO/mode/FNS" to "std"')
        test.expect(test.dut.at1.send_and_verify('at^scfg="GPIO/Mode/FNS","std"', expect='OK'))
        test.dut.dstl_switch_to_sim_slot1()
        test.dut.dstl_disable_dual_sim_mode()
        test.expect(test.dut.dstl_restart())


if '__main__' == __name__:
    unicorn.main()
