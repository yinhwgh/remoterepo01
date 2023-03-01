#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0094980.001, TC0094980.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_get_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.parser.internet_service_parser import SocketState, ServiceState
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    Intention:
        Check support for chunked transport mode.

    Precondition:
        One module with SIM card is required.
        Http server with chunked transfer encoding.
        Tracing tool is required
        Enter PIN and attach module to the network.
        Activate TCP/IP URCs.

    Description:
        1. Define PDP context for Internet services.
        2. Activate Internet service connection.
        3. Define HTTP GET profile to HTTP web page with chunked transfer encoding.
        4. Enable IP tracing (e.g. with Wireshark).
        5. Open HTTP profile.
        6. Check service state.
        7. Read all data.
        8. Check service state.
        9. Close HTTP service.
        10. Stop IP tracing.
        11. Analyze IP trace logs.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_scfg_tcp_with_urcs(test.dut, "on")
        dstl_enter_pin(test.dut)

    def run(test):
        test.log.info("Executing script for test case: 'TC0094980.001/002 HttpChunkedTransportMode'")
        test.log.step("1. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTTP web page with chunked transfer encoding.")
        test.server = HttpServer("IPv4",  extended=True)
        test.profile = HttpProfile(test.dut, "0", connection_setup.dstl_get_used_cid(), alphabet=1)
        test.profile.dstl_set_parameters_from_ip_server(test.server)
        test.profile.dstl_set_http_path("stream-bytes/5000")
        test.profile.dstl_generate_address()
        test.profile.dstl_set_http_command("get")
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("4. Enable IP tracing (e.g. with Wireshark).")
        module_ip = connection_setup.dstl_get_pdp_address()
        test.ssl_server_thread = test.thread(test.server.dstl_server_execute_linux_command,
                                        command="sudo tcpdump host {} -A -i ens3 -c 8".format(module_ip[0]))
        test.sleep(5)
        test.log.step("5. Open HTTP profile.")
        test.profile.dstl_get_service().dstl_open_service_profile()
        test.expect(test.profile.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="2200"))
        test.expect(test.profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("6. Check service state.")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("7. Read all data.")
        test.expect(test.profile.dstl_get_service().dstl_read_all_data(1500))

        test.log.step("8. Check service state.")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(test.profile.dstl_get_parser().dstl_get_service_data_counter("rx") == 5000)

        test.log.step("9. Close HTTP service.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Stop IP tracing.")
        test.ssl_server_thread.join()

        test.log.step("11. Analyze IP trace logs.")
        test.log.info("TCPDUMP RESPONSE:")
        test.log.info(test.server.linux_server_response)
        test.expect("Transfer-Encoding: chunked" in test.server.linux_server_response)

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

        if not test.profile.dstl_get_service().dstl_close_service_profile():
            test.log.warn("Problem during closing service profile.")


if "__main__" == __name__:
    unicorn.main()
