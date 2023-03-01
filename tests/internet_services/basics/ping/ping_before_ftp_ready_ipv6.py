#responsible: lukasz.lidzba@globallogic.com
#location: Wroclaw
#TC0093651.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_register_to_network


class Test(BaseTest):
    """
    Testing ping host (FQDN and IP address) before service FTP is ready (after OK but before ^SIS: ).
    Perform for IPv6.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.step("1) Log on to the network.")
        test.expect(dstl_register_to_network(test.dut))

        test.log.step("2) Define and activate PDP context.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("3) Set FTP put service profile.")
        test.ftp_server = FtpServer("IPv6", test, cid)
        test.ftp_ip_address = test.ftp_server.dstl_get_server_ip_address()
        test.ftp_fqdn_address = test.ftp_server.dstl_get_server_FQDN()
        test.ftp_port = test.ftp_server.dstl_get_server_port()
        test.file_name = "PingBeforeFtpReady_IPv6.txt"
        test.ftp_put = FtpProfile(test.dut, 0, cid, command="put", alphabet="1", host=test.ftp_ip_address,
                                  port=test.ftp_port, files=test.file_name,
                                  user=test.ftp_server.dstl_get_ftp_server_user(),
                                  passwd=test.ftp_server.dstl_get_ftp_server_passwd())
        test.ftp_put.dstl_generate_address()
        test.expect(test.ftp_put.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open service profile and start ping FQDN address before service is ready.")
        test.log.step("4.1) Wait for OK")
        ping_execution = InternetServiceExecution(test.dut, cid)
        test.expect(test.ftp_put.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("4.2) Start ping with maximum available requests and timelimit")
        requests = 30
        time_limit = 10000
        test.expect(ping_execution.dstl_execute_ping(test.ftp_fqdn_address, request=requests, timelimit=time_limit,
                                                     expected_response="Ping.*OK.*SISW: 0,1",
                                                     check_packet_statistics=False))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.2)
        test.log.info("Checking if FTP service is ready - ^SISW: x,1 should appeared")
        test.expect(test.ftp_put.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4.3) Check service state.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("5) Close service profile.")
        test.expect(test.ftp_put.dstl_get_service().dstl_close_service_profile())

        test.log.step("6) Open service profile and start ping IP address before service is ready.")
        test.log.step("6.1) Wait for OK")
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        # load_and_activate_internet_connection_profile() added to slow down a little bit opening FTP service profile
        # and make ping before the service is ready
        test.expect(test.ftp_put.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("6.2) Start ping with maximum available requests and timelimit")
        test.expect(ping_execution.dstl_execute_ping(test.ftp_ip_address, request=requests, timelimit=time_limit,
                                                     expected_response="Ping.*OK.*SISW: 0,1",
                                                     check_packet_statistics=False))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= requests * 0.2)
        test.log.info("Checking if FTP service is ready - ^SISW: x,1 should appeared")
        test.expect(test.ftp_put.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6.3) Check service state.")
        test.expect(test.ftp_put.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("7) Close service profile.")
        test.expect(test.ftp_put.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_delete_file(test.file_name)
        except AttributeError:
            test.log.error("Object was not created.")


if __name__ == "__main__":
    unicorn.main()
