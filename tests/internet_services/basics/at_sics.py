#responsible grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0095689.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """ Check basic AT^SICS functionality """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.con_id = test.connection_setup.dstl_get_used_cid()
        test.ftp_server = FtpServer("IPv4", test, test.con_id)
        test.data_length = 100
        test.ftp_server.dstl_ftp_server_create_file("at_sics_test.txt", test.data_length)

    def run(test):
        test.log.h2("Executing script for test case: 'TC0095689.001 AtSics'")

        test.log.step("1. Define DNS servers addresses")
        dns_addresses = ['8.8.8.8', '8.8.4.4', '[2001:4860:4860::8888]', '[2001:4860:4860::8844]']
        test.define_dns_addresses(dns_addresses, dns_defined=True)

        test.log.step("2. Restart module")
        test.expect(dstl_restart(test.dut))

        test.log.step("3. Activate internet service")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4. Define and start FTP service with get command (use FQDN address)")
        test.ftp_client = FtpProfile(test.dut, "0", test.con_id, command="get", alphabet="1", files="at_sics_test.txt")
        test.ftp_client.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_client.dstl_set_host(test.ftp_server.dstl_get_server_FQDN())
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))

        test.log.step("5. Read some FTP data")
        test.expect(test.ftp_client.dstl_get_service().dstl_read_data(test.data_length))
        test.expect(test.ftp_client.dstl_get_service().dstl_get_confirmed_read_length() == test.data_length)

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file("at_sics_test.txt"):
                test.log.warn("Problem with deleting file.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("6. Close and delete service profile")
        try:
            test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.ftp_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("FTP profile object was not created.")

        test.log.step("7. Delete DNS servers addresses")
        dns_addresses = ['0.0.0.0', '0.0.0.0', '[]', '[]']
        test.define_dns_addresses(dns_addresses, dns_defined=False)

        test.log.step("8. Restart module")
        test.expect(dstl_restart(test.dut))

    def define_dns_addresses(test, dns_addresses, dns_defined):
        dns_dict = {'dns1': dns_addresses[0], 'dns2': dns_addresses[1],
                    'ipv6dns1': dns_addresses[2], 'ipv6dns2': dns_addresses[3]}
        for dns_name, dns_value in dns_dict.items():
            test.expect(test.dut.at1.send_and_verify('AT^SICS={},"{}","{}"'.format(test.con_id, dns_name, dns_value)))
        test.expect(test.dut.at1.send_and_verify('AT^SICS?'))
        if dns_defined:
            for dns_name, dns_value in dns_dict.items():
                test.expect('SICS: {},"{}","{}"'.format(test.con_id, dns_name, dns_value) in test.dut.at1.last_response)
        else:
            test.expect('SICS:' not in test.dut.at1.last_response)


if __name__ == "__main__":
    unicorn.main()
