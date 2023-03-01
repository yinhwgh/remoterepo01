#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0012050.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Check the <ackData> and <unackData counter> for FTP
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file_name = "FtpAckCounter.txt"
        test.data_length = 1500

    def run(test):
        test.log.step("1. Configure an IP connection profile or PDP context and activate it.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("2. Configure a Ftp put service profile.")
        test.ftp_put = FtpProfile(test.dut, 0, cid, command="put", alphabet="1", host=test.ftp_ip_address,
                                  port=test.ftp_port, files=test.file_name,
                                  user=test.ftp_server.dstl_get_ftp_server_user(),
                                  passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_put.dstl_generate_address()
        test.expect(test.ftp_put.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open the service profile.")
        test.expect(test.ftp_put.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_put.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Send some data.")
        test.expect(test.ftp_put.dstl_get_service().dstl_send_sisw_command_and_data(test.data_length))
        test.sleep(5)

        test.log.step("5. Block the IP traffic by activating a firewall or using a shield box.")
        dut_ip_addresses = test.connection_setup.dstl_get_pdp_address()
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_addresses[0]))

        test.log.step("6. Check the <ackData> and <unackData> conter by calling at^sisi.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_ack_data() == test.data_length)
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_unack_data() == 0)

        test.log.step("7. Send some data.")
        test.expect(test.ftp_put.dstl_get_service().dstl_send_sisw_command_and_data(test.data_length,
                                                                eod_flag='1', skip_data_check=True))

        test.log.step("8. Check the <ackData> and <unackData> conter by calling at^sisi.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_ack_data() == test.data_length)
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_unack_data() == test.data_length)

        test.log.step("9. Enable IP traffic (deactivate firewall or remove shield box).")
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

        test.log.step("10. Wait until session state is \"down\".")
        test.expect(test.ftp_put.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("11. Check the <ackData> and <unackData> conter by calling at^sisi.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_ack_data() == test.ftp_put.dstl_get_parser().
                    dstl_get_service_data_counter("tx"))
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_unack_data() == 0)

        test.log.step("12. Close session.")
        test.expect(test.ftp_put.dstl_get_service().dstl_close_service_profile())

        test.log.step("13. Check the <ackData> and <unackData> conter by calling at^sisi.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_ack_data() == 0)
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_unack_data() == 0)

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_clean_up_directories()
        except AttributeError:
            test.log.error("Object was not created.")
        test.expect(test.ftp_put.dstl_get_service().dstl_close_service_profile())


if __name__ == "__main__":
    unicorn.main()
