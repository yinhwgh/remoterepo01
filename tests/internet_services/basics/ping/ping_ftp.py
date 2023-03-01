#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0024331.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile

class Test(BaseTest):
    """Check the ping functionality during an FTP session"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")



    def run(test):
        data_50 = 50
        srv_id = "0"
        request_10 = 10
        request_30 = 30
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.ftp_server = FtpServer("IPv4", test, connection_setup.dstl_get_used_cid())

        test.log.step("1. Configure a FTP service profile")
        ftp_client = FtpProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(), command="put",
                                ip_server=test.ftp_server, files="test.txt", alphabet="1")
        ftp_client.dstl_set_parameters_from_ip_server()
        ftp_client.dstl_generate_address()
        test.expect(ftp_client.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open the FTP service")
        test.expect(ftp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("3. Write some data ")
        test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command(data_50))
        test.expect(ftp_client.dstl_get_service().dstl_send_data(dstl_generate_data(data_50)))

        test.log.step("4. Call ping command with number of requests =10")
        ping_execution = InternetServiceExecution(test.dut, connection_setup.dstl_get_used_cid())
        test.expect(ping_execution.dstl_execute_ping(test.ftp_server.dstl_get_server_ip_address(), request_10))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= request_10 * 0.2)

        test.log.step("5. After ping command is finished, write some data with set eodFlag")
        test.expect(ftp_client.dstl_get_service().dstl_send_sisw_command(data_50, 1))
        test.expect(ftp_client.dstl_get_service().dstl_send_data(dstl_generate_data(data_50)))
        test.expect(ftp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("6. Call ping command with number of requests = 30")
        test.expect(ping_execution.dstl_execute_ping(test.ftp_server.dstl_get_server_ip_address(), request_30))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= request_30 * 0.2)

        test.log.step("7. Close the FTP service")
        test.expect(ftp_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")

        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()