#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0102304.001, TC0102304.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.certificates.internet_services_certificates import InternetServicesCertificates
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState

class Test(BaseTest):
    """
    Intention:
        To check FTPES function on Module. Correct communication starts out as plain FTP over port 21,
        but is upgraded to TLS/SSL encryption.
        This upgrade usually occurs before the user credentials are sent over the connection.

    description:
        1. Delete all certificates, from Module.
        2. Check that no certificates are present on Module.
        3. Attach Module to Network.
        4. Define FTPES "put" service profile to FTP server (secopt parameter = 1).
        5. Open defined profile.
        6. Check service and socket state using SISO command.
        7. Try to upload any file to FTP server (100 bytes).
        8. Check service and socket state using SISO command.
        9. Close FTP profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Executing script for test case: TC0102304.001/002 FTPES_NoCert")

        test.log.step("1. Delete all certificates, from Module.")
        test.certificates = InternetServicesCertificates(test.dut)
        if not test.certificates.dstl_count_uploaded_certificates() == 0:
            test.certificates.dstl_delete_all_certificates_using_ssecua()

        test.log.step("2. Check that no certificates are present on Module.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                    msg="Wrong amount of certificates installed")

        test.log.step("3. Attach Module to Network.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4. Define FTPES \"put\" service profile to FTP server (secopt parameter = 1)")
        test.ftpes_put = FtpProfile(test.dut, 0, connection_setup.dstl_get_used_cid(), command="put",
                                    files="test.txt", secopt="1", secure_connection=True, ftpes=True)
        test.ftpes_server = FtpServer("IPv4", test, connection_setup.dstl_get_used_cid())
        test.ftpes_put.dstl_set_parameters_from_ip_server(test.ftpes_server)
        test.ftpes_put.dstl_generate_address()
        test.expect(test.ftpes_put.dstl_get_service().dstl_load_profile())

        test.log.step("5. Open defined profile.")
        test.expect(test.ftpes_put.dstl_get_service().dstl_open_service_profile())
        test.expect(test.dut.at1.wait_for("The certificate does not exist"))

        test.log.step("6. Check service and socket state using SISO command.")
        check_service_and_socket_state(test)

        test.log.step("7. Try to upload any file to FTP server (100 bytes).")
        test.expect(not test.ftpes_put.dstl_get_service().dstl_send_sisw_command_and_data(100, eod_flag="1"))

        test.log.step("8. Check service and socket state using SISO command.")
        check_service_and_socket_state(test)

        test.log.step("9. Close FTP profile.")
        test.expect(test.ftpes_put.dstl_get_service().dstl_close_service_profile())


    def cleanup(test):
        try:
            if not test.ftpes_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftpes_server.dstl_ftp_server_delete_file("test.txt")
        except AttributeError:
            test.log.error("'ftpes_server' object was not created")


def check_service_and_socket_state(test):
    if test.dut.project == "SERVAL":
        test.log.info("According to the IPIS100314299 on Serval")
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value,
                    msg="Wrong service state")
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value,
                    msg="Wrong socket state")
    else:
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value,
                    msg="Wrong service state")
        test.expect(test.ftpes_put.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value,
                    msg="Wrong socket state")


if __name__ == "__main__":
    unicorn.main()
