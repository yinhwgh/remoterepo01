# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0010951.001, TC0010951.002

import string

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Check if the FTP server address parameter is handled correctly.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftp_server = FtpServer("IPv4", test, test.connection_setup.dstl_get_used_cid())
        test.is_port_closed = False
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_fqdn_address = test.ftp_server.dstl_get_server_FQDN()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file_name = "FtpServerAddress.txt"

    def run(test):
        test.log.step("1.1. Configure a valid FTP server IP address that is reachable")
        test.define_ftp_profile("put", test.ftp_ip_address)

        test.log.step("2.1. Try to get/put a file via FTP")
        data_length = 1500
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.ftp_client.dstl_get_service()
                    .dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(len(test.ftp_server.dstl_ftp_server_get_file(test.file_name)) == data_length)

        test.log.step("1.2. Configure a valid FTP server IP hostname that is reachable")
        test.define_ftp_profile("get", test.ftp_fqdn_address)

        test.log.step("2.2. Try to get/put a file via FTP")
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(len(test.ftp_client.dstl_get_service()
                        .dstl_read_return_data(data_length)) == data_length)
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("1.3. Configure a valid FTP server IP address that is not reachable")
        if test.ftp_server.standard_server:
            not_reachable_ip_address = "54.37.234.132"
        else:
            not_reachable_ip_address = test.ftp_ip_address
        test.is_port_closed = test.expect(test.ftp_server.dstl_server_close_port())
        test.define_ftp_profile("get", not_reachable_ip_address)

        test.log.step("2.3. Try to get/put a file via FTP")
        timeout_regex = ".*Connection timed out.*"
        test.open_close_not_reachable_ftp(timeout_regex)

        test.log.step("1.4. Configure a valid FTP server IP hostname that is not reachable")
        if test.ftp_server.standard_server:
            not_reachable_fqdn_address = "m2mtestserver4.testwro001.ovh"
        else:
            not_reachable_fqdn_address = test.ftp_fqdn_address
        test.define_ftp_profile("get", not_reachable_fqdn_address)

        test.log.step("2.4. Try to get/put a file via FTP")
        test.open_close_not_reachable_ftp(timeout_regex)

        test.log.step("1.5. Configure an invalid FTP server IP address (e.g. 256.1234.a.0)")
        invalid_ip = "256.1234.a.0"
        error_response = ".*CME ERROR.*"
        test.expect(test.dut.at1.send_and_verify("AT^SISS=0,address,\"{}\"".
                                                 format(invalid_ip), error_response))

        test.log.step("1.6. Configure an invalid FTP server hostname "
                      "(e.g. a hostname that exceeds the maximum allowed length)")
        invalid_hostname = "etwpmawosvhjamtfgbjbxhkeopemcmweokfpouiegcjequdzwmarpdedfxsrwrjrgy" \
                           "kpueifddetwpmawosvhjamtfgbjbxhkeopemcmweokfpouiegcjequdzwmarpdedfxs" \
                           "rwrjrgykpueifddxeufsqcqpkuiwwazsooujvoyrsepnuiqnveojzrllnbcpkkcwuv" \
                           "lvviuxbdpcjlkdwyldpviayxdkcatocakmswfmuxmhqvnhkefpokknqrsjgagkrdmg" \
                           "kjrofzjpkqvpenvlskkcxcromqvhcgpvgovegcbaiermzgzirwxjztaetwpmawosvh" \
                           "jamtfgbjbxhkeopemcmweokfpouiegcjequdzwmarpdedfxsrwrjrgykpueifddxe" \
                           "ufsqcqpkuiwwazsooujvoyrsepnuiqnveojzrllnbcpkkcwuvlvviuxbdpcjlkdwy" \
                           "ldpviayxdkcatocakmswfmuxmhqvnhkefpokknqrsjgagkrdmgkjrofzjpkqvpenv" \
                           "lskkcxcromqvhcgpvgovegcbaiermzgzirwxjzta.com"
        test.expect(test.dut.at1.send_and_verify("AT^SISS=0,\"address\",\"ftp://{}\"".
                                                 format(invalid_hostname), error_response))

        test.log.step("1.7. Configure a FTP server hostname that could not be resolved by the "
                      "DNS server.")
        test.define_ftp_profile("get", "notexistinghost098765.com")

        test.log.step("2.7. Try to get/put a file via FTP")
        host_not_found_regex = ".*Host not found.*"
        test.open_close_not_reachable_ftp(host_not_found_regex)

    def cleanup(test):
        if not test.is_port_closed:
            try:
                if not test.ftp_server.dstl_server_close_port():
                    test.log.warn("Problem during closing port on server.")
            except AttributeError:
                test.log.error("Object was not created.")
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file(test.file_name):
                test.log.warn("Problem with deleting file.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.ftp_client.dstl_get_service().dstl_close_service_profile()

    def define_ftp_profile(test, cmd, host):
        test.ftp_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                     command=cmd, host=host, port=test.ftp_port,
                                     user=test.ftp_server.dstl_get_ftp_server_user(),
                                     passwd=test.ftp_server.dstl_get_ftp_server_passwd(),
                                     alphabet="1", files=test.file_name)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())

    def open_close_not_reachable_ftp(test, regex):
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile(expected=regex,
                                                                                 timeout=90))
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())


if __name__ == "__main__":
    unicorn.main()
