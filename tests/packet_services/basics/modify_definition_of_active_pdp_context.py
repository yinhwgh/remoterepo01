# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0093334.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """TC0093334.001    ModifyDefinitionOfActivePdpContext

    Prove that it is not allowed to change the definition of an already activated context

    1. Define two pdp contexts
    2. Active defined pdp
    3. Check that has been properly activated (at+cgpaddr)
    4. Change pdp_type for activated context
    5. Change APN for activated context
    6. Deactivate all contexts
    7. Change pdp_type for inactiv context
    8. Change APN for inactiv context
    """
    contexts = []

    def setup(test):
        test.prepare_module("PREPARING DUT")
        test.cops_timeout = 90

    def run(test):
        test.log.step("1. Define two pdp contexts")
        test.define_first_two_pdp_contexts(test.dut.sim.apn_v4, test.dut.sim.apn_public_v4)
        test.rat = test.check_rat()

        test.log.step("2. Active defined pdp")
        test.change_pdp_activation_state(1, "check if both pdp contexts are successfully activated")

        test.log.step("3. Check that has been properly activated (at+cgpaddr)")
        test.check_ip_address()

        test.log.step("4. Change pdp_type for activated context")
        pdptype = test.save_supported_pdp_types()
        pdptype.remove('"IP"')
        test.change_pdp_type(pdptype[1], pdptype[2])

        test.log.step("5. Change APN for activated context")
        test.change_apn(pdptype[1], pdptype[2], test.dut.sim.apn_public_v4, test.dut.sim.apn_v4)

        test.log.step("6. Deactivate all contexts")
        test.change_pdp_activation_state(0, "check if both pdp contexts are successfully deactivated")

        test.log.step("7. Change pdp_type for inactiv context")
        test.change_pdp_type(pdptype[2], pdptype[1])

        test.log.step("8. Change APN for inactiv context")
        test.change_apn(pdptype[2], pdptype[1], test.dut.sim.apn_v4, test.dut.sim.apn_public_v4)

    def cleanup(test):
        test.log.info("Clearing contexts and restoring original contexts")
        test.clear_contexts()
        for line in test.contexts:
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={}".format(line), ".*OK.*"))
        test.detach_and_attach_module_into_network()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))

    def prepare_module(test, text):
        test.log.step(text)
        dstl_detect(test.dut)
        test.expect(dstl_get_bootloader(test.dut))
        test.expect(dstl_get_imei(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        test.sleep(10)
        test.change_ps_state(0)
        test.log.info("Creating backup of the contexts")
        test.contexts = test.save_contexts()
        test.clear_contexts()
        test.change_ps_state(1)
        test.sleep(10)

    def check_rat(test):
        test.log.info("===== Checking Radio Access Technology =====")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*OK.*"))
        rat = re.findall(r"(\d)[\r\n]", test.dut.at1.last_response)
        if test.expect(len(rat) > 0) and int(rat[0]) > 6:
            return "Module attach to LTE / NB IoT / CatM"
        else:
            return "Module NOT attach to LTE / NB IoT / CatM"

    def detach_and_attach_module_into_network(test):
        test.expect(test.dut.at1.send_and_verify('AT+COPS=2', ".*OK.*", timeout=test.cops_timeout))
        test.expect(test.dut.at1.send_and_verify('AT+COPS=0', ".*OK.*", timeout=test.cops_timeout))
        test.sleep(10)

    def change_ps_state(test, state):
        test.expect(test.dut.at1.send_and_verify("AT+CGATT={}".format(state), ".*OK.*"))

    def change_pdp_activation_state(test, state, text):
        if test.rat == "Module attach to LTE / NB IoT / CatM" and state == 1:
            test.log.info("Module attach to LTE / NB IoT / CatM\n"
                          "Activation CID=1 NOT needed - only CID=2 will be activated")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT={},2'.format(state), ".*OK.*"))
        elif test.rat == "Module attach to LTE / NB IoT / CatM" and state == 0:
            test.log.info("Module attach to LTE / NB IoT / CatM\n"
                          "Deactivation CID=1 impossible - Detached module from PS network will be realized\n"
                          "All contexts will be deactivated")
            test.change_ps_state(0)
        else:
            test.log.info("Module NOT attach to LTE / NB IoT / CatM\n"
                          "Activation /deactivation both defined PDP contexts will be realized")
            test.expect(test.dut.at1.send_and_verify('AT+CGACT={},1'.format(state), ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify('AT+CGACT={},2'.format(state), ".*OK.*"))
        test.log.info(text)
        test.expect(test.dut.at1.send_and_verify('AT+CGACT?', ".*[+]CGACT: 1,{}.*[+]CGACT: 2,{}".format(state, state),
                                                 ".*OK.*"))

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

    def save_supported_pdp_types(test):
        pdp_types = []
        if test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", ".*OK.*")):
            for line in test.dut.at1.last_response.splitlines():
                type = re.search(r'(\+CGDCONT: \(.*\),)(\".*\")(.*)', line)
                if type is not None:
                    pdp_types.append(type.group(2).strip())
        return pdp_types

    def define_first_two_pdp_contexts(test, apn_cid1, apn_cid2):
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,\"IP\",\"{}\"'.format(apn_cid1), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,\"IP\",\"{}\"'.format(apn_cid2), ".*OK.*"))

    def change_pdp_type(test, pdp_type_cid1, pdp_type_cid2):
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,{}'.format(pdp_type_cid1), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,{}'.format(pdp_type_cid2), ".*OK.*"))

    def change_apn(test, pdp_type_cid1, pdp_type_cid2, apn_cid1, apn_cid2):
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,{},\"{}\"'.format(pdp_type_cid1, apn_cid1), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,{},\"{}\"'.format(pdp_type_cid2, apn_cid2), ".*OK.*"))

    def check_ip_address(test):
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR", r".*[+]CGPADDR: 1(,\"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\")"
                                                               r".*[+]CGPADDR: 2(,\"\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}\")"
                                                               r".*OK.*"))


if "__main__" == __name__:
    unicorn.main()
