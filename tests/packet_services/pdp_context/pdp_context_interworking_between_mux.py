#responsible: grzegorz.brzyk@globallogic.com
#location: Wroclaw
#TC0103920.001

import unicorn
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """
    TC0103920.001 - PdpContextInterworkingBetweenMux    #test procedure version: 1.8.0

    INTENTION
    To check different use case of PDP Context activation and deactivation using MUX.

    PRECONDITION
    Equipment:
    a) DUT x1 attached to the network
    b) SIM Card supported APNs for IPv4.
    c) SIM Card supported APNs for IPv6 (if supported by module)
    Configuration:
    MUX installed on all supported DUT ports according to AT Spec (modem, asc0 etc.).

    Remember!
    Set up virtual ports on DUT (Virtual Port 1, Virtual Port 2, etc.).
    ...
    """

    def setup(test):
        test.log.step("0. Prepare module")
        test.time_value = 10
        dstl_detect(test.dut)
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_register_to_network(test.dut))
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+CIMI", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT^SMONI", ".*OK.*", timeout=test.time_value))
        test.expect(test.dut.at1.send_and_verify("AT\Q3", ".*OK.*", timeout=test.time_value))
        test.dut.at1.close()

    def run(test):
        project = test.dut.project.upper()
        if project == "BOBCAT":
            test.log.h2('Start check with IPV4 PDP context')
            adr_pdp_mux_table = ["adr_pdp_mux1", "adr_pdp_mux2", "adr_pdp_mux3"]
            tc_mux_init(test, used_mux=3)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IP", pdp_apn=test.dut.sim.apn_v4, used_mux=3)
            test.log.h2('Start check with IPV6 PDP context')
            tc_mux_init(test, used_mux=3)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IPV6", pdp_apn=test.dut.sim.apn_v6, used_mux=3)
        elif project == "SERVAL":
            test.log.h2('Start check with IPV4 PDP context')
            adr_pdp_mux_table = ["adr_pdp_mux1", "adr_pdp_mux2"]
            tc_mux_init(test, used_mux=2)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IP", pdp_apn=test.dut.sim.apn_v4, used_mux=2)
            test.log.h2('Start check with IPV6 PDP context')
            tc_mux_init(test, used_mux=2)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IPV6", pdp_apn=test.dut.sim.apn_v6, used_mux=2)
        elif project == "VIPER":
            test.log.h2('Start check with IPV4 PDP context')
            adr_pdp_mux_table = ["adr_pdp_mux1", "adr_pdp_mux2", "adr_pdp_mux3"]
            tc_mux_init(test, used_mux=3)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IP", pdp_apn=test.dut.sim.apn_v4_2nd,
                     used_mux=3)
            test.log.h2('Start check with IPV6 PDP context')
            tc_mux_init(test, used_mux=3)
            tc_steps(test, adr_pdp_mux_table, pdp_type="IPV6", pdp_apn=test.dut.sim.apn_v6,
                     used_mux=3)
        else:
            test.expect(False, critical=True, msg="Test procedure need be implemented for product.")

    def cleanup(test):
        test.dut.mux_1.close()
        test.dut.mux_2.close()
        test.dut.mux_3.close()

def tc_mux_init(test, used_mux):
    test.log.step("Step 1. Set up 1st virtual port on DUT (Virtual Port 1)")
    test.expect(test.dut.mux_1.send_and_verify("AT", ".*OK.*", timeout=test.time_value))

    test.log.step("Step 2. Set up 2nd virtual port on DUT (Virtual Port 2)")
    test.expect(test.dut.mux_2.send_and_verify("AT", ".*OK.*", timeout=test.time_value))

    test.log.step("Step 3. Set up 3rd virtual port on DUT (Virtual Port 3)")
    if used_mux == 3:
        test.expect(test.dut.mux_3.send_and_verify("AT", ".*OK.*", timeout=test.time_value))
    else:
        test.log.info('Interface reserved from normal use on module')

