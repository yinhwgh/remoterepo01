#responsible: renata.bryla@globallogic.com
#location: Wroclaw
#TC0095672.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_register_to_gsm
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """
    TC0095672.001 - PdpContextBasic

    INTENTION
    To check PDP Context activation and deactivation.
    Functional tests are not done here.
    ...
    """

    def setup(test):
        test.log.info("===== Prepare module =====")
        test.time_value = 10
        dstl_detect(test.dut)
        test.expect(dstl_register_to_network(test.dut))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=test.time_value))

    def run(test):
        test.log.info("===== Start check with IPV4 PDP context - CID=1 =====")
        test.execute_steps_1_and_2()
        test.execute_steps_3_to_6('1', "IP")
        if test.deact_method == "module attach to LTE / NB IoT / CatM":
            test.log.info("===== In first checking for CID=1 module was attach to LTE / NB IoT / CatM networks =====\n"
                          "===== Steps for checking activation / deactivation CID=1 will be realized once again "
                          "in RAT 2G =====")
            test.expect(dstl_register_to_gsm(test.dut))
            test.log.info("Timeout 10s for full network registration to 2G")
            test.sleep(10)
            test.log.info("===== Start check with IPV4 PDP context - CID=1 - second loop =====")
            test.execute_steps_3_to_6('1', "IP")
            test.expect(dstl_register_to_network(test.dut))
        test.log.step("Step 7. Repeat steps 3-6 for IPv6 context (if supported on DUT)")
        test.log.info("===== Start check with IPV6 PDP context - CID=2 =====")
        test.execute_steps_3_to_6('2', "IPV6")

    def cleanup(test):
        test.expect(test.dut_connection.dstl_detach_from_packet_domain())
        for iteration in range(1, 3):
            test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={}'.format(iteration), '.*OK.*', timeout=test.time_value))
        test.define_pdp_context('1', "IP", test.dut.sim.apn_v4)
        test.expect(test.dut_connection.dstl_attach_to_packet_domain())
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0", ".*OK.*", timeout=test.time_value * 6))
        test.log.info("Timeout 10s for full network registration")
        test.sleep(10)

    def execute_steps_1_and_2(test):
        test.dut_connection = dstl_get_connection_setup_object(test.dut, device_interface="at1")

        test.log.step("Step 1. Set on DUT context with IPv4 APN using at+cgdcont command")
        test.define_pdp_context('1', "IP", test.dut.sim.apn_v4)

        test.log.step("Step 2. Set on DUT context with IPv6 APN using at+cgdcont command")
        test.define_pdp_context('2', "IPV6", test.dut.sim.apn_v6)

        test.expect(test.dut_connection.dstl_attach_to_packet_domain())
        test.log.info("===== Check PDP context settings for CID 1 and CID 2 =====")
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?',
                    r'.*\+CGDCONT: 1,"IP","{}".*\+CGDCONT: 2,"IPV6","{}".*OK.*'.format
                    (test.dut.sim.apn_v4, test.dut.sim.apn_v6), timeout=test.time_value))

    def execute_steps_3_to_6(test, cid, pdp_type):
        test.log.step("Step 3. Activate 1st PDP context (at+cgact=1,1)")
        test.dut_connection.cgdcont_parameters['cid'] = cid
        test.expect(test.dut_connection.dstl_activate_pdp_context())

        test.log.step("Step 4. Check IP Address on DUT (at+cgpaddr) and context status (at+cgact?)")
        test.check_ip_address(cid, pdp_type, 1)
        test.check_pdp_context_status(cid, 1)

        test.log.step("Step 5. Deactivate 1st context on DUT (at+cgact=0,1)")
        test.deact_method = test.check_rat()
        if cid == '1' and test.deact_method == "module attach to LTE / NB IoT / CatM":
            test.log.info("===== For LTE, NB IoT, CatM networks first context cannot be deactivate =====\n"
                          "===== Detached module from PS network will be realized =====")
            test.expect(test.dut_connection.dstl_detach_from_packet_domain())
        else:
            test.log.info("===== Module NOT registered into LTE, NB IoT, CatM networks =====\n"
                          "===== Deactivate PDP context will be realized =====")
            test.expect(test.dut_connection.dstl_deactivate_pdp_context())

        test.log.step("Step 6. Check IP Address on DUT (at+cgpaddr) and context status (at+cgact?)")
        test.check_ip_address(cid, pdp_type, 0)
        test.check_pdp_context_status(cid, 0)

    def define_pdp_context(test, cid, pdp_type, pdp_apn):
        test.log.info("PDP context defined with {} type APN".format(pdp_type))
        test.dut_connection.cgdcont_parameters['cid'] = cid
        test.dut_connection.cgdcont_parameters['pdp_type'] = pdp_type
        test.dut_connection.cgdcont_parameters['apn'] = pdp_apn
        test.expect(test.dut_connection.dstl_define_pdp_context())

    def check_pdp_context_status(test, cid, exp_state):
        if test.expect(test.dut.at1.send_and_verify("AT+CGACT?", ".*\+CGACT: {},{}.*".format(cid, exp_state),
                                                    timeout=test.time_value)):
            test.log.info('Assert successful: CGACT - correct status')
        else:
            test.log.info('Assert failed: CGACT - incorrect status.')

    def check_ip_address(test, cid, pdp_type, exp_state):
        test.expect(test.dut.at1.send_and_verify("AT+CGPADDR={}".format(cid), r".*\+CGPADDR: {}.*[\r\n].*OK.*".
                                                 format(cid), timeout=test.time_value))
        if exp_state == 1:
            value_range = "([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
            regex_act_v4 = r"\+CGPADDR: 1,\"({0}\.){{3}}{0}\"".format(value_range)
            regex_act_v6 = r"\+CGPADDR: 2,\"({0}\.){{15}}{0}\"".format(value_range)
            if pdp_type == "IP":
                regex_act = regex_act_v4
            else:
                regex_act = regex_act_v6
            test.log.info('Expected phrase: {}'.format(regex_act))
            test.expect(re.search(regex_act, test.dut.at1.last_response))
            test.log.info('Assert successful: CGPADDR displayed as expected')
        else:
            regex_deact = r"\+CGPADDR: {}[\r\n]".format(cid)
            test.log.info('Expected phrase: {}'.format(regex_deact))
            test.expect(re.search(regex_deact, test.dut.at1.last_response))
            test.log.info('Assert successful: CGPADDR NOT displayed as expected')

    def check_rat(test):
        test.log.info("===== Checking Radio Access Technology =====")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*OK.*"))
        rat = re.findall(r"(\d)[\r\n]", test.dut.at1.last_response)
        if test.expect(len(rat) > 0) and int(rat[0]) > 6:
            return "module attach to LTE / NB IoT / CatM"
        else:
            return "module NOT attach to LTE / NB IoT / CatM"


if "__main__" == __name__:
    unicorn.main()
