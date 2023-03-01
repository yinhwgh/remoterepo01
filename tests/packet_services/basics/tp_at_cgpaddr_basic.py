#responsible: dariusz.drozdek@globallogic.com
#location: Wroclaw
#TC0091876.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """TC0091876.001    TpAtCgpaddrBasic

    1. Check command without and with PIN
    2. Check command for valid and invalid parameters
    3. Define some contexts with address and check if +CGPADDR shows the same address
    - Functional test is not done here
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", "OK"))
        test.expect(dstl_restart(test.dut))
        test.log.info('Creating backup of the contexts')
        test.contexts = save_contexts(test)
        test.log.info('Clearing contexts')
        clear_contexts(test)
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=1,\"IP\",\"{}\"".format(test.dut.sim.apn_v4), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=2,\"IP\",\"{}\"".format(test.dut.sim.apn_public_v4),
                                                 ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=3,\"IPV6\",\"{}\"".format(test.dut.sim.apn_v6), ".*OK.*"))

    def run(test):
        test.log.step("1. Check command without and with PIN")
        test.log.info("Test command without PIN")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?", r".*\+CPIN: SIM PIN.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=?", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR", r".*\+CME ERROR: SIM PIN required.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=1", r".*\+CME ERROR: SIM PIN required.*"))
        test.log.info("Test command with PIN")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF?", ".*0,0,0,0.*OK"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=?", r".*[+]CGPADDR: \(1(,2,|-)3\).*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR", r".*[+]CGPADDR: 1(,\"\d{1,3}.\d{1,3}.\d{1,3}."
                                                               r"\d{1,3}\"|).*"
                                                               r".*[+]CGPADDR: 2.*"
                                                               r".*[+]CGPADDR: 3.*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=1", r".*[+]CGPADDR: 1(,\"\d{1,3}.\d{1,3}.\d{1,3}."
                                                                 r"\d{1,3}\"|).*"))

        test.log.step("2. Check command for valid and invalid parameters")
        test.log.info("Check command for valid values")
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=", r".*[+]CGPADDR: 1(,\"\d{1,3}.\d{1,3}.\d{1,3}."
                                                                r"\d{1,3}\"|).*"
                                                                r".*[+]CGPADDR: 2.*"
                                                                r".*[+]CGPADDR: 3.*OK.*"))
        for cid in range(1, 17):
            test.expect(test.dut.at1.send_and_verify("AT+CGPADDR={}".format(cid), r".*OK.*"))
            if cid < 4:
                test.expect(re.search(".*[+]CGPADDR: {}.*".format(cid), test.dut.at1.last_response))
            else:
                test.expect(not re.search(".*[+]CGPADDR: {}.*".format(cid), test.dut.at1.last_response))
        for cid in range(1, 4):
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=1,{}".format(cid), r".*OK.*"))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify("AT+CGPADDR={}".format(cid), r".*OK.*"))
            if cid < 3:
                test.expect(re.search(r".*[+]CGPADDR: {},\"\d{}.\d{}.\d{}.\d{}\".*".format(
                    cid, "{1,3}", "{1,3}", "{1,3}", "{1,3}"), test.dut.at1.last_response))
            else:
                test.expect(re.search(r".*[+]CGPADDR: {},\"(\d{}\.){}\d{}\"".format(
                    cid, "{1,3}", "{15}", "{1,3}"), test.dut.at1.last_response))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=1,2,3", r".*OK.*"))
        test.expect(re.search(r".*[+]CGPADDR: 1,\"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\"\r\n"
                              r"[+]CGPADDR: 2,\"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\"\r\n"
                              r"[+]CGPADDR: 3,\"(\d{1,3}\.){15}\d{1,3}\"\r\n", test.dut.at1.last_response))

        test.log.info("Check command for invalid values")
        for invalid_value in ["0", "17", "1,a", "-3", "2a"]:
            test.expect(test.dut.at1.send_and_verify("AT+CGPADDR={}".format(invalid_value), r".*[+]CME ERROR: .*"))

        test.log.step("3. Define some contexts with address and check if +CGPADDR shows the same address"
                      "\n- Functional test is not done here")
        test.log.info("Serval does not support this functionality.")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=4,\"IP\",\"apn4\",\"192.168.1.1\"", r".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR=4", r".*[+]CGPADDR: 4.*"))

        for cid in range(1, 4):
            test.expect(test.dut.at1.send_and_verify("AT+CGACT=0,{}".format(cid), ".*(OK|ERROR).*"))

    def cleanup(test):
        test.log.info('Clearing contexts and restoring original contexts')
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
        clear_contexts(test)
        for line in test.contexts:
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={}".format(line), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def save_contexts(test):
    context_contents = []
    if test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*")):
        for line in test.dut.at1.last_response.splitlines():
            pdpcontext = re.search(r'(\+CGDCONT: )(\d{1,2},.*)', line)
            if pdpcontext is not None:
                context_contents.append(pdpcontext.group(2).strip())
    return context_contents


def clear_contexts(test):
    cids = []
    if test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*OK.*")):
        for line in test.dut.at1.last_response.splitlines():
            pdpcontext = re.search(r'(\+CGDCONT: )(\d{1,2})(,.*)', line)
            if pdpcontext is not None:
                cids.append(pdpcontext.group(2).strip())
        for cid in cids:
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={}'.format(cid), '.*OK.*'))


if "__main__" == __name__:
    unicorn.main()
