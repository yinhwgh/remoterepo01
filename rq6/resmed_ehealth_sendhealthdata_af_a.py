# responsible dan.liu@thalesgroup.com
# location Dalian
# TC0107851.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
import resmed_ehealth_initmodule_normal_flow
from core import dstl
from core.interface import decode_text
from ssh2.exceptions import Timeout
import logging
import re

log = logging.getLogger("aux")


class Test(BaseTest):
    """
       TC0107851.001 - Resmed_eHealth_SendHealthData_AF_A
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.dut.devboard.send_and_verify('mc:urc=off', "OK")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def run(test):
        main_process(test)

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


def kill_ssh_process(test, ssh_server_property, process_name, indexes_to_kill=[0]):
    dstl.log.h2("DSTL execute: 'dstl_direct_kill_ssh_process'.")
    if not test.ssl_server.standard_server:
        if not process_name:
            return
        test.ssl_server.ssh_server_property_name = ssh_server_property
        ssh_server = eval("dstl.test.{}".format(test.ssl_server.ssh_server_property_name))
        # ssh_server.send_and_receive('ps -aux | grep "{}"'.format(process_name))

        command = 'ps -aux | grep "{}"'.format(process_name)
        timeout = 0
        if timeout != 0:
            ssh_server.session.set_timeout(timeout * 1000)
        ssh_server.send(command, sudo=False, silent=None)

        ssh_server.last_response = ""
        ssh_server.last_retcode = -1
        line_id = 0
        while True:
            try:
                print('-------------', ssh_server._shell_channel, '------------------')
                size, buff = ssh_server._shell_channel.read()
                ssh_server.last_response += decode_text(buff)
            except Timeout:
                log.error("{}. Timeout occurred when reading from channel.".format(ssh_server.name))
                break
            except Exception as ex:
                log.error("{}. Exception occurred when reading from channel. {}".format(ssh_server.name, ex))
                break
            lines = ssh_server.last_response.splitlines()
            while len(lines) > line_id + 1:
                if line_id != len(lines) - 2 or lines[line_id]:
                    ssh_server.log_receive(lines[line_id])
                line_id += 1
            try:
                if lines[-1].endswith(ssh_server._end_of_command):
                    try:
                        ssh_server.last_response = ssh_server.last_response.replace(ssh_server._end_of_command,
                                                                                    "").rstrip()
                    except Exception as ex:
                        log.warning("{}. Unexpected error while cleaning last_response message".format(ssh_server.name))
                        log.debug(ex, exc_info=True)
                    try:
                        last_line = ssh_server.last_response[ssh_server.last_response.rfind('\n'):].strip()
                    except Exception as ex:
                        ssh_server.log.warning(ex)
                        log.debug(ex, exc_info=True)
                        break
                    try:
                        ssh_server.last_retcode = int(re.match(r"(\d+)$", last_line).group(1))
                    except Exception as ex:
                        try:
                            ssh_server.last_retcode = int(re.search(r"(\d+)$", last_line).group(1))
                        except Exception as ex:
                            log.warning("{}. Return code was not detected in {}".format(ssh_server.name, last_line))
                            ssh_server.last_retcode = -1
                    try:
                        ssh_server.last_response = ssh_server.last_response[:ssh_server.last_response.rfind('\n')]
                    except Exception as ex:
                        log.debug(ex, exc_info=True)
                    break
            except IndexError as ex:
                log.debug("{}. last_response buffer is empty".format(ssh_server.name))
                break
        ssh_server.session.set_timeout(ssh_server.timeout)

        server_response = ssh_server.last_response.split('\n')
        try:
            for index in indexes_to_kill:
                if 'grep' in server_response[index]:
                    dstl.log.info('No maching process found.')
                else:
                    process_id = server_response[index].replace('  ', ' ').replace('  ', ' ').split(' ')[1]
                    ssh_server.send_and_receive('sudo kill {}'.format(process_id))
        except IndexError:
            dstl.log.warn('Incorrect response - cannot parse process ID.')
    else:
        dstl.expect(False, msg="Extended IpServer is required for execution of this method.", critical=True)


def main_process(test):
    test.cipher = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
    server_send_data = dstl_generate_data(1500)
    test.log.step("1. Run OpenSSL server with one cipher suite supported by module: {}.".
                  format(test.cipher))
    test.ssl_server = SslServer("IPv4", "socket_tls", test.cipher)
    ip_address = test.ssl_server.dstl_get_server_ip_address()
    ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
    test.sleep(30)
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

    test.log.step("4. Set Real Time Clock to current time.")
    test.expect(dstl_set_real_time_clock(test.dut))

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
    test.log.step('12.sends health data (~100k-1MByte) to the receiving server in 1500Bytes chunks ')
    test.expect(socket_service.dstl_get_service().dstl_send_sisw_command(req_write_length=1500))
    partial_send_data = dstl_generate_data(1500)
    test.expect(socket_service.dstl_get_service().dstl_send_data(data=partial_send_data))
    test.expect(test.dut.at1.send_and_verify('AT^SISC=0', 'OK\r\n', timeout=5, handle_errors=True))
    socket_service.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_WRITE)
    test.log.step('13.Stop the TCPS server')
    test.ssl_server.dstl_kill_ssh_process(ssh_server_property="ssh_server", process_name='openssl-1.0')
    # kill_ssh_process(test, ssh_server_property="ssh_server", process_name='openssl-1.0')
    test.log.step('14. checks the connection status ')
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISI_WRITE) == ServiceState.ALLOCATED.value)
    test.log.step('15. closes the internet service profile')
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.log.step('16. Start the TCPS server')
    test.thread(test.ssl_server.dstl_run_ssl_server)
    test.sleep(10)
    test.log.step('17. opens the internet service, waits for SISW URC')
    test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
    test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
    test.log.step('18. .Check signal quality')
    test.expect(test.dut.at1.send_and_verify('at+csq', ".*OK.*"))
    test.log.step('19. Monitoring Serving Cell')
    test.expect(test.dut.at1.send_and_verify('at^smoni', ".*OK.*"))
    test.log.step("20. Client: Send data 1500 bytes *100.")
    test.expect(socket_service.dstl_get_service().dstl_send_sisw_command_and_data(1500, repetitions=10))
    test.log.step('21. checks the connection status ')
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISI_WRITE) == ServiceState.UP.value)
    test.log.step("22. Close socket profile.")
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)


if __name__ == "__main__":
    unicorn.main()
