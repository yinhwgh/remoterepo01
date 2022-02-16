# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107798.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import NF_pre_config
from core import dstl
rethread = False


class Test(BaseTest):
    """
     TC0107798.001-Resmed_eHealth_DownloadFile_ExceptionalFlow_A
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        uc_init_module(test, 1)

    def run(test):
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 1.")
        main_process(test, 1)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 2.")
        main_process(test, 2)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        global rethread
        rethread = True
        test.log.step("Begin exceptional_flow step 3.")
        main_process(test, 3)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 4.")
        main_process(test, 4)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 5.")
        main_process(test, 5)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 6.")
        main_process(test, 6)
        test.ssh_server.close()
        test.sleep(10)
        NF_pre_config(test)
        test.log.step("Begin exceptional_flow step 7.")
        main_process(test, 7)

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

def dstl_compare_cipher_suite_without_error(test, data_read_from_server=""):
    """Method compares cypher suite used on server with cypher suite defined as expected (in OpenSLL format).
    Args:
        data_read_from_server: output form server read using AT^SISR command (optional - needed only for HTTPS)
    Returns:
        Method returns 'True' in case comparison was successful and 'False' – otherwise.
    responsible grzegorz.dziublinski@globallogic.com
    location Wroclaw
    """
    dstl.log.h2("DSTL execute: 'dstl_compare_cipher_suite'.")
    cipher_match = ""
    if "http_tls" in test.ssl_server.ssl_protocol:
        cipher_match = "Cipher is "
    elif "socket_tls" in test.ssl_server.ssl_protocol:
        cipher_match = "CIPHER is "
    elif "dtls" in test.ssl_server.ssl_protocol:
        cipher_match = "Ciphersuite: "
    server_response = dstl.test.ssh_server.last_response
    if len(data_read_from_server) > 0:
        server_response_with_cipher = data_read_from_server
    else:
        server_response_with_cipher = server_response
    try:
        cipher_suite = server_response_with_cipher.split(cipher_match)[1].split("\n")[0]
    except IndexError:
        dstl.log.warning("'{}' not found in server response. Cipher name cannot be taken from server response."
                         .format(cipher_match))
        return False
    dstl.log.info("Cipher detected from OpenSSL server answer: {}".format(cipher_suite))
    dstl.log.info("Cipher defined by test script/test case: {}".format(test.ssl_server.openssl_cipher_name))
    return cipher_suite == test.ssl_server.openssl_cipher_name

def EF_Soft_reset(test, checkstep, restart):
    if checkstep == restart:
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        main_process(test)
        return True
    else:
        return False

def main_process(test, restart=0):
    test.log.step("1. Configures the IP service connection profile 0 "
                  "with an inactive timeout set to 90 seconds and a private APN using AT^SICS.")
    server_send_data = dstl_generate_data(1500)
    connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(connection_setup.dstl_load_internet_connection_profile())
    test.expect(connection_setup.dstl_activate_internet_connection(),
                msg="Could not activate PDP context")
    socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                   host=test.ip_address,
                                   port=test.port_number,
                                   protocol="tcp", secure_connection=True, tcp_ot="90")
    socket_service.dstl_generate_address()
    test.expect(socket_service.dstl_get_service().dstl_load_profile())
    if EF_Soft_reset(test, 1, restart):
        return True

    test.log.step("2.  Closes the internet service profile (ID 0) and configures this service profile "
                  "as a secure TCP socket in non-transparent mode (server authentication only)")
    socket_service.dstl_set_secopt("1")
    test.expect(socket_service.dstl_get_service().dstl_write_secopt())
    if EF_Soft_reset(test, 2, restart):
        return True

    test.log.step("3. Open socket profile.")
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', handle_errors=True)
    test.sleep(5)
    if rethread and restart == 0:
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(20)
    test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
    test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
    if EF_Soft_reset(test, 3, restart):
        return True

    test.log.step('4. Server send 1500 data ')
    test.log.info('Server send 1500 data*10 ')
    for i in range(10):
        test.ssl_server.dstl_send_data_from_ssh_server(data=server_send_data, ssh_server_property='ssh_server')
        test.sleep(1)
    if EF_Soft_reset(test, 4, restart):
        return True

    test.log.step("5. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks.")
    for i in range(10):
        test.expect(socket_service.dstl_get_service().dstl_read_data
                    (req_read_length=1500, repetitions=1))
        test.sleep(1)
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.UP.value)
    if EF_Soft_reset(test, 5, restart):
        return True

    test.log.step("6. Closes internet service profile after the successful download of the file.")
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
    if EF_Soft_reset(test, 6, restart):
        return True

    test.log.step("7. Checks the file integrity with a SHA256 hash.")
    test.expect(dstl_compare_cipher_suite_without_error(test), msg="Incorrect server response!")
    if EF_Soft_reset(test, 7, restart):
        return True

if __name__ == "__main__":
    unicorn.main()
