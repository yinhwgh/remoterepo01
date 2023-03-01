#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093577.001, TC0093577.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_compare_internet_service_profiles import dstl_compare_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_execute_sips_command import dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import dstl_check_no_internet_profiles_defined
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_modify_siss_read_response import dstl_modify_siss_read_response
from random import randint


class Test(BaseTest):
    """Check if module stable and properly saving/loading defined profiles after hard restart right after saving profiles."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.devboard.send_and_verify('MC:ver', 'OK'))

    def run(test):
        test.log.h2("Executing script for test case: ' 	TC0093577.001/002 InternetProfileStoragePowerCollision'")
        max_number_of_profiles = 10
        supported_services = ['socktcp', 'sockudp', 'http', 'ftp']
        test.all_services = {}
        service_profiles = []

        test.log.step("1) Enter PIN.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("2) Define PDP context or internet profile connection if module doesn't support PDP contexts.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        test.log.step("3) Clear all internet service profiles.")
        test.expect(dstl_reset_internet_service_profiles(test.dut))

        test.log.step("4) Define 10 service profiles (HTTP/FTP/Socket).")
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services) - 1)]
            service_profiles.append(define_service_profile(test, profile_number, service_type))
            test.all_services[profile_number] = service_type

        test.log.step("5) Check defined profiles.")
        profiles_list_all = dstl_get_siss_read_response(test.dut)
        dstl_check_siss_read_response(test.dut, service_profiles, test.dut.at1.last_response)

        test.log.step("6) Save all profiles and wait for OK.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("7) After receiving OK response, immediately restart the module (manually on DSB).")
        restart_module_with_mctest(test)

        test.log.step("8) Enter PIN.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("9) Check if service profiles are empty.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step("10) Load profiles with Internet Profile Storage command.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("11) Check loaded service profiles and compare the list with list from point 5.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), profiles_list_all)

        test.log.step("12) Reset all Internet profile Storage settings.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "reset"))

        test.log.step("13) Check defined profiles.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step("14) Load all profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("15) Check if loaded profiles are exactly the same as on list in point 5.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), profiles_list_all)

        test.log.step("16) Save only one chosen profile and wait for OK.")
        selected_profile = str(randint(0, max_number_of_profiles-1))
        test.expect(dstl_execute_sips_command(test.dut, "service", "save", selected_profile))

        test.log.step("17) Immediately after receiving OK response, restart the module (manually on DSB).")
        restart_module_with_mctest(test)

        test.log.step("18) Enter PIN.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("19) Load one (saved) profile with Internet Profile Storage command.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load", selected_profile))

        test.log.step("20) Check loaded service profile and compare it with list from point 5.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               dstl_modify_siss_read_response(test.dut, profiles_list_all, profile_to_leave=selected_profile))

        test.log.step("21) Clear all profiles.")

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))


def define_service_profile(test, profile_number, service_type):
    if 'http' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, test.con_id, alphabet=1, http_command="head",
                                      host="www.httpbin.org", ip_version='ipv4', http_path="bytes/2000")
    elif 'ftp' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, test.con_id, command="get", host="ftpserver",
                                     alphabet="1", files='test_profile_storage.txt', user="test_user_1", passwd="test123")
    elif 'sockudp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="udp", alphabet=1,
                                        host="2001:41B0:607:1100::117B", port="65222", ip_version='IPv6')
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="tcp", host="192.222.134.134",
                                        port="61234", ip_version='IPv4', secopt='1')
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


def restart_module_with_mctest(test):
    test.expect(test.dut.devboard.send_and_verify('MC:vbatt=off', 'OK'))
    test.sleep(2)
    test.expect(test.dut.devboard.send_and_verify('MC:vbatt=on', 'OK'))
    test.expect(test.dut.devboard.send_and_verify('MC:IGN=1000', 'OK'))
    test.expect(test.dut.at1.wait_for('SYSSTART'))


if "__main__" == __name__:
    unicorn.main()
