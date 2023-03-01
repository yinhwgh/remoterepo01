# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0087436.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_execute_sips_command import \
    dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from random import randint
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board, \
    dstl_turn_on_vbatt_via_dev_board, \
    dstl_turn_on_igt_via_dev_board, dstl_switch_on_at_echo


class Test(BaseTest):
    """Prove the stability of the ^SIPS command against loss of power, prove that using IP service
    is still possible after power loss during saving or loading profiles."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_switch_on_at_echo(test.dut)

    def run(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.log.h2("Executing script for test case: 'TC0087436.002 - "
                    "InternetProfileStorageStress'")

        max_number_of_profiles = 10
        restart_timeout = 240
        supported_services = ['http', 'ftp', 'socktcp', 'sockudp', 'https', 'ftps', 'socktcps',
                              'sockudps']
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        test.con_id = connection_setup.dstl_get_used_cid()

        service_profiles = []
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services) - 1)]
            service_profiles.append(define_service_profile(test, profile_number, service_type))

        test.log.step("1. Power loss during restart")
        test.log.step("1.1 Save all internet profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

        test.log.step("1.2 Restart the module.")
        restart_parallel = test.thread(dstl_restart, test.dut, timeout=restart_timeout)
        test.sleep(1)
        test.log.step("1.3 Disconnect the power supply during restart.")
        emergoff_parallel = test.thread(switch_module_off_and_on, test)
        emergoff_parallel.join()
        restart_parallel.join()

        test.log.step("1.4 Wait 10 seconds. (done in step 1.3)")
        test.log.step("1.5 Reconnect the power supply. (done in step 1.3)")
        test.log.step("1.6 Restart the module. (done in step 1.3)")
        test.log.step("1.7 Load all internet profiles.")
        test.sleep(60)  # added sleep so module has time to turn on
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("1.8 Display all internet profiles.")
        dstl_check_siss_read_response(test.dut, service_profiles)

        test.log.step("2. Power loss during profile saving")
        test.log.step("2.1 Save all internet profiles.")
        save_parallel = test.thread(dstl_execute_sips_command, test.dut, "service", "save")

        test.sleep(0.2)
        test.log.step("2.2 Disconnect the power supply right after the AT command.")
        emergoff_parallel = test.thread(switch_module_off_and_on, test)
        emergoff_parallel.join()
        save_parallel.join()

        test.log.step("2.3 Wait 10 seconds. (done in step 2.2)")
        test.log.step("2.4 Reconnect the power supply. (done in step 2.2)")
        test.log.step("2.5 Restart the module. (done in step 2.2)")
        test.log.step("2.6 Load all internet profiles.")
        test.sleep(60)  # added sleep so module has time to turn on
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("2.7 Display all internet profiles.")
        dstl_check_siss_read_response(test.dut, service_profiles)

        test.log.step("3. Power loss during profile loading")
        test.log.step("3.1 Load all internet profiles.")
        load_parallel = test.thread(dstl_execute_sips_command, test.dut, "service", "load")

        test.log.step("3.2 Disconnect the power supply right after the AT command.")
        emergoff_parallel = test.thread(switch_module_off_and_on, test)
        emergoff_parallel.join()
        load_parallel.join()

        test.log.step("3.3 Wait 10 seconds. (done in step 3.2)")
        test.log.step("3.4 Reconnect the power supply. (done in step 3.2)")
        test.log.step("3.5 Restart the module. (done in step 3.2)")
        test.log.step("3.6 Load all internet profiles.")
        test.sleep(60)  # added sleep so module has time to turn on
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("3.7 Display all internet profiles.")
        dstl_check_siss_read_response(test.dut, service_profiles)


    def cleanup(test):
        test.expect(dstl_reset_internet_service_profiles(test.dut))
        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))


def switch_module_off_and_on(test):
    dstl_turn_off_vbatt_via_dev_board(test.dut)
    test.sleep(10)
    dstl_turn_on_vbatt_via_dev_board(test.dut)
    dstl_turn_on_igt_via_dev_board(test.dut)


def define_service_profile(test, profile_number, service_type):
    if 'http' in service_type:
        service_profile = HttpProfile(test.dut, profile_number, test.con_id, alphabet=1,
                                      http_command="get", host="www.httpbin.org", ip_version='ipv4',
                                      http_path="bytes/1000")
    elif 'ftp' in service_type:
        service_profile = FtpProfile(test.dut, profile_number, test.con_id, command="get",
                                     host="ftpserver", alphabet="1", files='test.txt',
                                     user="test_user", passwd="test123")
    elif 'sockudp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="udp",
                                        host="8.8.8.8", port="65100", ip_version='IPv4')
    elif 'socktcp' in service_type:
        service_profile = SocketProfile(test.dut, profile_number, test.con_id, protocol="tcp",
                                        host="192.122.134.234", port="65123", secopt=0,
                                        ip_version='IPv4')
    if service_type.endswith('s'):
        service_profile.dstl_set_secure_connection(True)
        service_profile.dstl_set_secopt(1)
    service_profile.dstl_generate_address()
    test.expect(service_profile.dstl_get_service().dstl_load_profile())
    return service_profile


if "__main__" == __name__:
    unicorn.main()
