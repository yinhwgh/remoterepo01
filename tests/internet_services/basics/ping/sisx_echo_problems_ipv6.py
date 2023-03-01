# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105513.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.auxiliary.restart_module import dstl_restart
from dstl.packet_domain.select_printing_ip_address_format import \
    dstl_select_printing_ip_address_format


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.info("TC0105513.001 - SISX_EchoProblems_IPv6")

        test.log.step("1) Power on DUT (do not enter PIN)")
        dstl_restart(test.dut)

        test.log.step("2) Try to send PING request using AT ^ SISX command to available IPv6 "
                      "server: \n"
                      "- using IPv6 address (e.g. AT^SISX=\"PING\", 1, "
                      "\"2001:41d0:601:1100:0:0:0:72\", 3 )\n"
                      "- using domain name (FQDN)(e.g. AT^SISX=\"PING\", 1, "
                      "\"www.m2mtestserver2.testwro001.ovh\", 3 )")
        connection_setup_object_ipv4 = dstl_get_connection_setup_object(test.dut, ip_version="IPV4")
        connection_setup_object_ipv4.cgdcont_parameters['cid'] = '1'
        con_id_ipv4 = connection_setup_object_ipv4.dstl_get_used_cid()
        test.expect(connection_setup_object_ipv4.dstl_load_internet_connection_profile())

        connection_setup_object_ipv6 = dstl_get_connection_setup_object(test.dut, ip_version="IPV6",
                                                                        ip_public=True)
        connection_setup_object_ipv6.cgdcont_parameters['cid'] = '2'
        con_id_ipv6 = connection_setup_object_ipv6.dstl_get_used_cid()

        ping_execution_ipv4 = InternetServiceExecution(test.dut, con_id_ipv4)
        ping_execution_ipv6 = InternetServiceExecution(test.dut, con_id_ipv6)

        test.ip_server = EchoServer("IPv6", "TCP", extended=True)
        server_fqdn_address = test.ip_server.dstl_get_server_FQDN()
        server_ip_address = test.ip_server.dstl_get_server_ip_address()

        test.expect(ping_execution_ipv6.dstl_execute_ping(server_ip_address, request=3,
                                                     expected_response="ERROR: SIM PIN required"))
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_fqdn_address, request=3,
                                                     expected_response="ERROR: SIM PIN required"))

        test.log.step("3) Enter PIN and attach Module to NW (do not activate IPv6 context) and try "
                      "ping again:"
                      "- using IPv6 address (e.g. AT^SISX=\"PING\", 1, "
                      "\"2001:41d0:601:1100:0:0:0:72\", 3 )\n"
                      "- using domain name(FQDN)(e.g. AT^SISX=\"PING\", 1, "
                      "\"www.m2mtestserver2.testwro001.ovh\", 3 )")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_ip_address, request=3,
                                                     expected_response="ERROR: no network service"))
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_fqdn_address, request=3,
                                                     expected_response="ERROR: no network service"))

        test.log.step("4) Depends on product:"
                      "- activate IPv6 pdp context / nv bearer(e.g.using SICA Command)\n"
                      "- create IPv6 Connection profile")
        test.expect(connection_setup_object_ipv6.
                    dstl_load_and_activate_internet_connection_profile(), critical=True)
        dstl_select_printing_ip_address_format(test.dut, 1)

        test.log.step("5) Try SISX PING request to not existing IPv6 server(use random address) "
                      "with longest possible\n"
                      " < timelimit >:\n"
                      "- using IPv6 address(e.g. AT^SISX=\"PING\", 1, \"2001::1\", 3, 10000 )\n"
                      "- ping_execution_ipv6 domain name(FQDN)"
                      "(e.g. AT^SISX=\"PING\", 1, \"www.test1234567890test.ovh\", 3, 10000 )")
        test.expect(ping_execution_ipv6.dstl_execute_ping("2001::1", request=3, timelimit=10000,
                                                     expected_response=
                                                     "SISX: \"Ping\",1,{},\"2001::1\",-1"
                                                          .format(con_id_ipv6)))
        test.expect(test.dut.at1.wait_for("\"Ping\",2," + con_id_ipv6 + ",3,0,3,100.*",
                                          timeout=60))
        test.expect(ping_execution_ipv6.dstl_execute_ping("www.test1234567890test.ovh",
                                                              request=3, timelimit=10000,
                                                              expected_response="not found"))
        
        test.log.step("6) Activate firewall on available IPv6 server and check SISX PING request:\n"
                      "- using IPv6 address(e.g. AT^SISX =\"PING\", 1, "
                      "\"2001:41d0:601:1100:0:0:0:72\", 3, 10000 )\n"
                      "- using domain name(FQDN)(e.g. AT^SISX=\"PING\", 1, "
                      "\"www.m2mtestserver2.testwro001.ovh\", 3 )")

        test.log.info("Checking module IPV6 address on the server side")
        test.ping_server_thread = test.\
            thread(test.ip_server.dstl_server_execute_linux_command,
                   command="sudo tcpdump -i ens3 \"icmp6\" -c 1")
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_ip_address, request=3,
                                                          timelimit=10000,
                                                          expected_response="\"Ping\",2," +
                                                                            con_id_ipv6 +
                                                                            ",3,3,0,0.*"))
        test.ping_server_thread.join()
        test.log.info(test.ip_server.linux_server_response)
        response_list = list(test.ip_server.linux_server_response.split("\n"))
        keepalive_lines = []
        for line in response_list:
            if ("IP6 " in line) and ("neighbour" not in line):
                keepalive_lines.append(line)

        server_response = keepalive_lines[0].split("IP6 ")
        module_ipv6_address = server_response[1].split(" ")[0]

        test.ip_server.dstl_server_block_ping_function(module_ipv6_address)
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_ip_address, request=3,
                                                     expected_response="\"Ping\",2," + con_id_ipv6
                                                                       + ",3,0,3,100.*"))
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_fqdn_address, request=3,
                                                     expected_response="\"Ping\",2," + con_id_ipv6
                                                                       + ",3,0,3,100.*"))
        test.ip_server.dstl_server_accept_ping_function()

        test.log.step("7)  Try SISX PING request to available IPv6 server using wrong"
                      "(not activated for IPv6)\n"
                      " < conProfileId >:\n"
                      "- using IPv6 address(e.g. AT^SISX=\"PING\", 5, "
                      "\"2001:41d0:601:1100:0:0:0:72\", 3 )\n"
                      "- using domain name(FQDN)(e.g. AT^SISX=\"PING\", 5, "
                      "\"www.m2mtestserver2.testwro001.ovh\", 3 )")
        test.expect(connection_setup_object_ipv4.
                    dstl_load_and_activate_internet_connection_profile())
        test.expect(ping_execution_ipv4.dstl_execute_ping(server_ip_address, request=3,
                                                     expected_response="\"Ping\",2," + con_id_ipv4
                                                                       + ",3,0,3,100.*"))
        test.expect(ping_execution_ipv4.dstl_execute_ping("ipv6.google.com", request=3,
                                                     expected_response="not found"))

        test.log.step("8) Try PING request to avaliable IPv6 server:\n"
                      "- using IPv6 address(e.g. AT^SISX=\"PING\", 5, "
                      "\"2001:41d0:601:1100:0:0:0:72\", 3 )\n"
                      "- using domain name(FQDN)(e.g. AT^SISX=\"PING\", 5, "
                      "\"www.m2mtestserver2.testwro001.ovh\", 3 ")
        test.expect(connection_setup_object_ipv6.dstl_activate_internet_connection())
        test.expect(ping_execution_ipv6.dstl_execute_ping(server_ip_address, request=3,
                                                     expected_response="\"Ping\",2," + con_id_ipv6
                                                                       + ",3,3,0,0.*"))
        test.expect(ping_execution_ipv6.dstl_execute_ping("ipv6.google.com", request=3,
                                                     expected_response="\"Ping\",2," + con_id_ipv6
                                                                       + ",3,3,0,0.*"))

    def cleanup(test):
        try:
            test.ping_server_thread.join()
        except AttributeError:
            test.log.error("Thread was not created.")

        try:
            if not test.ip_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()