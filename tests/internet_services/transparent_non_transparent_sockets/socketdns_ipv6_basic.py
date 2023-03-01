# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0104939.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.internet_connection_setting.internet_connection_setting import \
    dstl_set_internet_connection_setting, dstl_clear_all_internet_connection_setting
from dstl.internet_service.parser.internet_service_parser import SocketState, ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """ Setting wrong/right DNS1 and DNS2 address and open TCP IPv6 service. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.echo_server = EchoServer("IPv6", "TCP")

    def run(test):
        test.log.info("Executing TS for TC0104939.001 SocketDNS_IPv6_basic")
        test.log.step("1. Attach modules to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Define internet connection profile with correct APN.")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3. Define internet service profile for Socket client using FQDN address.")
        fqdn_server_address = test.echo_server.dstl_get_server_FQDN()
        ip_server_address = test.echo_server.dstl_get_server_ip_address()
        cid = connection_setup.dstl_get_used_cid()
        test.socket = SocketProfile(test.dut, "6", cid,  protocol="tcp", alphabet='1', ip_version=6,
                                    host=fqdn_server_address, port=test.echo_server.
                                    dstl_get_server_port())
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("4. Define wrong IPv6 DNS addresses (For some products restart is needed).")
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "ipv6dns1",
                                                         "2001:41d0:601:1111::92"))
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "ipv6dns2",
                                                         "2001:41d0:601:1177::79",
                                                         restart_needed=True))
        test.sleep(5)
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.sleep(5)

        test.log.step("5. Open service.")
        test.expect(test.socket.dstl_get_service().dstl_open_service_profile(
            wait_for_default_urc=False))

        test.log.step("6. Wait for URC ^SIS")
        test.expect(test.socket.dstl_get_urc().dstl_is_sis_urc_appeared("0", timeout=180),
                    msg="Expected URC not appeared.")

        test.log.step("7. Check socket and service state.")
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(test.socket.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)
        rem_ip_address = test.socket.dstl_get_parser().dstl_get_service_remote_address_and_port(
            'IPv6')
        empty_address = "[::]:{}".format(test.echo_server.dstl_get_server_port())
        test.expect(empty_address in rem_ip_address, msg="Empty remote address expected")

        test.log.step("8. Close service.")
        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Define correct IPv6 DNS addresses (For some products restart is needed).")
        test.expect(dstl_set_internet_connection_setting(test.dut, 1, "ipv6dns1",
                                                         "2001:4860:4860::8888"))
        test.expect(dstl_set_internet_connection_setting(test.dut, 1, "ipv6dns2",
                                                         "2001:4860:4860::8844",
                                                         restart_needed=True))
        test.sleep(5)
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.sleep(5)

        test.log.step("10. Open service.")
        test.expect(test.socket.dstl_get_service().dstl_open_service_profile())

        test.log.step("11. Wait for URC ^SIS")
        test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("12. Check socket and service states")
        test.expect(test.socket.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)
        test.expect(test.socket.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)
        rem_ip_address = test.socket.dstl_get_parser().dstl_get_service_remote_address_and_port(
            "IPv6")
        test.expect(ip_server_address.upper() in rem_ip_address, 
                    msg="Correct remote address expected")

    def cleanup(test):
        test.log.step("13. Close service.")
        try:
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket.dstl_get_service().dstl_reset_service_profile())
            dstl_clear_all_internet_connection_setting(test.dut, restart_needed=True)
        except AttributeError:
            test.log.error("Socket object was not created.")
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()