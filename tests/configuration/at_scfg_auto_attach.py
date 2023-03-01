#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0088252.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.security import lock_unlock_sim
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.configuration import network_registration_status
from dstl.configuration import set_autoattach
from dstl.auxiliary.devboard import devboard
from dstl.network_service import network_monitor
from dstl.network_service import network_access_type


class TpAtScfgAutoAttach(BaseTest):
    """
    TC0088252.001 -  TpAtScfgAutoAttach
    Subscribers: 1 dut, 1 remote, 1 MCTest
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_turn_off_dev_board_urcs())

    def run(test):
        ps_domain = "ps+eps"
        for i in range(1, 3):
            if i == 1:
                test.log.step("{}.Test GAA with pin locked".format(i))
                test.expect(test.dut.dstl_lock_sim())
                test.expect(test.dut.dstl_restart())
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
                sim_state = "locked"
            else:
                test.log.step("{}.Test GAA with pin unlocked".format(i))
                test.expect(test.dut.dstl_unlock_sim())
                test.expect(test.dut.dstl_restart())
                test.sleep(2)
                test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))
                sim_state = "unlocked"
            test.log.step("{}.1 Check commands without pin input, valid and invalid parameters".format(i))
            error_21_or_53 = "ERROR: (21|53)"
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", "OK"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=?",
                                                     "SCFG:\s\"GPRS/AutoAttach\",\(?\"disabled\",\"enabled\"\)?.*OK.*"))
            test.expect(
                test.dut.at1.send_and_verify("AT^SCFG?", "SCFG:\s\"GPRS/AutoAttach\",\"(disabled|enabled)\".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\",\"ON\"", error_21_or_53))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\",\"enabled\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\",\"OFF\"", error_21_or_53))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\",\"disabled\"", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"GPRS/AutoAttach\"", ".*OK.*"))

            test.log.step("{}.2 GAA enabled with pin {}".format(i, sim_state))
            test.expect(test.dut.dstl_enable_ps_autoattach())
            test.restart_and_enable_network_state_urc(sim_state)

            test.log.info("After retarting module is automatically attached to network.")
            checked_urc = test.dut.dstl_check_network_registration_urc(domain="all", expected_state="1")
            if checked_urc:
                test.expect(checked_urc)
            else:
                test.log.info("Module may be already registerd to network before enabling URC. Read value and check.")
                test.expect(test.dut.dstl_read_network_registration_state(domain="all", expected_state="1"))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT: 1"))

            test.log.step("{}.2.1.GAA enabled with pin {}: manually deregister and re-register".format(i, sim_state))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=60))
            test.expect(test.dut.dstl_check_network_registration_urc(domain="all", expected_state="0"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", timeout=60))
            test.expect(test.dut.dstl_check_network_registration_urc(domain="all", expected_state="1"))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT: 1"))
            test.log.step("{}.2.2 GAA enabled with pin {}: manually detach and attach".format(i, sim_state))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", "OK", timeout=60))
            test.expect(test.dut.dstl_check_network_registration_urc(domain=ps_domain, expected_state="0"))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", "OK", timeout=60))
            test.expect(test.dut.dstl_check_network_registration_urc(domain=ps_domain, expected_state="1"))

            # For some products even without antenna, module is still able to register to network
            test.log.step("{}.3 Check GAA after switching antenna".format(i))
            test.log.step("{}.3.1 GAA enabled, switch Off antenna, URC appears".format(i))
            test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "OFF1"))
            if not test.dut.dstl_check_network_registration_urc(domain="all", expected_state="[02]", timeout=20):
                test.expect(False, msg="No impact to network when switching off antenna, please test manually.")
            else:
                test.expect(test.dut.dstl_check_ps_autoattach_enabled())
                test.log.step("{}.3.2 GAA enabled, switch ON antenna, URC appears".format(i))
                test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "ON1"))
                test.expect(test.dut.dstl_check_network_registration_urc(domain="all", expected_state="1", timeout=70))
                test.expect(test.dut.dstl_check_ps_autoattach_enabled())
                test.log.step("{}.3.3 GAA disabled, switch Off antenna, CS URC appears, PS/EPS is offline".format(i))
                test.expect(test.dut.dstl_disable_ps_autoattach())
                test.restart_and_enable_network_state_urc(sim_state)
                test.expect(test.dut.dstl_check_network_registration_urc(domain="cs", expected_state="1"))
                test.expect(test.dut.dstl_read_network_registration_state(ps_domain, "0"))
                test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "OFF1"))
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT: 0"))
                test.log.step("{}.3.4 GAA disabled, switch ON antenna, CS URC appears, PS/EPS is offline".format(i))
                test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "ON1"))
                test.expect(test.dut.dstl_check_network_registration_urc(domain="cs", expected_state="1"))
                test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT: 0"))
                test.log.step("{}.3.5 Manually attach to PS/EPS domain can succeed after switching antenna".format(i))
                test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", "OK", timeout=30))
                test.expect(test.dut.dstl_read_network_registration_state(ps_domain, "1"))

            test.log.step("{}.4 Check GAA disabled with pin {}".format(i, sim_state))
            test.expect(test.dut.dstl_disable_ps_autoattach())
            test.restart_and_enable_network_state_urc(sim_state)
            if not test.dut.dstl_check_network_registration_urc("cs", "1"):
                test.expect(test.dut.dstl_read_network_registration_state("cs", "1"))
            test.expect(test.dut.dstl_read_network_registration_state(ps_domain, "0"))
            test.log.step("{}.4.1 Check GAA disabled with pin {}: manually attach to PS/EPS domain".format(i, sim_state))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", "OK", timeout=60))
            test.expect(test.dut.dstl_read_network_registration_state(ps_domain, "1"))
            test.sleep(5)
            test.expect(test.dut.dstl_read_network_registration_state("cs", "1"))
            test.log.step("{}.4.2 Check GAA disabled with pin {}: manually deregister and re-register".format(i, sim_state))
            test.expect(test.dut.dstl_set_network_registration_urc(ps_domain, urc_mode="2"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=60))
            test.expect(test.dut.dstl_check_network_registration_urc(domain="all", expected_state="0"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "READY"))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0", "OK", timeout=60))
            # test.expect(test.dut.dstl_register_to_lte())
            test.expect(test.dut.at1.send_and_verify("AT+CGATT?", "\+CGATT: 0"))
            test.log.step("{}.4.3 Check GAA disabled with pin {}: manually attach to PS/EPS domain".format(i, sim_state))
            test.expect(test.dut.at1.send_and_verify("AT+CGATT=1", "OK", timeout=60))
            test.expect(test.dut.dstl_read_network_registration_state("all", "1"))

    def cleanup(test):
        test.expect(test.dut.dstl_switch_antenna_mode_via_dev_board(1, "ON1"))
        test.expect(test.dut.at1.send_and_verify("AT&F"))
        test.expect(test.dut.at1.send_and_verify("AT&W"))
        test.expect(test.dut.dstl_lock_sim())
    
    def restart_and_enable_network_state_urc(test, sim_state):
        test.expect(test.dut.dstl_restart())
        test.sleep(2)
        if sim_state == "locked":
            test.expect(test.dut.dstl_set_network_registration_urc("cs", "2"))
            test.expect(test.dut.dstl_enter_pin())
            test.expect(test.dut.dstl_set_network_registration_urc("ps+eps", "2"))
        else:
            test.expect(test.dut.dstl_set_network_registration_urc("all", urc_mode="2"))



if __name__ == "__main__":
    unicorn.main()
