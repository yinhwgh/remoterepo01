#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0094546.001, TC0094546.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_get_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response


class Test(BaseTest):
    """
    Intention:
        Check maximum number of redirects

    Precondition:
        One module with SIM card is required.
        Enter PIN and attatch module to the network.
        Http server with 7 URL redirects.
        Activate TCP/IP URCs.

    Description:

        1. Define PDP context for Internet services.
        2. Activate Internet service connection.
        3. Define HTTP GET profile to HTTP web page with 7 redirects (e.g. http://www.httpbin.org/absolute-redirect/7).
        4. Check current settings of all Internet service profiles.
        5. Open HTTP profile.
        6. Check service state.
        7. Read all data.
        8. Check service state.
        9. Close HTTP service.
    """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_scfg_tcp_with_urcs(test.dut, "on")
        dstl_enter_pin(test.dut)

    def run(test):
        test.log.step("1. Define PDP context for Internet services.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("3. Define HTTP GET profile to HTTP web page with 7 redirects "
                      "(e.g. http://www.httpbin.org/absolute-redirect/7).")
        test.address = "absolute-redirect/7"
        test.server = HttpServer("IPv4")
        test.profile = HttpProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid())
        test.profile.dstl_set_parameters_from_ip_server(test.server)
        test.profile.dstl_set_http_path(test.address)
        test.profile.dstl_generate_address()
        test.profile.dstl_set_http_command("get")
        test.expect(test.profile.dstl_get_service().dstl_load_profile())

        test.log.step("4. Check current settings of all Internet service profiles.")
        dstl_check_siss_read_response(test.dut, [test.profile])

        test.log.step("5. Open HTTP profile.")
        test.profile.dstl_get_service().dstl_open_service_profile()
        test.sleep(30) #waiting for profile to open, and scanning buffer for appropraite URC
        buffer = test.dut.at1.last_response + "\n" + test.dut.at1.read()
        host_port = "{}:{}".format(test.profile._model.host, test.profile._model.port)
        for i in range(1, 7):
            test.expect("SIS: 0,0,2200,\"redirect to: http://{}/absolute-redirect/{}".format(host_port, i) in buffer)

        test.expect("SIS: 0,0,2200,\"redirect to: http://{}/get".format(host_port) in buffer)

        test.expect("SISR: 0,1" in buffer)
        test.expect("SIS: 0,0,2200,\"Http connect {}\"".format(host_port) in buffer)

        test.log.step("6. Check service state.")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 4)

        test.log.step("7. Read all data.")
        test.expect(test.profile.dstl_get_service().dstl_read_all_data(1500, 1000))

        test.log.step("8. Check service state.")
        test.expect(test.profile.dstl_get_parser().dstl_get_service_state() == 6)

        test.log.step("9. Close HTTP service.")
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.profile.dstl_get_service().dstl_close_service_profile()
        except AttributeError:
            test.log.error("Profile object was not created.")

        try:
            test.server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
