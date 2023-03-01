# responsible maciej.gorny@globallogic.com
# Wroclaw
# TC0093320.001, TC0093320.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState


class Test(BaseTest):
    """
    Short description:
    Check http parameters: user agent and http properties

    Detailed description:
    1. Define PDP context for Internet services.
    2. Activate Internet service connection.
    3. Define HTTP GET profile to HTML web page (e.g. http://www.httpbin.org/html).
    4. Set hcUserAgent parameter to "Test User Agent"
    5. Set hcProp parameter to
    "Connection: keep-alive\0d\0aAccept-Language: pl,en-US;q=0.7,en;q=0.3\0d\0aContent-Type: text/html"
    6. Enable IP tracing (e.g. with Wireshark).
    7. Open HTTP profile.
    8. Check service state.
    9. Read all data.
    10. Check service state.
    11. Close HTTP service.
    12. Stop IP tracing.
    13. Analize IP trace logs.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        test.log.info("Executing script for test case: 'TC0093320.001/002 TcHttpHcUserAgentProp'")
        hcuser_agent_value = "Test User Agent"
        hcprop_value = "Connection: keep-alive/0d/0aAccept-Language: pl,en-US;q=0.7,en;q=0.3/0d/0aContent-Type:" \
                       " text/html"
        test.server = HttpServer("IPv4", extended=True)
        server_ip_address = test.server.dstl_get_server_ip_address()
        server_port = test.server.dstl_get_server_port()

        test.log.step("1. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTML web page (e.g. http://www.httpbin.org/html).")
        srv_id = "0"
        con_id = connection_setup.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, srv_id, con_id, http_command="get", host=server_ip_address,port=server_port)
        http_client.dstl_set_hc_prop(hcprop_value)
        http_client.dstl_set_hc_user_agent(hcuser_agent_value)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Set hcUserAgent parameter to 'Test User Agent'")
        test.log.info("Done in previous step")

        test.log.step("5. Set hcProp parameter to \r\n "
        "'Connection: keep-alive\0d\0aAccept-Language: pl,en-US;q=0.7,en;q=0.3\0d\0aContent-Type: text/html'")
        test.log.info("Done in previous step")

        test.log.step("6. Enable IP tracing (e.g. with Wireshark).")
        module_ip = connection_setup.dstl_get_pdp_address()
        test.ssl_server_thread = test.thread(test.server.dstl_server_execute_linux_command,
                                        command="sudo tcpdump host {} -A -e -i ens3 -c 6".format(module_ip[0]))
        test.sleep(5)

        test.log.step("7. Open HTTP profile.")
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                    '"Http connect {}:{}"'.format(server_ip_address, server_port)))
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("8. Check service state.")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(http_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("9. Read all data.")
        test.expect(http_client.dstl_get_service().dstl_read_all_data(1500))
        test.expect("SIS: {},0,48,\"Remote peer has closed the connection\"".format(srv_id)
                    in http_client.dstl_get_service().sisr_last_response)
        test.expect("SISR: {},2\r\n".format(srv_id) in http_client.dstl_get_service().sisr_last_response)

        test.log.step("10. Check service state")
        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(http_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("11. Close HTTP GET service.")
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())
        test.expect(http_client.dstl_get_service().dstl_reset_service_profile())

        test.log.step("12. Stop IP tracing.")
        test.ssl_server_thread.join()

        test.log.step("13. Analyze IP trace logs.")
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.server.linux_server_response)
        test.expect("User-Agent: "+hcuser_agent_value in test.server.linux_server_response)
        test.expect("Connection: keep-alive" in test.server.linux_server_response)
        test.expect("Accept-Language: pl,en-US;q=0.7,en;q=0.3" in test.server.linux_server_response)
        test.expect("Content-Type: text/html" in test.server.linux_server_response)


    def cleanup(test):
        try:
            test.ssl_server_thread.join()
        except AttributeError:
            test.log.error("Problem with join thread.")

        try:
            if not test.server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
