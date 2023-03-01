# responsible: wen.liu@thalesgroup.com
# location: Dalian
# TC0093950.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.call import enable_voice_call_with_ims
from dstl.configuration import configure_scfg_provider_profile
from dstl.security import set_sim_waiting_for_pin1


class Test(BaseTest):
    """
    TC0093950.001 - TpAtCavimsBasic
    Intention:  This procedure provides basic tests for the VoLTE related command AT+CAVIMS.
    Subscriber: 1
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_enable_voice_call_with_ims(manually_register_to_lte=True))
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        pass

    def run(test):
        test.log.step("1. Test/Read command without PIN")
        test.expect(test.dut.at1.send_and_verify('at+cpin?', expect='\+CPIN: SIM PIN\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.log.step("2. Test/Read command with PIN and register on 2G")
        test.expect(test.dut.dstl_enter_pin())
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.log.step("3. Test/Read command with PIN and register on 3G")
        test.expect(test.dut.dstl_register_to_umts())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.log.step("4. Test/Read command with PIN and register on 4G")
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.log.info("Reading more information for provider condition for VOLTE.")
        test.dut.at1.send_and_verify("AT+CGDCONT?")
        test.dut.at1.send_and_verify("AT+CGACT?")
        test.dut.at1.send_and_verify("AT+CVMOD?")
        test.dut.at1.send_and_verify("AT^SCFG?")
        test.log.step("5. Check invalid parameters")
        test.expect(test.dut.at1.send_and_verify('at+cavims', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+cavims=0', expect='\+CME ERROR: unknown'))
        test.expect(test.dut.at1.send_and_verify('at+cavims=1', expect='\+CME ERROR: unknown'))
        test.log.step("6. Check influence on current setting for AT&F")
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at&f', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at&f', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.log.step("7. Check influence on current setting for AT&W")
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.expect(test.dut.at1.send_and_verify('at&w', expect='OK'))
        test.expect(test.dut.dstl_restart())
        test.sleep(10)
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(10)
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.log.step("8. Check influence on current setting for ATZ")
        test.expect(test.dut.dstl_register_to_gsm())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.expect(test.dut.at1.send_and_verify('atz', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        test.expect(test.dut.dstl_register_to_lte())
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.expect(test.dut.at1.send_and_verify('atz', expect='OK'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 1\s+OK'))
        test.log.step("9. Check influence on current setting for airplane mode")
        test.dut.dstl_set_airplane_mode()
        test.expect(test.dut.at1.send_and_verify('at+cavims=?', expect='\s+\+CAVIMS: \(0,1\)'))
        test.expect(test.dut.at1.send_and_verify('at+cavims?', expect='\+CAVIMS: 0\s+OK'))
        pass

    def cleanup(test):
        test.dut.dstl_set_full_functionality_mode()
        test.dut.dstl_switch_on_provider_auto_select()
        pass


if '__main__' == __name__:
    unicorn.main()
