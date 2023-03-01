#responsible grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0012053.001, TC0012053.002
import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):
    """Short description:
       Check that endOfData flag is not ignored, if <reqWriteLength> equals 0.

       Detailed description:
       1. Configure a connection profile.
       2. Configure and open a Ftp put service profile.
       3. Send some data.
       4. Call at^sisw=x,0,1.
       5. Check IP state (at^sisi).
       6. Try to send some data.
       7. Close service profile.
       """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

    def run(test):
        data_50 = 50
        srv_id = 0

        test.log.info("TC0012053.001/002 - FtpEodReqLength0")
        test.log.step("1) Configure a connection profile.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())
        dut_ip_address = connection_setup_object.dstl_get_pdp_address()[0]
        test.log.info("IP address: {}".format(dut_ip_address))

        test.log.step("2) Configure and open a Ftp put service profile.")
        test.ftp_service = FtpProfile(test.dut, srv_id, connection_setup_object.dstl_get_used_cid(), alphabet="1",
                                      command="put", files="test.txt")
        test.ftp_server = FtpServer("IPv4", extended=True)
        test.ftp_service.dstl_set_parameters_from_ip_server(test.ftp_server)
        test.ftp_service.dstl_generate_address()
        test.expect(test.ftp_service.dstl_get_service().dstl_load_profile())
        test.expect(test.ftp_service.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftp_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("3) Send some data.")
        test.expect(test.ftp_service.dstl_get_service().dstl_send_sisw_command_and_data(data_50))

        test.expect(test.ftp_server.dstl_server_block_incoming_traffic(dut_ip_address))

        test.log.step("4) Call at^sisw=x,0,1.")
        test.expect(test.ftp_service.dstl_get_service().dstl_send_sisw_command(0, eod_flag='1'))

        test.log.step("5) Check IP state (at^sisi).")
        test.expect(test.ftp_service.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE) ==
                    ServiceState.CLOSING.value)
        test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())
        test.expect(test.ftp_service.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.expect(test.ftp_service.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE) ==
                    ServiceState.DOWN.value)

        test.log.step("6) Try to send some data.")
        test.expect(test.ftp_service.dstl_get_service().dstl_send_sisw_command(data_50, expected="ERROR"))

        test.log.step("7. Close service profile.")
        test.expect(test.ftp_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")
        test.ftp_service.dstl_get_service().dstl_close_service_profile()
        test.ftp_service.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
