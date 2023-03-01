# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0093572.001, TC0093572.002

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
    """Prove the correct functionality of the ^SIPS command via the USB interface."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("Executing script for test case: "
                    "'TC0093572.001/002 InternetProfileStorageBasicUsb'")
        usb_interfaces = ['dut_usb_m', 'dut_usb_a','dut_usb_d', 'dut_usb_n']
        max_number_of_profiles = 10
        supported_services = ['socktcp', 'sockudp', 'http', 'ftp']
        test.all_services = {}
        dstl_reset_internet_service_profiles(test.dut)

        for usb_interface in usb_interfaces:
            test.remap({'dut_at1': usb_interface})
            test.log.step("Do the following scenario at USB: {}".format(usb_interface))
            service_profiles = []

            test.log.step("1. Define 9 service profiles with a minimum set of parameters.")
            for profile_number in range(max_number_of_profiles-1):
                service_type = supported_services[randint(0, len(supported_services) - 1)]
                service_profiles.append(define_service_profile(test, profile_number, service_type))
                test.all_services[profile_number] = service_type

            test.log.step("2. Display all profiles.")
            profiles_list_all = dstl_get_siss_read_response(test.dut)
            test.expect('SISS: 9,"srvType",""' in test.dut.at1.last_response)
            dstl_check_siss_read_response(test.dut, service_profiles, test.dut.at1.last_response)

            test.log.step("3. Save all profiles.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))

            test.log.step("4. Restart the DUT.")
            test.expect(dstl_restart(test.dut))

            test.log.step("5. Enter the PIN.")
            test.expect(dstl_enter_pin(test.dut))

            test.log.step("6. Display service profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("7. Load an undefined service profile.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', '9'))

            test.log.step("8. Display service profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("9. Load one of defined service profiles.")
            selected_profile = str(randint(0, max_number_of_profiles-2))
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', selected_profile))

            test.log.step("10. Display service profiles.")
            dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                            dstl_modify_siss_read_response(test.dut,
                                            profiles_list_all, profile_to_leave=selected_profile))

            test.log.step("11. Load all saved profiles.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'load'))

            test.log.step("12. Display service profiles.")
            dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                                   profiles_list_all)

            test.log.step("13. Reset the reloaded service profile.")
            test.expect(dstl_execute_sips_command(test.dut, 'service', 'reset'))

            test.log.step("14. Display all service profiles.")
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("15. Repeat the scenario above on each USB interface "
                          "(if module support more than one).")

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
