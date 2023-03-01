# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0105397.001

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.auxiliary.restart_module import dstl_restart
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.configuration.scfg_remapping_ipv6 import dstl_enable_remapping_ipv6_iid, \
    dstl_disable_remapping_ipv6_iid
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.packet_domain.select_printing_ip_address_format import \
    dstl_select_printing_ip_address_format


class Test(BaseTest):
    """
    TC intention: Test behavior of TCP/RemappingIpv6IID setting impact for the FTP client profile.

    1. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module
    2. On DUT module define and activate IPV6 PDP contexts
    3. On DUT set printing IP address format to IPv6-like colon-notation
    4. On DUT define and open 2 IPV6 FTP get profiles (one using IPV6 server address, second FQDN)
    5. On DUT check and compare local addresses assigned in siso and cgpaddr
    6. Download data from server on both profiles.
    7. Close FTP profiles on DUT.
    8. On DUT Set the TCP/RemappingIpv6IID setting to 1 and restart module
    9. Repeat steps 2-7.
    10. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6',
                                                                 ip_public=True)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.file_size = 1500
        test.file_name = "ftp_client_ipv6_address_allocation_check.txt"
        test.ipv6_regex = "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([" \
                          "0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9" \
                          "a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([" \
                          "0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2" \
                          "}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|" \
                          ":((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z" \
                          "]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[" \
                          "0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4" \
                          "}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[" \
                          "0-4]|1{0,1}[0-9]){0,1}[0-9]))"

    def run(test):
        test.log.step("1. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module")
        test.set_remappingipv6iid_and_restart(0)
        test.execute_steps_2_to_7()

        test.log.step("8. On DUT Set the TCP/RemappingIpv6IID setting to 1 and restart "
                      "module")
        test.set_remappingipv6iid_and_restart(1)

        test.log.step("9. Repeat steps 2-7.")
        test.execute_steps_2_to_7()

    def cleanup(test):
        test.log.step("10. On DUT Set the TCP/RemappingIpv6IID setting to 0 and restart module")
        test.set_remappingipv6iid_and_restart(0)

        try:
            if not test.ftp_server.dstl_server_close_port() and not \
                    test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")

    def set_remappingipv6iid_and_restart(test, value=0):
        if value == 0:
            test.expect(dstl_disable_remapping_ipv6_iid(test.dut))
        else:
            test.expect(dstl_enable_remapping_ipv6_iid(test.dut))
        test.expect(dstl_restart(test.dut))
        test.expect(dstl_enter_pin(test.dut))

    def execute_steps_2_to_7(test):
        test.log.step("2. On DUT module define and activate IPV6 PDP contexts")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftp_server = FtpServer("IPv6", test, test.connection_setup.dstl_get_used_cid())
        test.expect(test.ftp_server.dstl_ftp_server_create_file(test.file_name, test.file_size),
                    critical=True)

        test.log.step("3. On DUT set printing IP address format to IPv6-like colon-notation")
        test.expect(dstl_select_printing_ip_address_format(test.dut, 1))

        test.log.step("4. On DUT define and open 2 IPV6 FTP get profiles "
                      "(one using IPV6 server address, second FQDN)")
        ftp_clients = test.define_ftp_profiles()
        test.expect(dstl_get_siss_read_response(test.dut))
        for profile in ftp_clients:
            test.expect(profile.dstl_get_service().dstl_open_service_profile())
            test.expect(profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("5. On DUT check and compare local addresses assigned in siso and cgpaddr")
        address_from_cgpaddr = test.connection_setup.dstl_get_pdp_address()[0].upper()
        test.expect(re.search(test.ipv6_regex, address_from_cgpaddr))
        for profile in ftp_clients:
            address_from_siso = profile.dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version="IPv6").split("[")[1].split("]:")[0].upper()
            test.expect(address_from_siso != address_from_cgpaddr, msg="Comparing address from siso"
                                                                       " and address from cgpaddr")

        test.log.step("6. Download data from server on both profiles.")
        for profile in ftp_clients:
            test.expect(len(profile.dstl_get_service().dstl_read_return_data(test.file_size))
                        == test.file_size)

        test.log.step("7. Close FTP profiles on DUT.")
        for profile in ftp_clients:
            test.expect(profile.dstl_get_service().dstl_close_service_profile())

    def define_ftp_profiles(test):
        ftp_client = []
        for profile_number in range(2):
            ftp_client.append(FtpProfile(test.dut, profile_number,
                                         test.connection_setup.dstl_get_used_cid(), command="get",
                                         alphabet="1", files=test.file_name))
            ftp_client[profile_number].dstl_set_parameters_from_ip_server(test.ftp_server)
            if profile_number == 1:
                ftp_client[profile_number].dstl_set_host(test.ftp_server.dstl_get_server_FQDN())
            ftp_client[profile_number].dstl_generate_address()
            test.expect(ftp_client[profile_number].dstl_get_service().dstl_load_profile())
        return ftp_client


if "__main__" == __name__:
    unicorn.main()
