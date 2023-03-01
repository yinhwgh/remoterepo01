# responsible dan.liu@thalesgroup.com
# location Dalian
# TC0107805.001
import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module

class Test(BaseTest):
    """
       TC0107805.001 - Resmed_eHealth_SendHealthData_NF
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        uc_init_module(test, 1)

    def run(test):
        test.cipher = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
        server_send_data = dstl_generate_data(1500)
        test.log.step("1. Run OpenSSL server with one cipher suite supported by module: {}.".
                      format(test.cipher))
        test.ssl_server = SslServer("IPv4", "socket_tls", test.cipher)
        ip_address = test.ssl_server.dstl_get_server_ip_address()
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)

        test.log.step("2. Load client certificate and server public certificate "
                      "(micCert.der) on module.")
        test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                                dstl_get_openssl_configuration_number())
        if test.certificates.dstl_count_uploaded_certificates() > 0:
            test.certificates.dstl_delete_all_uploaded_certificates()
        test.certificates.dstl_upload_openssl_certificates()

        test.log.step("3. Check if certificates are installed.")
        test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                    msg="Wrong amount of certificates installed")

        test.log.step("5. Define PDP context for Internet services.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())

        test.log.step("6. Activate Internet service connection.")
        test.expect(connection_setup.dstl_activate_internet_connection(),
                    msg="Could not activate PDP context")

        test.log.step("7. Define TCP socket client profile to openSSL server. "
                      "Use socktcps connection.")
        socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                       host=ip_address,
                                       port=test.ssl_server.dstl_get_server_port(),
                                       protocol="tcp", secure_connection=True, tcp_ot="90")
        socket_service.dstl_generate_address()
        test.expect(socket_service.dstl_get_service().dstl_load_profile())

        test.log.step("8. Enable Security Option of IP service (secopt parameter).")
        socket_service.dstl_set_secopt("1")
        test.expect(socket_service.dstl_get_service().dstl_write_secopt())

        test.log.step("9. Open socket profile.")
        test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
        test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.log.step('10. Check signal quality')
        test.expect(test.dut.at1.send_and_verify('at+csq', ".*OK.*"))
        test.log.step('11. Monitoring Serving Cell')
        test.expect(test.dut.at1.send_and_verify('at^smoni', ".*OK.*"))

        test.log.step("11. Client: Send data 1500 bytes *100.")
        test.expect(socket_service.dstl_get_service().dstl_send_sisw_command_and_data
                    (1500, repetitions=100))
        test.log.step('12. checks the connection status ')
        test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
            at_command=Command.SISI_WRITE) == ServiceState.UP.value)
        test.log.step("13. Close socket profile.")
        test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
            at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


if __name__ == "__main__":
    unicorn.main()
