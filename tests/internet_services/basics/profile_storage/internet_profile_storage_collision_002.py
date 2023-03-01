#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0087356.002, TC0087356.004

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_compare_internet_service_profiles import dstl_compare_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_execute_sips_command import dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import dstl_check_no_internet_profiles_defined
from random import randint


class Test(BaseTest):
    """Prove the correct functionality of the ^SIPS command in case profiles are in use."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0087356.002/004 InternetProfileStorageCollision'")
        max_number_of_profiles = 10
        service_profiles = []
        supported_services = ['socktcp', 'sockudp', 'http', 'ftp']
        test.tcp_echo_server = EchoServer('IPv4', "TCP")
        test.udp_echo_server = EchoServer('IPv4', "UDP")

        test.log.step("1. Enter PIN and attach module to the network if not done yet.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2. Clear all defined service profiles.")
        test.expect(dstl_reset_internet_service_profiles(test.dut))

        test.log.step("3. Define PDP context or internet profile connection if module doesn't support PDP contexts.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        test.log.step("4. Fill all profiles with HTTP/FTP/Socket profiles.")
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services) - 1)]
            define_service_profile(test, profile_number, service_type)
        profiles_list_all_types = dstl_get_siss_read_response(test.dut)

        test.log.step("5. Save all defined profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("6. Restart the module.")
        test.expect(dstl_restart(test.dut))

        test.log.step("7. Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("8. Check if all service profiles are empty.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step("9. Fill all profile with socket profiles.")
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services)/2 - 1)]
            service_profiles.append(define_service_profile(test, profile_number, service_type))

        test.log.step("10. Display the profiles.")
        profiles_list_only_sockets = dstl_get_siss_read_response(test.dut)

        test.log.step("11. Open all defined service profiles.")
        for profile_number in range(0, max_number_of_profiles):
            test.expect(service_profiles[profile_number].dstl_get_service().dstl_open_service_profile())
            test.expect(service_profiles[profile_number].dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("12. Try to load stored profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load", expected="ERROR"))

        test.log.step("13. Check the profiles.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), profiles_list_only_sockets)

        test.log.step("14. Close all open profiles.")
        for profile_number in range(0, max_number_of_profiles):
            test.expect(service_profiles[profile_number].dstl_get_service().dstl_close_service_profile())

        test.log.step("15. Load stored profiles again.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("16. Check the profiles.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), profiles_list_all_types)

    def cleanup(test):
        try:
            if not test.tcp_echo_server.dstl_server_close_port() or test.udp_echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))


def define_service_profile(test, profile_number, service_type):
    if 'http' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, test.con_id, alphabet=1, http_command="get",
                                      host="www.httpbin.org", ip_version='ipv4', http_path="bytes/1000")
    elif 'ftp' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, test.con_id, command="get", host="ftpserver",
                                     alphabet="1", files='test.txt', user="test_user", passwd="test123")
    elif 'sockudp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="udp")
        service_profile.dstl_set_parameters_from_ip_server(test.udp_echo_server)
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="tcp")
        service_profile.dstl_set_parameters_from_ip_server(test.tcp_echo_server)
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


if "__main__" == __name__:
    unicorn.main()
