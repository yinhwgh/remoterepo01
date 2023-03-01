# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0087355.002

from random import randint
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_turn_on_vbatt_via_dev_board, \
    dstl_turn_on_igt_via_dev_board, dstl_switch_off_at_echo
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.shutdown_smso import dstl_shutdown_smso
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import \
    dstl_check_no_internet_profiles_defined
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_compare_internet_service_profiles import \
    dstl_compare_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """ Prove the correct functionality of the ^SIPS command via RS232 interface """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_switch_off_at_echo(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_reset_internet_service_profiles(test.dut))

    def run(test):
        test.log.info('Executing script for test case: '
                      '"TC0087355.002 InternetProfileStorageOverwrite_dahlia"')
        max_number_of_profiles = 10
        supported_services = ['socktcp', 'sockudp', 'http', 'ftp', 'mqtt']
        service_profiles_1st = []
        service_profiles_2nd = []

        test.log.step(f'Do the following scenario at ASC0: {"dut_asc_0"}')
        test.remap({'dut_at1': 'dut_asc_0'})

        test.log.step('1. Define all possible service profiles.')
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services)-1)]
            service_profiles_1st.append(define_service_profile(test, profile_number, service_type))

        test.log.step('2. Display all internet service profiles.')
        profiles_list_all_1st = dstl_get_siss_read_response(test.dut)
        dstl_check_siss_read_response(test.dut, service_profiles_1st, test.dut.at1.last_response)

        test.log.step('3. Save all service profiles.')
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'save'))

        test.log.step('4. Switch off the DUT.')
        test.expect(dstl_shutdown_smso(test.dut))

        test.log.step('5. Wait 10 seconds.')
        test.sleep(10)

        test.log.step('6. Switch on the DUT.')
        test.expect(dstl_turn_on_vbatt_via_dev_board(test.dut))
        test.expect(dstl_turn_on_igt_via_dev_board(test.dut))
        test.expect(test.dut.at1.wait_for("SYSSTART"))

        test.log.step('7. Enter the PIN.')
        test.expect(dstl_enter_pin(test.dut))

        test.log.step('8. Display all internet service profiles.')
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step('9. Define service profiles but different than before.')
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services)-1)]
            service_profiles_2nd.append(define_service_profile(test, profile_number, service_type))

        test.log.step('10. Display all internet service profiles.')
        dstl_check_siss_read_response(test.dut, service_profiles_2nd)

        test.log.step('11. Load all of the defined profiles.')
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'load'))

        test.log.step('12. Display all internet service profiles.')
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               profiles_list_all_1st)

    def cleanup(test):
        test.log.step('13. Reset all profiles.')
        test.expect(dstl_reset_internet_service_profiles(test.dut))

        test.log.step('14. Display all internet service profiles.')
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))


def define_service_profile(test, profile_number, service_type):
    if 'http' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, '1', http_command="head",
                                      host="www.httpbin.org")
    elif 'ftp' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, '1', command="get",
                                     host="ftpserver",
                                     files='profile_storage.txt', user="user123",
                                     passwd="test123")
    elif 'sockudp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, '1', protocol="udp",
                                        host="122.242.234.89", port="64321")
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, '1', protocol="tcp",
                                        host="192.222.134.224", port="61234")
    else:
        service_profile = MqttProfile(test.dut, profile_number, '1', cmd="publish", topic="mqtt",
                                      client_id='123', hc_cont_len='0', hc_content="12345")
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


if "__main__" == __name__:
    unicorn.main()