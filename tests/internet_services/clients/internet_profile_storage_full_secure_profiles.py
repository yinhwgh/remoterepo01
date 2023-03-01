#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0105448.001, TC0105448.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
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
    """Prove the correct functionality of the ^SIPS command  for secure service profiles."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0105448.001/.002 InternetProfileStorageFullSecureProfiles'")
        max_number_of_profiles = 10
        test.all_services = {}
        service_profiles = []
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.con_id = connection_setup.dstl_get_used_cid()
        supported_services = ['https', 'ftps', 'socktcps', 'sockudps']

        test.log.step("1. Define all possible service profiles with the secure parameters (e.g., ftps, udps, tcps, https)")
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services) - 1)]
            service_profiles.append(define_service_profile(test, profile_number, service_type))
            test.all_services[profile_number] = service_type

        test.log.step("2. Display all internet service profiles.")
        defined_profiles_list = dstl_get_siss_read_response(test.dut)
        dstl_check_siss_read_response(test.dut, service_profiles, test.dut.at1.last_response)

        test.log.step("3. Save all service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("4. Reset the DUT. Enter the PIN.")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("5. Load all saved service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("6. Display all internet service profiles")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), defined_profiles_list)

        test.log.step("7. Reset one of the defined service profiles.")
        selected_profile_number = str(randint(0, max_number_of_profiles-1))
        test.expect(dstl_execute_sips_command(test.dut, "service", "reset", selected_profile_number))

        test.log.step("8. Save all service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("9. Reset the DUT. Enter the PIN.")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("10. Load saved service profiles (from step 8).")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("11. Display internet service profiles.")
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               dstl_modify_siss_read_response(test.dut, defined_profiles_list,
                                                                              profile_to_remove=selected_profile_number))

        test.log.step("12. Reset all of the defined service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "reset"))

        test.log.step("13. Save all service profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("14. Reset the DUT. Enter the PIN.")
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("15. Load saved service profiles (from step 13).")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("16. Display all internet service profiles.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))


def define_service_profile(test, profile_number, service_type):
    if 'https' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, test.con_id, alphabet=1, http_command="get",
                                      host="www.httpbin.org", ip_version='ipv4', http_path="bytes/1000")
    elif 'ftps' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, test.con_id, command="get", host="ftpserver",
                                     alphabet="1", files='test.txt', user="test_user", passwd="test123", secopt='1')
    elif 'sockudps' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="udp",  alphabet=1,
                                        host="2001:41D0:601:1100::137B", port="65100", ip_version='IPv6')
    elif 'socktcps' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="tcp", host="192.122.134.234",
                                        port="65123", ip_version='IPv4', secopt='1')
    service_profile.dstl_set_secure_connection(True)
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


if "__main__" == __name__:
    unicorn.main()
