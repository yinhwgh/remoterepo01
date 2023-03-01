# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0087401.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard
from dstl.network_service import register_to_network
from dstl.configuration import shutdown_smso
from dstl.auxiliary import init


# dut_devboard has to be configured to the port of MC, e.g. dut_usb_mctst
class AtCfun0(BaseTest):
    """
       TC0087401.001 - AtCfun0
       The module should log off from network and SIM interface should be powered off when Cfun=0 mode is active.
       Check if module is able to log on to the network and SIM interface is powered on when Cfun=1 mode is active.
       Subscribers: dut, MCTest
       Debugged: Serval
    """

    def setup(test):
        test.expect(test.dut.dstl_insert_sim())
        test.dut.dstl_detect()
        pass

    def run(test):
        cfun_test_resp = "\+CFUN: \(0,1,4\),\(0[,-]1\)"
        test.log.step("1. Register to network")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_check_network_status('any'))

        test.log.step("2. Check current CFUN value: CFUN: 1")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+", wait_after_send=1))

        test.log.step("3. Set module to sleep mode CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+cfun=0,0", expect="\s+\^SYSSTART AIRPLANE MODE\s+",
                                                 wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))

        test.log.step("4. Check CFUN setting CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 0\s+"))

        test.log.step("5. Module should be log off network when CFUN: 0")
        test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: \d,[04]\s+"))
        test.expect(test.dut.at1.send_and_verify("at+cpin=?", "\s+OK\s+"))
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s\+CME ERROR: SIM not inserted\s", wait_after_send=5))

        test.log.step("6. Set module back to normal mode CFUN: 1")
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,0", "\s\^SYSSTART\s", wait_for="\s\^SYSSTART\s",
                                                 wait_after_send=5))

        test.log.step("7. Pin authentication should be lost, CFUN: 1")
        test.expect(test.dut.at1.send_and_verify("at+cpin=?", "\s+OK\s+"))
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))
        test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: \d,[024]\s+"))

        test.log.step("8. Check current CFUN settings, CFUN: 1")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

        test.log.step("9. Input pin value, module should be attached to network, CFUN: 1")
        test.expect(test.dut.dstl_register_to_network())

        test.expect(test.dut.dstl_check_network_status('any'))

        test.log.step("10. Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("11. Check CFUN, CFUN: 1")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

        test.log.step("12. Check CPIN state after restart")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))

        test.log.step("13. Set module to sleep mode CFUN:0")
        if 'VIPER' is test.dut.project:
            test.sleep(5)
        test.expect(test.dut.at1.send_and_verify("at+cfun=0,0", expect="\s+\^SYSSTART AIRPLANE MODE\s+",
                                                 wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))

        test.log.step("14. Check CFUN settings: CFUN:0")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 0\s+"))

        test.log.step("15. Input pin when CFUN:0, error is returned")
        test.expect(test.dut.at1.send_and_verify("at+cpin=\"{}\"".format(test.dut.sim.pin1),
                                                 "\s\+CME ERROR: (SIM not inserted|SIM failure)\s"))

        test.log.step("16. Set module back to normal mode")
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,0", "\^SYSSTART", wait_for="\^SYSSTART", wait_after_send=5))

        test.log.step("17. Check pin status after setting back to CFUN:1")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))

        test.log.step("18. Check CFUN settings")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

        test.log.step("19. Remove SIM card")
        test.expect(test.dut.dstl_remove_sim())
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM not inserted\s+"))

        test.log.step("20. Switch off Module")
        test.expect(test.dut.dstl_insert_sim())  # insert SIM again, because SIM removing is only recognized
        # by module if it is on
        test.expect(test.dut.dstl_shutdown_smso())
        test.sleep(2)

        test.log.step("21. Swtich on Module with MC")
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board(1000))
        test.expect(test.dut.at1.wait_for("SYSSTART"))
        test.expect(test.dut.dstl_remove_sim())  # 2nd step remove SIM while module is ON

        test.log.step("22. Check SIM status - removed from scripts, "
                      "because with removing SIM card by MC devboard, SIM card can be detected after module restarts")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "SIM not inserted"))
        if 'VIPER' is test.dut.project:
            test.sleep(5)

        test.log.step("23. Change module to sleep mode")
        test.expect(test.dut.at1.send_and_verify("at+cfun=0,0", expect="\s+\^SYSSTART AIRPLANE MODE\s+",
                                                 wait_for="\s+\^SYSSTART AIRPLANE MODE\s+"))

        test.log.step("24. Check CFUN settings")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 0\s+"))

        test.log.step("25. Insert SIM card")
        # can not call dstl because it automatically checks pin status and output error
        test.dut.devboard.send("MC:CCIN=0")
        test.sleep(1)

        test.log.step("26. Check SIM status")
        test.attempt(test.dut.at1.send_and_verify, "at+cpin?", "\s+SIM PIN\s+", retry=3, sleep=1)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 0\s+"))

        test.log.info("27. Set module back to normal mode")
        test.expect(test.dut.at1.send_and_verify("at+cfun=1,0", expect="\s+\^SYSSTART\s+",
                                                 wait_for="\s+\^SYSSTART\s+", timeout=25))

        test.log.step("28. SIM authentication should be lost,CFUN:1")
        test.attempt(test.dut.at1.send_and_verify, "at+cpin?", expect="\s+SIM PIN\s+", sleep=1.5, retry=5)
        test.expect(test.dut.at1.send_and_verify("at+creg?", "\s+\+CREG: \d,[04]\s+"))

        test.log.step("29. Check CFUN settings")
        test.expect(test.dut.at1.send_and_verify("at+cfun=?", cfun_test_resp))
        test.expect(test.dut.at1.send_and_verify("at+cfun?", "\s+\+CFUN: 1\s+"))

        test.log.step("30. Check pin status CFUN:1")
        test.expect(test.dut.at1.send_and_verify("at+cpin?", "\s+SIM PIN\s+"))
        pass

    def cleanup(test):
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.at1.send_and_verify("at+cfun=1", "OK"))
        test.sleep(1)
        pass


if "__main__" == __name__:
    unicorn.main()
