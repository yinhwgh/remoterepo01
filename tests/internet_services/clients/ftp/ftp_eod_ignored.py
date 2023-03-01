#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0012051.001, TC0012051.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Check that endOfData flag is ignored, if <cnfWritelength> != <reqWriteLength>.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Executing script for test case: 'TC0012051.001/002 FtpEodIgnored'")

        test.log.step("1. Configure a connection profile.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.dut_addresses = test.connection_setup.dstl_get_pdp_address()

        test.log.step("2. Configure and open a Ftp put service profile.")
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.file_name = "FtpEodIgnored.txt"
        test.ftp_client = FtpProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), alphabet="1",
                                     command="put", files=test.file_name)
        test.ftp_client.dstl_set_parameters_from_ip_server(ip_server=test.ftp_server)
        test.ftp_client.dstl_generate_address()
        test.expect(test.ftp_client.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("3. Block the IP traffic by a activating firewall or using a shield box.")
        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(test.dut_addresses[0]))

        test.log.step("4. Send data until the internal buffer is full (<cnfWriteLength> = 0).")
        data_length = 1500
        previous_unack_value = None
        is_buffer_not_overflowed = True
        while is_buffer_not_overflowed:
            test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command(data_length))
            if test.ftp_client.dstl_get_service().dstl_get_confirmed_write_length() == 0:
                break
            current_unack_value = test.ftp_client.dstl_get_service().dstl_get_unacknowledged_data()
            if current_unack_value == previous_unack_value:
                test.expect(test.ftp_client.dstl_get_service().dstl_send_data(dstl_generate_data(data_length)))
                test.log.info("<unackData> value is exactly the same as in previous loop despite the incoming traffic "
                              "is blocked and data was sent. Sending further data is interrupted.")
                break
            previous_unack_value = current_unack_value
            test.expect(test.ftp_client.dstl_get_service().dstl_send_data(dstl_generate_data(data_length)))
            test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("5. Try to send data and set eodFlag. ")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command(data_length, eod_flag="1", expected="OK"))

        test.log.step("6. Allow IP traffic by deactivating the firewall.")
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

        for i in range(20):
            test.sleep(5)
            if test.ftp_client.dstl_get_parser().dstl_get_service_ack_data(Command.SISI_WRITE) > 0:
                break

        test.log.step("7. Check the IP State and the <ackData> and <unackData> counter.")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_ack_data() > 0)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_unack_data() == 0)

        test.log.step("8. Send data and set the eod flag.")
        test.expect(test.ftp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_length, eod_flag="1"))
        test.expect(test.ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("9. Check the IP Sate and the <ackData> and <unackData> counter.")
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_ack_data() > 0)
        test.expect(test.ftp_client.dstl_get_parser().dstl_get_service_unack_data() == 0)

        test.log.step("10. Close the Ftp service.")
        test.expect(test.ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_clean_up_directories()
        except AttributeError:
            test.log.error("Object was not created.")
        test.ftp_client.dstl_get_service().dstl_close_service_profile()
        test.ftp_client.dstl_get_service().dstl_reset_service_profile()


if __name__ == "__main__":
    unicorn.main()
