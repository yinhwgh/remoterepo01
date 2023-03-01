# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0091788.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.supplementary_services import lock_unlock_facility
from dstl.usim import get_imsi
from dstl.configuration.set_error_message_format import dstl_set_error_message_format


class Test(BaseTest):
    """ TC0091788.001 - TpAtCpinBasic  """

    def setup(test):
        test.cfg_imsi = test.dut.sim.imsi
        test.simpuk = test.dut.sim.puk1
        test.simpin = test.dut.sim.pin1
        test.simpin2 = test.dut.sim.pin2
        test.simpuk2 = test.dut.sim.puk2

        if test.simpin is "" or test.simpuk is "" or test.cfg_imsi is "" or test.simpin2 is "" or test.simpuk2 is "":
            test.expect(False, critical=True, msg="important values from configuration file is missing - abort")

        test.dut.dstl_detect()

        device_sim = None   # none means by default: SIM1
        test.dut.dstl_lock_unlock_facility(device_sim=device_sim, facility="SC", lock=True)
        # test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(test.simpin), "OK"))
        sim_imsi = test.dut.dstl_get_imsi()

        if sim_imsi != test.cfg_imsi:
            test.expect(False, critical=True, msg="SIM card and configuration file do not match! - abort")

        test.dut.dstl_restart()
        test.sleep(5)
        test.dut.dstl_set_error_message_format('1')
        pass

    def run(test):
        test.log.info("1.test without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"777777\"", ".*ERROR.*"))

        test.log.info("2.test at+cpin=<pin>,<new pin>")
        if test.simpuk:
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"6789\"", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*SIM PUK.*"))
            test.expect(test.dut.at1.send_and_verify(f"AT+CPIN=\"{test.simpuk}\",\"{test.simpin}\"", ".*OK.*"))

        test.log.info("3.test with PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=?", "OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*READY.*OK.*"))

        test.log.info("4.enter correct PIN again")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(test.simpin), ".*CME ERROR: (16|18).*"))
        # CME16:  	incorrect password (here it is the wrong pwd for PIN2)
        # CME18:  	PUK2 required (here it is the wrong pwd for PIN2)
        last_resp = test.dut.at1.last_response
        ret = False
        if "CME ERROR: 16" in last_resp or "incorrect password" in last_resp:
            ret = test.expect(
                test.dut.at1.send_and_verify("AT+CPIN=\"{}\"".format(test.simpin2), ".*OK.*"))
        elif "CME ERROR: 18" in last_resp or "PUK2" in last_resp:
            ret = test.expect(
                test.dut.at1.send_and_verify("AT+CPIN=\"{}\",\"{}\"".format(test.simpuk2, test.simpin2), ".*OK.*"))
        else:
            test.expect(False, critical=True, msg="SIM PIN2/PUK2 is wrong! - abort")

        if ret is not True:
            test.expect(False, critical=True, msg="SIM card and configuration file do not match! - abort")
        pass

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
