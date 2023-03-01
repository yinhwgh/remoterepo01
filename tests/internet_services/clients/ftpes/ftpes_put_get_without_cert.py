#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0102312.001, TC0102312.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.ftpes_server import FtpesServer
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
        data_1024 = 1024

        test.log.info("TC0102312.001/002 - FTPES_PutGet_WithoutCert")
        test.log.step("1) Delete all certificates, from Module.")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.log.step("2) Check that no certificates are present on Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0)

        test.log.step("3) Attach Module to Network.")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4) Define FTPES \"put\" service profile to FTP server (secopt parameter = 0).")
        test.ftpes_put = FtpProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(), command="put",
                                    alphabet='1', files="test.txt", secopt="0", secure_connection=True, ftpes=True)
        test.ftpes_server = FtpesServer("IPv4", test, connection_setup_object.dstl_get_used_cid())
        test.ftpes_put.dstl_set_parameters_from_ip_server(test.ftpes_server)
        test.ftpes_put.dstl_generate_address()
        test.expect(test.ftpes_put.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open defined profile. Check in URCs if encryption is used while connection.")
        test.expect(test.ftpes_put.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftpes_put.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="200",
                                                                        urc_info_text=".*openFtpData with TLS DATA.*"))
        test.expect(test.ftpes_put.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6) Check service and socket state using SISO command.")
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("7) Try to upload any file to FTP server (1 KB).")
        test.expect(test.ftpes_put.dstl_get_service().dstl_send_sisw_command_and_data(data_1024, eod_flag="1"))

        test.log.step("8) Check service and socket state using SISO command.")
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("9) Close FTP put profile.")
        test.expect(test.ftpes_put.dstl_get_service().dstl_close_service_profile())

        test.log.step("10) Define FTPES \"get\" service profile to FTP server (same file that was uploaded in step 7).")
        test.ftpes_get = FtpProfile(test.dut, 1, connection_setup_object.dstl_get_used_cid(), command="get",
                                    alphabet='1', files="test.txt", secopt="0", secure_connection=True, ftpes=True)
        test.ftpes_get.dstl_set_parameters_from_ip_server(test.ftpes_server)
        test.ftpes_get.dstl_generate_address()
        test.expect(test.ftpes_get.dstl_get_service().dstl_load_profile())

        test.log.step("11) Open defined profile. Check in URCs if encryption is used while connection.")
        test.expect(test.ftpes_get.dstl_get_service().dstl_open_service_profile())
        test.expect(test.ftpes_get.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", urc_info_id="200",
                                                                        urc_info_text=".*openFtpData with TLS DATA.*"))
        test.expect(test.ftpes_get.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("12) Check service and socket state using SISO command.")
        test.expect(test.ftpes_get.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.ftpes_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("13) Download whole file from FTP server (wait for proper URC after downloading file).")
        test.expect(test.ftpes_get.dstl_get_service().dstl_read_data(data_1024))
        test.expect(test.ftpes_get.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))

        test.log.step("14) Check service and socket state using SISO command.")
        test.expect(test.ftpes_get.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.ftpes_get.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

        test.log.step("15) Close FTP get profile.")
        test.expect(test.ftpes_get.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.ftpes_server.dstl_ftp_server_delete_file("test.txt"):
                test.log.warn("Problem with deleting file.")
            if not test.ftpes_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("'ftpes_server' object was not created")
        test.ftpes_put.dstl_get_service().dstl_close_service_profile()
        test.ftpes_put.dstl_get_service().dstl_reset_service_profile()
        test.ftpes_get.dstl_get_service().dstl_close_service_profile()
        test.ftpes_get.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
