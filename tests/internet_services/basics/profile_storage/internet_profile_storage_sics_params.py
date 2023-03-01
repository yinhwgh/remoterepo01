# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094952.001, TC0094952.002
from random import randint

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_no_internet_profiles_defined import \
    dstl_check_no_internet_profiles_defined
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_execute_sips_command import dstl_execute_sips_command
from dstl.internet_service.profile_storage.dstl_get_siss_read_response \
    import dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """ TC intention: Check saving/loading of AT^SIPS command for Internet Profile's."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))


    def run(test):
        supported_services = ['http', 'ftp', 'socktcp', 'sockudp', 'https', 'ftps', 'socktcps',
                              'sockudps']
        max_number_of_profiles = 10

        test.log.info("Executing TS for TC0094952.001/002 InternetProfileStorageSicsParams")
        test.log.step("1. Enter PIN.")
        test.log.info("PIN entered in preparation")

        test.log.step("2. Define PDP context.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.con_id = test.connection_setup.dstl_get_used_cid()

        test.log.step("3. Define connections and fill all possible Internet Profiles.")

        service_profiles = []
        for profile_number in range(max_number_of_profiles):
            service_type = supported_services[randint(0, len(supported_services) - 1)]
            service_profiles.append(test.define_service_profile(profile_number, service_type))
        dstl_check_siss_read_response(test.dut, service_profiles)

        test.log.step("4. Save all profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "save",))

        test.log.step("5. Reset the profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "reset"))

        test.log.step("6. Display and check the Internet Profiles.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step("7. Restart module.")
        test.expect(dstl_restart(test.dut))

        test.log.step("8. Enter PIN.")
        test.sleep(30)
        """to give module time to activate SIM card"""
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("9. Display and check the Internet Profiles.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.log.step("10. Load all profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "load"))

        test.log.step("11. Display and check the Internet Profiles.")
        dstl_check_siss_read_response(test.dut, service_profiles)

    def cleanup(test):
        test.log.step("12. Reset all profiles.")
        test.expect(dstl_execute_sips_command(test.dut, "service", "reset"))

        test.log.step("13. Display and check the Internet Profiles.")
        test.expect(dstl_check_no_internet_profiles_defined(test.dut))

        test.expect(dstl_execute_sips_command(test.dut, "service", "save"))

    def define_service_profile(test, profile_number, service_type):
        if 'http' in service_type:
            service_profile = HttpProfile(test.dut, profile_number, test.con_id, alphabet=1,
                                          http_command="get", host="www.httpbin.org",
                                          ip_version='ipv4',
                                          http_path="bytes/1000")
        elif 'ftp' in service_type:
            service_profile = FtpProfile(test.dut, profile_number, test.con_id, command="get",
                                         host="ftpserver", alphabet="1", files='test.txt',
                                         user="test_user", passwd="test123", ftpath="/ftpath")
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