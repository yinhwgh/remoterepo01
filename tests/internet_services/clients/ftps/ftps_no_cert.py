#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0103544.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ftps_server import FtpsServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        data_100 = 100

        test.log.info("TC0103544.001 - FTPS_NoCert")
        test.log.step("1) Delete all certificates, from Module.")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            for index in range(11):
                test.certificates.dstl_delete_certificate(index)

        test.log.step("2) Check that no certificates are present on Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

        test.log.step("3) Attach Module to Network.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4) Define FTPS \"put\" service profile to FTP server (secopt parameter = 1).")
        test.ftps_service = FtpProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(), command="put",
                                      files="test.txt", secopt=1, secure_connection=True)
        test.ftps_server = FtpsServer("IPv4", test, connection_setup_object.dstl_get_used_cid())
        test.ftps_service.dstl_set_parameters_from_ip_server(test.ftps_server)
        test.ftps_service.dstl_generate_address()
        test.expect(test.ftps_service.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open defined profile.")
        test.expect(test.ftps_service.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.ftps_service.dstl_get_urc().dstl_is_sis_urc_appeared("0", "77",
                                                                              "The certificate does not exist"))

        test.log.step("6) Check service and socket state using SISO command.")
        if test.dut.project == "SERVAL":
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)
        else:
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("7) Try to upload any file to FTP server (100 bytes).")
        if test.dut.project == "SERVAL":
            test.expect(not test.ftps_service.dstl_get_service().dstl_send_sisw_command_and_data(data_100))
        else:
            test.expect(test.ftps_service.dstl_get_service().dstl_send_sisw_command_and_data(data_100))

        test.log.step("8) Check service and socket state using SISO command.")
        if test.dut.project == "SERVAL":
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)
        else:
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            test.expect(test.ftps_service.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("9) Close FTP profile.")
        test.expect(test.ftps_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftps_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with cleaning directories.")
            if not test.ftps_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
