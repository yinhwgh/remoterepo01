#responsible: cong.hu@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0095626.001, TC0095626.002
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.configuration import dual_sim_operation
from dstl.security import set_sim_waiting_for_pin1

class Test(BaseTest):
    """
    TC0095626.001, TC0095626.002 - TpAtCmerSimSwitchCross
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', expect='OK'))
        test.dut.dstl_set_sim_waiting_for_pin1()
        test.expect(test.dut.dstl_restart())

    def run(test):
        test.log.info('1.Enable "service" indicator')
        test.log.info('1.Enable SIM dual Mode')
        test.expect(test.dut.at1.send_and_verify('at^scfg=\"GPIO/Mode/FNS\",\"std\"', '.*OK.*'))
        test.expect(test.dut.dstl_enable_dual_sim_mode())
        test.expect(test.dut.dstl_restart())
        test.log.info('2.Enable "service" indicator')
        test.expect(test.dut.at1.send_and_verify('at^sind="service",1', expect='\^SIND: service,1,0'))
        test.log.info('3.Switch to SIM slot 1')
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.log.info('4.Enter SIM PIN')
        test.expect(test.dut.dstl_enter_pin())
        test.log.info('5.Wait for +CIEV: "service","1" URC')
        test.expect(test.dut.at1.wait_for('\+CIEV: service,1', append=True))
        test.log.info('6.Switch to SIM slot 2')
        test.expect(test.dut.dstl_switch_to_sim_slot2())
        test.log.info('7.Wait for +CIEV: "service","0" URC')
        test.expect(test.dut.at1.wait_for('\+CIEV: service,0', append=True))
        test.log.info('8.Enter PIN for SIM2')
        test.expect(test.dut.dstl_enter_pin(device_sim=test.dut.sim2))
        test.log.info('9.Wait for +CIEV: "service","1" URC')
        test.expect(test.dut.at1.wait_for('\+CIEV: service,1', append=True))

        # Since QCT product does not support AT+CMER, step
        # "9, repeat step4 to step8 with at+cmer =0/2/3(If DUT is a QCT platform product, you can
        # ignore this step as it does not support "AT+CEER" command)."
        # is not implemented.
        # Output error for product who supports the function, to avoid missing validation points
        test.dut.at1.send_and_verify("AT+CMER?", 'ERROR|OK')
        if 'OK' in test.dut.at1.last_response:
            test.expect(False, msg='Step "repeat step4 to step8 with at+cmer =0/2/3" is not implemented.')
        else:
            test.log.info('Module does not support AT+CMER, skip tests for '
                          '"repeat step4 to step8 with at+cmer =0/2/3".')

    def cleanup(test):
        test.log.info('1.Switch back to SIM slot 1')
        test.expect(test.dut.dstl_switch_to_sim_slot1())
        test.expect(test.dut.dstl_disable_dual_sim_mode())
        test.expect(test.dut.at1.send_and_verify('at^scfg=\"GPIO/Mode/FNS\",\"gpio\"', '.*OK.*'))
        test.log.info('2.Restart the module.')
        test.expect(test.dut.dstl_restart())

if '__main__' == __name__:
    unicorn.main()
