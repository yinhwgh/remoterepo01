# responsible: baris.kildi@thalesgroup.com
# location: Berlin
# TC0102484.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """"
    Activate PDP Context with different PDP type, IPv6 and Ipv4, the activation and deactivation should be successful.
    """

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_enter_pin()
        test.dut.dstl_register_to_network()

    def run(test):

        available_PDP_Type = ["IP", "IPV6", "IPV4V6"]

        for pdp_type in available_PDP_Type:
            test.log.info("1. Configure PDP context 1-3 with different PDP types 'IP', 'IPV6' and 'IPV4V6' ")
            connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=pdp_type, ip_public=False)
            test.expect(connection_setup_dut.dstl_define_pdp_context())

            test.log.info("2. Activate PDP context")
            test.expect(connection_setup_dut.dstl_activate_pdp_context())

            test.log.info("3. Check if PDP context is active")
            test.expect(connection_setup_dut.dstl_get_pdp_address())

            #test.log.info("4. Deactivate PDP context")
            #test.expect(connection_setup_dut.dstl_deactivate_pdp_context())

            if pdp_type == "IP" or "IPV4V6":
                test.socket_data_transfer_ipv4()
            elif pdp_type == "IPV6":
                test.socket_data_transfer_ipv6()

    def socket_data_transfer_ipv4(test):

            test.log.info("6. Send 10 byte socket data with IPV4 PDP context.")
            res = test.dut.at1.send_and_verify("at^sica=1,1", ".*OK.*")
            if not res:
                test.log.error("Active internet service failed.")
                return
            test.dut.at1.send_and_verify("AT^SICS=1,\"dns1\",\"0.0.0.0\"", ".*OK.*")
            test.dut.at1.send_and_verify("at^siss=1,\"srvType\",\"Socket\"")
            test.dut.at1.send_and_verify("at^siss=1,\"conId\",1")
            test.dut.at1.send_and_verify("at^siss=1,\"address\",\"socktcp://78.47.86.194:7\"")

            test.dut.at1.send_and_verify("at^siso=1")
            res = test.dut.at1.wait_for(".*SISW.*", timeout=60.0)
            test.sleep(5)
            if not res:
                test.log.error("Open TCP profile service failed.")
                test.dut.at1.send_and_verify("at^sisc=1")
                return
            test.dut.at1.send_and_verify("at^sisw=1,10")
            test.expect(test.dut.at1.send_and_verify("1111111111", ".*SISR.*"))
            test.expect(test.dut.at1.send_and_verify("at^sisr=1,10", "1111111111"))
            test.expect(test.dut.at1.send_and_verify("at^sisc=1"))

    def socket_data_transfer_ipv6(test):

            test.log.info("6. Send 10 byte socket data with IPV6 PDP context.")
            test.expect(test.dut.at1.send_and_verify("at^sica=1,1", ".*OK.*"))
            if not res:
                test.log.error("Active internet service failed.")
                return
            test.dut.at1.send_and_verify("AT^SICS=1,\"ipv6dns1\",\"[]\"", ".*OK.*")
            test.dut.at1.send_and_verify("at^siss=1,\"srvType\",\"Socket\"")
            test.dut.at1.send_and_verify("at^siss=1,\"conId\",1")
            test.dut.at1.send_and_verify("at^siss=1,\"address\",\"socktcp://[2a01:04f8:0192:722e:2::/68]:7\"")
            test.dut.at1.send_and_verify("at^siso=1")
            res = test.dut.at1.wait_for(".*SISW.*", timeout=60.0)
            test.sleep(5)
            if not res:
                test.log.error("Open TCP profile service failed.")
                test.dut.at1.send_and_verify("at^sisc=1")
                return
            test.dut.at1.send_and_verify("at^sisw=1,10")
            test.expect(test.dut.at1.send_and_verify("1111111111", ".*SISR.*"))
            test.expect(test.dut.at1.send_and_verify("at^sisr=1,10", "1111111111"))
            test.expect(test.dut.at1.send_and_verify("at^sisc=1"))

    def cleanup(test):

        pass


if "__main__" == __name__:
    unicorn.main()
