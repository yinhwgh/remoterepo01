#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0091871.002

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode, \
    dstl_set_minimum_functionality_mode
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_gsm

class Test(BaseTest):
    """     TC0091871.002    TpAtCgactBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CGACT.

    1. Restart module and set PDP contexts.
    2. Check test command: should not work without pin authentication.
    3. Check read command: should not work without pin authentication.
    4. Check write command: should not work without pin authentication.
    5. Register to network.
    6. Check test command: AT+CGACT=?
    7. Check read command: AT+CGACT?
    8. Set valid parameters: (should return OK)
    9. Set some invalid parameters: (should be rejected).
    """

    def setup(test):
        global project, product
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        project = test.dut.project.upper()
        product = test.dut.product.upper()
        test.log.info('project is {}'.format(project))
        if project != ("COUGAR" or "DAHLIA"):
            dstl_set_minimum_functionality_mode(test.dut)
            test.sleep(1)
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*"))
            for x in range(16):
                test.dut.at1.send_and_verify("AT+CGDCONT={}".format(x + 1), ".*OK.*")


    def run(test):
        time_to_response = 20
        test.log.step("1. Restart module and set PDP contexts.")
        test.expect(dstl_restart(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        if project == "COUGAR" and test.dut.variant.upper() != 'J':
            test.expect(
                test.dut.at1.send_and_verify('AT+CGDCONT=3,\"IPV4V6\",\"{}\"'.format(test.dut.sim.apn_v4), ".*OK.*"))
            test.expect(
                test.dut.at1.send_and_verify("AT+CGDCONT?", ".*3,\"IPV4V6\",\"{}\".*".format(test.dut.sim.apn_v4)))
        else:
            test.set_pdp_contexts()
        test.log.step("2. Check test command: should not work without pin authentication.")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", ".*CPIN: SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=?", ".*CME ERROR: SIM PIN required.*"))
        test.log.step("3. Check read command: should not work without pin authentication.")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CME ERROR: SIM PIN required.*"))
        test.log.step("4. Check write command: should not work without pin authentication.")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=1", ".*CME ERROR: SIM PIN required.*"))
        test.log.step("5. Register to network.")
        if project == "COUGAR" or product == "TX62" or project == "SERVAL":
            test.expect(dstl_register_to_network(test.dut))
        else:
            test.expect(dstl_register_to_gsm(test.dut))
        test.log.step("6. Check test command: AT+CGACT=?")
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=?", ".*CGACT: \(0,1\).*"))
        test.log.step("7. Check read command: AT+CGACT?")
        test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*")
        cgdcont_cid = (re.findall(' \d+', test.dut.at1.last_response))
        test.dut.at1.send_and_verify("AT+CGACT?", ".*OK.*")
        cgact_cid = (re.findall(' \d+', test.dut.at1.last_response))
        test.expect(cgact_cid == cgdcont_cid, msg="Number of cid is incorrect")
        test.expect('1,0' or '1,1' in test.dut.at1.last_response)
        test.expect('2,0' or '2,1' in test.dut.at1.last_response)
        test.expect('3,0' or '3,1' in test.dut.at1.last_response)
        test.log.step("8. Set valid parameters: (should return OK)")
        test.log.info("Timeout 10s for full network registration")
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=1", r".*OK.*|.*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 1,1.*CGACT: 2,1.*OK.*"))
        if project == "COUGAR":
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,2", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,4", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,3", ".*OK.*", timeout=time_to_response))
        elif project == "SERVAL":
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,2", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 2,0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,2", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 2,1.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 3,0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 3,1.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0", ".*OK.*", timeout=time_to_response))
        elif product != "TX62":
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0", ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,1", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 1,0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,1", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 1,1.*OK.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,2", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 2,0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,2", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 2,1.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 3,0.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*CGACT: 3,1.*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,1,2,3", ".*OK.*", timeout=time_to_response))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0", ".*OK|ERROR.*", timeout=time_to_response))
        test.log.step("9. Set some invalid parameters: (should be rejected).")
        if project == "COUGAR":
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,9", ".*ERROR.*"))
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,2,3,4", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,17", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=2,1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=-1", ".*ERROR.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGACT=2,2,3,4", ".*ERROR.*"))

    def cleanup(test):
        test.expect(dstl_register_to_network(test.dut))
        test.dut.at1.send_and_verify("AT&F", ".*OK.*")
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def set_pdp_contexts(test):
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"{}\"'.format(test.dut.sim.apn_v4), ".*OK.*"))
        test.expect(
            test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"{}\"'.format(test.dut.sim.apn_public_v4), ".*OK.*"))

        apn2 = test.dut.sim.apn_v6
        if apn2 is not None:
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,\"IPV6\",\"{}\"'.format(apn2), ".*OK.*"))
        else:
            apn2 = test.dut.sim.apn_v4_2nd
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=3,\"IP\",\"{}\"'.format(apn2), ".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
