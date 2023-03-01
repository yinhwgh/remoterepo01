# responsible: feng.han@thalesgroup.com
# location: Dalian
# TC0107813.001


import unicorn
import time
import re
from core.basetest import BaseTest
import dstl.auxiliary.devboard.devboard
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from dstl.serial_interface.serial_interface_flow_control import dstl_check_flow_control_number_after_set
from dstl.serial_interface.config_baudrate import dstl_get_supported_max_baudrate, dstl_set_baudrate, \
    dstl_get_supported_baudrate_list
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_adjust_clock_normal_flow
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import resmed_ehealth_initmodule_normal_flow
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module

restart_cuunter = 1  # Restart counter to make the script stop
run_all = False  # False for normal flow,which does not need retry.
re_init = False  # if re_init is Ture,do not continue with normal flow after re-init


class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        uc_init_module(test, 1)

    def run(test):
        main_process(test)

    def cleanup(test):
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.log.info("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


def main_process(test):
    test.cipher = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    test.ssl_server = SslServer("IPv4", "socket_tls", test.cipher)
    ip_address = test.ssl_server.dstl_get_server_ip_address()
    test.log.info("Load client certificate and server public certificate "
                  "(micCert.der) on module.")
    test.certificates = OpenSslCertificates(test.dut, test.ssl_server.
                                            dstl_get_openssl_configuration_number())
    if test.certificates.dstl_count_uploaded_certificates() > 0:
        test.certificates.dstl_delete_all_uploaded_certificates()
    test.certificates.dstl_upload_openssl_certificates()
    test.log.info("Check if certificates are installed.")
    test.expect(test.certificates.dstl_count_uploaded_certificates() >= 2,
                msg="Wrong amount of certificates installed")

    test.log.step(
        '1. Configures the IP service connection profile 0 with an inactive timeout set to 90 seconds and a private APN using ')
    connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=1,IP,internet4g.gdsp", ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify("AT^SICA=1,1", ".*OK.*"))
    test.log.step(
        '2. Closes the internet service profile (ID 0) and configures this service profile as a secure TCP socket in non-transparent mode (server authentication only) ')
    socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                   host=ip_address,
                                   port=test.ssl_server.dstl_get_server_port(),
                                   protocol="tcp", secure_connection=True, tcp_ot="90")
    socket_service.dstl_generate_address()
    test.expect(socket_service.dstl_get_service().dstl_load_profile())
    socket_service.dstl_set_secopt("1")
    test.expect(socket_service.dstl_get_service().dstl_write_secopt())
    test.expect(test.dut.at1.send_and_verify("at^siss=0,conid,1", ".*OK.*"))
    # ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
    # test.sleep(10)
    for i in range(100):
        test.log.info("begin loop {} times".format(i))
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(60)
        test.log.step('3. Opens the internet service and waits for SISR URC.')
        test.expect(socket_service.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        test.log.step('4. Server sends the requested file to the module.')
        for i in range(10):
            server_send_data = dstl_generate_data(1500)
            test.ssl_server.dstl_send_data_from_ssh_server(data=server_send_data, ssh_server_property='ssh_server')
        test.expect(socket_service.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.log.step(
            '5. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks stores it temporarily on the application processor memory andÂ  checks the connection status with AT^SISI=0 in between.')
        for i in range(10):
            test.expect(socket_service.dstl_get_service().dstl_read_data(1500))
        test.expect(test.dut.at1.send_and_verify('at^sisi=0', ".*SISI: 0,4,15000,0,0.*"))
        test.log.step('6. Closes internet service profile after the successful download of the file.')
        test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
        test.sleep(10)

if "__main__" == __name__:
    unicorn.main()
