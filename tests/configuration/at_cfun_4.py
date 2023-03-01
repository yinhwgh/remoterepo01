#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0087400.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.configuration import functionality_modes

class  AtCfun4(BaseTest):
    """
        TC0087400.001 - AtCfun4
        Check if module logs off from the network and SIM interface is powered on when Cfun=4 mode is active.
        Check if module is able to log on to the network and SIM interface is powered on when Cfun=1 mode is active.
        Debugged: Serval
    """
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

    def run(test):
        """
            Check commands when +CFUN: 1 or +CFUN: 4
        """
        test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))
        # Check twice without rst and with rst equals to 0
        rst_values = ['', ',0']
        for rst in rst_values:
            if rst is '':
                with_rst_0 = False
                log_step=1
                test.log.info(f"***************************{log_step}. AtCfun4: without rst - begin ***************************")
            else:
                log_step=2
                with_rst_0 = True
                test.log.info(f"***************************{log_step}. AtCfun4: rst is 0 - begin ***************************")
            test.log.info(f"{log_step}.1 CFUN1,attach to network")
            test.expect(test.dut.dstl_register_to_network())
            test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: [012],1.*"))
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

            test.log.info(f"{log_step}.2 CFUN4 with pin: disconnect network, pin status keeps")
            test.expect(test.dut.at1.send_and_verify("at+cfun=4{}".format(rst), expect="\s+\^SYSSTART AIRPLANE MODE\s+",
                                                         wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 4\s+"))
            test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: [012],[04]\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+OK\s+"))
            
            test.log.info(f"{log_step}.3 CFUN1 with pin: connected to network, pin status keeps")
            test.expect(test.dut.dstl_set_full_functionality_mode(restart=False, with_rst_0=with_rst_0))
            test.attempt(test.dut.at1.send_and_verify, "at+creg?", expect="\s+\+CREG: [012],1.*", retry=10, sleep=5)
            test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+OK\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))
            test.expect(test.dut.dstl_restart())
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

            test.log.info(f"{log_step}.4 CFUN4 without pin, enter pin")
            test.expect(test.dut.at1.send_and_verify("at+cfun=4{}".format(rst), expect="\s+\^SYSSTART AIRPLANE MODE\s+",
                                                         wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 4\s+"))
            # for serval, in CFUN 4 state, USIM connection keeps
            test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))
            test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(test.dut.sim.pin1), wait_after_send=3)
            test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: [012],[04]\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+READY\s+"))

            test.log.info(f"{log_step}.5 CFUN1: pin status keeps, connected to network")
            test.expect(test.dut.dstl_set_full_functionality_mode(restart=False, with_rst_0=with_rst_0))
            test.attempt(test.dut.at1.send_and_verify, "at+creg?", expect="\s+\+CREG: [012],1\s+", retry=10, sleep=5)
            test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+READY\s+"))
            test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))
            if rst is '':
                test.log.info(
                        f"***************************{log_step}. AtCfun4: without rst - end ***************************")
            else:
                test.log.info(f"***************************{log_step}. AtCfun4: rst is 0 - end ***************************")

    def cleanup(test):
        test.expect(test.dut.dstl_restart())


if "__main__" == __name__:
    unicorn.main()
