# responsible: tomasz.brzyk@globallogic.com
# location: Wroclaw
# TC0104918.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.internet_connection_setting.internet_connection_setting import \
    dstl_clear_all_internet_connection_setting, dstl_set_internet_connection_setting
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network


class Test(BaseTest):
    """
    Setting wrong/right DNS1 and DNS2 address and open UDP IPv4 service.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Executing TS for TC0104918.001SocketDNS_IPv4_basic")
        incorrect_dns1 = "8.8.8.0"
        incorrect_dns2 = "8.8.4.0"
        correct_dns1 = "8.8.8.8"
        correct_dns2 = "8.8.4.4"

        test.log.step("1. Attach Module to the Network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Define internet connection profile with correct APN.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. Define internet service profile for Socket client using FQDN address.")
        test.server = EchoServer("IPv4", "UDP")
        socket = SocketProfile(test.dut, "1", connection_setup.dstl_get_used_cid(),
                               protocol="udp", host=test.server.dstl_get_server_FQDN(),
                               ip_version=4, port=test.server.dstl_get_server_port())
        socket.dstl_generate_address()
        ip_server_address = test.server.dstl_get_server_ip_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("4. Define wrong IPv4 DNS addresses (For some products restart is needed).")
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "dns1", incorrect_dns1))
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "dns2", incorrect_dns2,
                                                         restart_needed=True))
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("5. Open service.")
        test.expect(socket.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("6. Wait for URC ^SIS")
        test.expect(socket.dstl_get_urc().dstl_is_sis_urc_appeared("0", timeout=180),
                    msg="Expected URC not appeared.")

        test.log.step("7. Check socket and service state.")
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        rem_ip_address = socket.dstl_get_parser().dstl_get_service_remote_address_and_port\
            (ip_version='IPv4')
        empty_address = "0.0.0.0:{}".format(test.server.dstl_get_server_port())
        test.expect(empty_address in rem_ip_address, msg="Empty remote address expected")

        test.log.step("8. Close service.")
        test.expect(socket.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Define correct IPV4 DNS addresses (For some products restart is needed).")
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "dns1", correct_dns1))
        test.expect(dstl_set_internet_connection_setting(test.dut, cid, "dns2", correct_dns2,
                                                         restart_needed=True))
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("10. Open service.")
        test.expect(socket.dstl_get_service().dstl_open_service_profile())

        test.log.step("11. Wait for URC.")
        test.expect(socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("12. Check socket and service state.")
        test.expect(socket.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(socket.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        rem_ip_address = socket.dstl_get_parser().dstl_get_service_remote_address_and_port(
            ip_version='IPv4')
        test.expect(ip_server_address.upper() in rem_ip_address,
                    msg="Correct remote address expected")

        test.log.step("13. Close service.")
        test.expect(socket.dstl_get_service().dstl_close_service_profile())
        test.expect(socket.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        try:
            if not test.server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.info("Restoring DNS settings to default values.")
        test.expect(dstl_clear_all_internet_connection_setting(test.dut, restart_needed=True))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        dstl_execute_sips_command(test.dut, "service", "save")


if "__main__" == __name__:
    unicorn.main()