def tc_steps(test, adr_pdp_mux_table, pdp_type, pdp_apn, used_mux):
    test.log.step("Step 4. On Virtual Port 1 define PDP context with {} type APN".format(pdp_type))
    test.mux1_connection = dstl_get_connection_setup_object(test.dut, device_interface="mux_1")
    test.mux1_connection.cgdcont_parameters['cid'] = '1'
    test.mux1_connection.cgdcont_parameters['pdp_type'] = pdp_type
    test.mux1_connection.cgdcont_parameters['apn'] = pdp_apn
    test.expect(test.mux1_connection.dstl_define_pdp_context())
    test.dut.mux_1.send_and_verify('at+cops=0','OK')
    test.expect(test.mux1_connection.dstl_attach_to_packet_domain())

    test.log.step("Step 5. Check if PDP context (at-cgdcont?) is define on Virtual Port 1")
    check_pdp_context_define(test, pdp_type, pdp_apn, device=test.dut.mux_1, interface=test.mux1_connection)

    test.log.step("Step 6. Check if PDP context (at-cgdcont?) is define on Virtual Port 2")
    test.mux2_connection = dstl_get_connection_setup_object(test.dut, device_interface="mux_2")
    check_pdp_context_define(test, pdp_type, pdp_apn, device=test.dut.mux_2, interface=test.mux2_connection)

    test.log.step("Step 7. Check if PDP context (at-cgdcont?) is define on Virtual Port 3")
    if used_mux == 3:
        test.mux3_connection = dstl_get_connection_setup_object(test.dut, device_interface="mux_3")
        check_pdp_context_define(test, pdp_type, pdp_apn, device=test.dut.mux_3, interface=test.mux3_connection)
    else:
        test.log.info('Interface reserved from normal use on module')

    test.log.step("Step 8. Activate 1st PDP context (at-cgact=1,1) on Virtual Port 1")
    test.expect(test.mux1_connection.dstl_activate_pdp_context())
    test.active_pdp = test.dut.mux_1.last_response

    test.log.step("Step 9. Check PDP context status (at-cgact?) on Virtual Port 1.")
    check_pdp_context_status(test, device=test.dut.mux_1, interface=test.mux1_connection)

    test.log.step("Step 10. Check PDP context status (at-cgact?) on Virtual Port 2.")
    check_pdp_context_status(test, device=test.dut.mux_2, interface=test.mux2_connection)

    test.log.step("Step 11. Check PDP context status (at-cgact?) on Virtual Port 3.")
    if used_mux == 3:
        check_pdp_context_status(test, device=test.dut.mux_3, interface=test.mux3_connection)
    else:
        test.log.info('Interface reserved from normal use on module')

    test.log.step("Step 12. Check IP Address (at-cgpaddr) on Virtual Port 1")
    check_ip_address(test, device=test.dut.mux_1, interface=test.mux1_connection, interface_nr=adr_pdp_mux_table[0])

    test.log.step("Step 13. Check IP Address (at-cgpaddr) on Virtual Port 2")
    check_ip_address(test, device=test.dut.mux_2, interface=test.mux2_connection, interface_nr=adr_pdp_mux_table[1])

    test.log.step("Step 14. Check IP Address (at-cgpaddr) on Virtual Port 3")
    if used_mux == 3:
        check_ip_address(test, device=test.dut.mux_3, interface=test.mux3_connection, interface_nr=adr_pdp_mux_table[2])
    else:
        test.log.info('Interface reserved from normal use on module')

    test.log.step("Step 15. Disconnect Virtual Port 1 on Virtual Port 1.")
    test.expect(test.mux1_connection.dstl_detach_from_packet_domain())
    test.dut.mux_1.close()
    test.log.step("Step 16. Disconnect Virtual Port 2 on Virtual Port 2.")
    test.expect(test.dut.mux_2.send_and_verify("AT+CGATT?", r".*\+CGATT: 0.*", timeout=test.time_value))
    test.dut.mux_2.close()
    test.log.step("Step 17. Disconnect Virtual Port 3 on Virtual Port 3.")
    if used_mux == 3:
        test.expect(test.dut.mux_3.send_and_verify("AT+CGATT?", r".*\+CGATT: 0.*", timeout=test.time_value))
        test.dut.mux_3.close()
    else:
        test.log.info('Interface reserved from normal use on module')


def check_pdp_context_define(test, pdp_type, pdp_apn, device, interface):
    test.expect(device.send_and_verify("AT+CGDCONT?", ".*OK.*", timeout=test.time_value))
    regex = r".*CGDCONT: 1,\"({})\",\"({})\"".format(pdp_type, pdp_apn)
    if test.expect(re.search(regex, device.last_response)):
        test.log.info('Assert successful: CGDCONT - correct status')
    else:
        test.log.info('Assert failed: CGDCONT - incorrect status. Trying to define PDP context')
        test.expect(interface.dstl_define_pdp_context())

def check_pdp_context_status(test, device, interface):
    test.expect(device.send_and_verify("AT+CGACT?", ".*OK.*", timeout=test.time_value))
    act_pdp_mux = device.last_response
    if test.expect(act_pdp_mux == test.active_pdp):
        test.log.info('Assert successful: CGACT - correct status')
    else:
        test.log.info('Assert failed: CGACT - incorrect status. Trying to activate PDP context')
        test.expect(test.expect(interface.dstl_activate_pdp_context()))

def check_ip_address(test, device, interface, interface_nr):
    test.expect(interface.dstl_get_pdp_address())
    value_range = "([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
    regex1 = r"\+CGPADDR: 1,\"({0}\.){{3}}{0}\"".format(value_range)
    regex2 = r"\+CGPADDR: 1,\"({0}\.){{15}}{0}\"".format(value_range)
    if test.expect(re.search(regex1, device.last_response) or re.search(regex2, device.last_response)):
        if device == test.dut.mux_1:
            test.adr_pdp_mux1 = device.last_response
            test.log.info('Assert successful: CGPADDR - correct status')
        else:
            interface_nr = device.last_response
            test.expect(interface_nr == test.adr_pdp_mux1)
            test.log.info('Assert successful: CGPADDR - correct status')
    else:
        test.log.error('Assert failed: Cannot read response form CGPADDR')


if  "__main__" == __name__:
    unicorn.main()