# responsible sebastian.lupkowski@globallogic.com
# location: Wroclaw
# TC0084429.001
import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_gsm


class Test(BaseTest):
    """
    TC0084429.001    Show local IP address

    check, wether the local IP address is displayed correctly

    1. define all possible PDP contexts
    2. display the addresses of all defined contexts
    3. activate PDP context number 1
    4. display the list of addresses for all PDP contexts
    5. display the address of the active PDP context
    6. display the address of all other defined PDP contexts one by another
    7. deactivate PDP context number 1
    8. repeat step 3 to 7 for all defined PDP contexts
    9. display the addresses of all defined contexts
    """


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(30)  # waiting for module to get ready

    def run(test):
        test.log.info('Creating backup of the contexts')
        test.contexts = save_contexts(test)

        test.log.info('Getting max number of PDP contexts')
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", ".*OK.*"))
        max_pdp = int(re.search(r'(CGDCONT: \(\d-)(\d{1,2})', test.dut.at1.last_response).group(2))

        test.log.info('Deregistering module from network')
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))

        test.log.step('1. define all possible PDP contexts')
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","{}"'.format(test.dut.sim.apn_v4), '.*OK.*'))
        for cid in range(2, max_pdp+1):
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}{0}"'.format(cid, test.dut.sim.apn_v4),
                                                     '.*OK.*'))

        test.log.step('2. display the addresses of all defined contexts')
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '.*OK.*'))
        for cid in range(1, max_pdp+1):
            test.expect(re.search(r'(\+CGPADDR: {}\W)'.format(cid), test.dut.at1.last_response))

        for cid in range(1, max_pdp+1):
            if cid > 1:
                test.log.info('Setting valid APN for next step')
                test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}{0}"'
                                                         .format(cid-1, test.dut.sim.apn_v4), '.*OK.*'))
                test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={0},"IP","{1}"'
                                                         .format(cid, test.dut.sim.apn_v4), '.*OK.*'))
            else:
                test.expect(dstl_register_to_gsm(test.dut))

            test.log.step('3. activate PDP context number {}'.format(cid))
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=1,{}'.format(cid), '.*OK.*'))

            test.log.step('4. display the list of addresses for all PDP contexts')
            test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '.*OK.*'))
            for context in range(1, max_pdp+1):
                if context is not cid:
                    test.expect(re.search(r'(\+CGPADDR: {}\W)'.format(context), test.dut.at1.last_response))
                else:
                    test.expect(re.search(r'(\+CGPADDR: ' + str(context) + r',\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")',
                                          test.dut.at1.last_response))

            test.log.step('5. display the address of the active PDP context')
            test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(cid), '.*OK.*'))
            test.expect(re.search(r"(\+CGPADDR: " + str(cid) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                                  test.dut.at1.last_response))

            test.log.step('6. display the address of all other defined PDP contexts one by another')
            for context in range(1, max_pdp+1):
                if context is not cid:
                    test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(context), '.*OK.*'))
                    test.expect(re.search(r'(\+CGPADDR: {}\W)'.format(context), test.dut.at1.last_response))

            test.log.step('7. deactivate PDP context number {}'.format(cid))
            test.expect(test.dut.at1.send_and_verify('AT+CGACT=0,{}'.format(cid), '.*OK.*'))
            test.sleep(5)

            if cid < max_pdp:
                test.log.step('8. repeat step 3 to 7 for all defined PDP contexts')

        test.log.step('9. display the addresses of all defined contexts')
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR', '.*OK.*'))
        for cid in range(1, max_pdp+1):
            test.expect(re.search(r'(\+CGPADDR: {}\W)'.format(cid), test.dut.at1.last_response))

    def cleanup(test):
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
