#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0094809.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.attach_to_network import enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    """intention: Setting right/wrong DNS1 and DNS2 address and activate context based on IPv6.
    TcDnsServerAndPing_IPv6

    description:
    1. Enter PIN if not entered yet.
    2. Define PDP context.
    3. Define correct based on IPv6: dns1 and dns2 values (eg. Google DNS), restart module if necessary.
    4. Activate defined context.
    5. Ping chosen IPv6 site/ip address with 10 repetitions.
    6. Deactivate context.
    7. Define wrong IPv6 dns1, restart module if necessary.
    8. Activate defined context.
    9. Ping chosen IPv6 site/ip address with 10 repetitions.
    10. Deactivate context.
    11. Define wrong IPv6 dns1 and dns2, restart module if necessary.
    12. Activate defined context.
    13. Ping chosen IPv6 site/ip address with 10 repetitions.
    14. Deactivate context.
    15. Define wrong IPv6 dns2, restart module if necessary.
    16. Activate defined context.
    17. Ping chosen IPv6 site/ip address with 10 repetitions.
    18. Deactivate context.
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.restart_needed = test.dut.project == "SERVAL" or "VIPER"
        test.log.step("1. Enter PIN if not entered yet.")
        enter_pin(test.dut)

        test.log.step("2. Define PDP context.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version="ipv6")
        test.expect(connection_setup_object.dstl_load_internet_connection_profile())
        test.cid = connection_setup_object.dstl_get_used_cid()

        test.log.step("3. Define correct based on IPv6: dns1 and dns2 values (eg. Google DNS), restart module if "
                      "necessary.")
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns1,[2001:4860:4860::8888]".format(test.cid)))
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns2,[2001:4860:4860::8844]".format(test.cid)))

        if test.restart_needed:
            dstl_restart(test.dut)
            enter_pin(test.dut)

        test.log.step("4. Activate defined context.")
        connection_setup_object.dstl_attach_to_packet_domain()
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        test.log.step("5. Ping chosen IPv6 site/ip address with 10 repetitions.")
        test.server = EchoServer("IPv6", "TCP", True)
        request_amount = 10
        ping_address = test.server.dstl_get_server_FQDN()
        ping_execution = InternetServiceExecution(test.dut, test.cid)
        test.expect(ping_execution.dstl_execute_ping(ping_address, request=request_amount))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= request_amount * 0.2)

        test.log.step("6. Deactivate context.")
        connection_setup_object.dstl_detach_from_packet_domain()

        test.log.step("7. Define wrong IPv6 dns1, restart module if necessary")
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns1,[2001:4860:4860::0000]".format(test.cid)))
        if test.restart_needed:
            dstl_restart(test.dut)
            enter_pin(test.dut)

        test.log.step("8. Activate defined context.")
        connection_setup_object.dstl_attach_to_packet_domain()
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        test.log.step("9. Ping chosen IPv6 site/ip address with 10 repetitions.")
        test.expect(ping_execution.dstl_execute_ping(ping_address, request=request_amount))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= request_amount * 0.2)

        test.log.step("10. Deactivate context.")
        connection_setup_object.dstl_detach_from_packet_domain()

        test.log.step("11. Define wrong IPv6 dns1 and dns2, restart module if necessary.")
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns2,[2001:4860:4860::1111]".format(test.cid)))
        if test.restart_needed:
            dstl_restart(test.dut)
            enter_pin(test.dut)

        test.log.step("12. Activate defined context.")
        connection_setup_object.dstl_attach_to_packet_domain()
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        test.log.step("13. Ping chosen IPv6 site/ip address with 10 repetitions.")
        if test.dut.project == "SERVAL":
            test.expect(ping_execution.dstl_execute_ping(ping_address, request=request_amount, expected_response='ERROR'))
        else:
            test.expect(ping_execution.dstl_execute_ping(ping_address, request=request_amount))
            test.expect(len(ping_execution.dstl_get_time_statistic()) == 0)

        test.log.step("14. Deactivate context.")
        connection_setup_object.dstl_detach_from_packet_domain()

        test.log.step("15. Define wrong IPv6 dns2, restart module if necessary.")
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns1,[2001:4860:4860::8888]".format(test.cid)))
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns2,[2001:4860:4860::1111]".format(test.cid)))

        if test.restart_needed:
            dstl_restart(test.dut)
            enter_pin(test.dut)

        test.log.step("16. Activate defined context.")
        connection_setup_object.dstl_attach_to_packet_domain()
        test.expect(connection_setup_object.dstl_activate_internet_connection())

        test.log.step("17. Ping chosen IPv6 site/ip address with 10 repetitions.")
        test.expect(ping_execution.dstl_execute_ping(ping_address, request=request_amount))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= request_amount * 0.2)

        test.log.step("18. Deactivate context.")
        connection_setup_object.dstl_detach_from_packet_domain()


    def cleanup(test):
        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")
        test.log.step("removing defined dns")
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns1,[]".format(test.cid)))
        test.expect(test.dut.at1.send_and_verify("at^sics={},ipv6dns2,[]".format(test.cid)))
        if test.restart_needed:
            dstl_restart(test.dut)


if "__main__" == __name__:
    unicorn.main()
