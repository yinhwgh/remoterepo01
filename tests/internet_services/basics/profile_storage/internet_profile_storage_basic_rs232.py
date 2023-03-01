# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0087351.001, TC0087351.003

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart
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
    """Prove the correct functionality of the ^SIPS command via the RS232 interface."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("Executing script for test case: "
                    "'TC0087351.001/003 InternetProfileStorageBasicRS232'")
        asc_interfaces = ['dut_asc_0', 'dut_asc_1']
        max_number_of_profiles = 10
        supported_services = ['socktcp', 'sockudp', 'http', 'ftp']
        test.all_services = {}
        dstl_reset_internet_service_profiles(test.dut)

        for asc_interface in asc_interfaces:
            test.remap({'dut_at1': asc_interface})
            if asc_interface == 'dut_asc_0':
                test.log.step("Do the following scenario at ASC0")
            service_profiles = []

            test.log.step("Define 9 connection (If SIPS command covers connection profiles) and "
                          "service profiles with a minimum set of parameters.")
            for profile_number in range(max_number_of_profiles-1):
                service_type = supported_services[randint(0, len(supported_services) - 1)]
                service_profiles.append(define_service_profile(test, profile_number, service_type))
                test.all_services[profile_number] = service_type

            test.log.step("2. Display all internet profiles.")
            profiles_list_all = dstl_get_siss_read_response(test.dut)
            test.expect('SISS: 9,"srvType",""' in test.dut.at1.last_response)
            dstl_check_siss_read_response(test.dut, service_profiles, test.dut.at1.last_response)

            test.log.step("3. Save the profiles.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))

            test.log.step("4. Restart the DUT.")
            test.expect(dstl_restart(test.dut))

            test.log.step("5. Enter the PIN.")
            test.sleep(30)###to give module time to enable SIM
            test.expect(dstl_enter_pin(test.dut))

            test.log.step("6. Display all internet profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("7. Load an undefined connection (If SIPS command covers connection "
                          "profiles) profile and an undefined service profile.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', '9'))

            test.log.step("8. Display all internet profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("9. Load the defined connection profile. (If SIPS command "
                          "covers connection profiles)")
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step("10. Display all internet profiles. (If SIPS command covers connection "
                          "profiles)")
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step("11. Load a defined service profile.")
            selected_profile = str(randint(0, max_number_of_profiles-2))
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', selected_profile))

            test.log.step("12. Display all internet profiles.")
            dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                            dstl_modify_siss_read_response(test.dut,
                                            profiles_list_all, profile_to_leave=selected_profile))

            test.log.step("13. Reset the reloaded connection profile. (If SIPS command covers "
                          "connection profiles)")
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step("14. Display all internet profiles. (If SIPS command covers connection "
                          "profiles)")
            test.log.info("SIPS command does not support connection profiles on Viper")

            test.log.step("15. Reset the reloaded service profile.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'reset'))

            test.log.step("16. Display all service profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("Repeat the scenario above at ASC1")

    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))


def define_service_profile(test, profile_number, service_type):
    if 'http' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, '1', http_command="head",
                                      host="www.httpbin.org")
    elif 'ftp' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, '1', command="get", host="ftpserver",
                                     files='profile_storage.txt', user="user123", passwd="test123",
                                     alphabet=1)
    elif 'sockudp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, '1', protocol="udp",
                                        host="122.242.234.89", port="64321")
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, '1', protocol="tcp",
                                        host="192.222.134.224", port="61234")
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


if "__main__" == __name__:
    unicorn.main()
