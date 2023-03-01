#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093574.001, TC0093574.002

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
from dstl.internet_service.profile_storage.dstl_modify_siss_read_response import dstl_modify_siss_read_response
from random import randint


class Test(BaseTest):
    """Check if module stable and properly saving/loading defined profiles after many attempts."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0093574.001/.002 InternetProfileStorageSaveLoadStress'")
        iterations = 400
        max_number_of_profiles = 10
        supported_services = ['http', 'ftp', 'socktcp', 'sockudp', 'https', 'ftps', 'socktcps', 'sockudps']

        test.log.step("1) Enter PIN if not entered yet.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("2) Define PDP context or internet profile connection if module doesn't support PDP contexts.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        for iteration in range(1, iterations+1):
            test.log.step("3) Clear all internet service profiles. \n Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_reset_internet_service_profiles(test.dut))
            test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

            test.log.step("4) Define random number (1-10) of different type of service profiles (HTTP/FTP/SMTP/Socket) "
                          "if all types are supported. \n Itearation no. {} of {}".format(iteration, iterations))
            number_of_profiles = randint(1, max_number_of_profiles)
            for profile_number in range(number_of_profiles):
                service_type = supported_services[randint(0, len(supported_services)-1)]
                define_service_profile(test, profile_number, service_type)

            test.log.step("5) Show defined profiles. \n Itearation no. {} of {}".format(iteration, iterations))
            defined_profiles_list = dstl_get_siss_read_response(test.dut)

            test.log.step("6) Chose randomly: with Internet Profile Storage command save all defined profiles or "
                          "save only one service profile. \n Itearation no. {} of {}".format(iteration, iterations))
            select_one_profile_number = randint(0,1)
            if select_one_profile_number:
                selected_profile_number = str(randint(0, number_of_profiles - 1))
                test.expect(dstl_execute_sips_command(test.dut, "service", "save", selected_profile_number))
            else:
                test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

            test.log.step("7) Restart module. \n Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_restart(test.dut))

            test.log.step("8) Enter PIN. \n Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_enter_pin(test.dut))

            test.log.step("9) Check if service profiles are empty. \n Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("10) Load profile(s) with Internet Profile Storage command. "
                          "\n Itearation no. {} of {}".format(iteration, iterations))
            if select_one_profile_number:
                test.expect(dstl_execute_sips_command(test.dut, "service", "load", selected_profile_number))
            else:
                test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

            test.log.step("11) Show loaded service profiles and compare the list with list from point 5. \n "
                          "Itearation no. {} of {}".format(iteration, iterations))
            if select_one_profile_number:
                modified_profiles_list = dstl_modify_siss_read_response(test.dut, defined_profiles_list, profile_to_leave=selected_profile_number)
                dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), modified_profiles_list)
            else:
                dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), defined_profiles_list)

            test.log.step("12) Reset all Internet profile Storage settings and check the result. \n "
                          "Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_execute_sips_command(test.dut, "service", "reset"))
            test.expect(dstl_check_no_internet_profiles_defined(test.dut))

            test.log.step("13) Load profile(s) again. \n Itearation no. {} of {}".format(iteration, iterations))
            test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

            test.log.step("14) Check service profiles. \n Itearation no. {} of {}".format(iteration, iterations))
            if select_one_profile_number:
                modified_profiles_list = dstl_modify_siss_read_response(test.dut, defined_profiles_list, profile_to_leave=selected_profile_number)
                dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), modified_profiles_list)
            else:
                dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut), defined_profiles_list)

            test.log.step("15) Repeat whole test {0} times.\nIteration: {1} of {0} finished.".format(iterations, iteration))

    def cleanup(test):
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
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="udp",  alphabet=1,
                                        host="2001:41D0:601:1100::137B", port="65100", ip_version='IPv6')
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="tcp", host="192.122.134.234",
                                        port="65123", secopt=0, ip_version='IPv4')
    if service_type.endswith('s'):
        service_profile.dstl_set_secure_connection(True)
        service_profile.dstl_set_secopt(1)
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())


if "__main__" == __name__:
    unicorn.main()
