# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0104389.003

import re
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Check if "secsni" parameter works as expected. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.info('=== According to TC Precondition: '
                      'Https server with support of SNI Extension ===\n'
                      '=== -> SslServer will be used ===')
        test.log.info('=== Run OpenSSL server with one cipher suite. ===')
        test.ssl_server = SslServer("IPv4", "http_tls", "TLS_RSA_WITH_AES_128_CBC_SHA256",
                                    extended=True)
        test.server_ip_address = test.ssl_server.dstl_get_server_ip_address()
        test.server_fqdn_address = test.ssl_server.dstl_get_server_FQDN()
        test.server_port = test.ssl_server.dstl_get_server_port()
        test.srv_id_0 = "0"
        test.log.info('=== Define PDP context and activate Internet service connection. ===')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.con_id = test.connection_setup.dstl_get_used_cid()
        test.timeout = 60

    def run(test):
        test.log.info('Executing script for test case: "TC0104389.003 secsniParameterCheck"')

        test.log.step('1. Create HTTPS post service profile '
                      '(do not set "secsni" parameter if 1 is a default value on tested product)')
        test.log.step('2. As address use FQDN name, secopt to 0.')
        test.http_service = HttpProfile(test.dut, test.srv_id_0, test.con_id, alphabet=1,
                                        secure_connection=True, ip_version="IPv4",
                                        http_command="post", secopt="0", hc_cont_len=100,
                                        host=test.server_fqdn_address, port=test.server_port)
        test.http_service.dstl_generate_address()
        test.expect(test.http_service.dstl_get_service().dstl_load_profile())

        test.log.step('3. Run Wireshark logs trace on server side.')
        test.log.info('=== TCPdump logging will be started in next step ===')

        test.log.step('4. Open service.')
        test.start_threads_and_open_service()

        test.log.step('5. Wait for successful connection open.')
        test.expect(test.http_service.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2200", '"Http connect.*'))

        test.log.step('6. Close connection.')
        test.close_connection_and_stop_threads()
        test.verify_ssh_server_logs("FQDN_address", is_sni=True)

        test.log.step('7. Set value of parameter "secsni" to "0"')
        test.set_and_check_secsni_settings("0")

        test.log.step('8. Open service.')
        test.start_threads_and_open_service()

        test.log.step('9. Wait for successful connection open.')
        test.expect(test.http_service.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2200", '"Http connect.*'))

        test.log.step('10. Close connection.')
        test.close_connection_and_stop_threads()
        test.verify_ssh_server_logs("FQDN_address")

        test.log.step('11. Change address parameter and use IP address.')
        test.http_service.dstl_set_host(test.server_ip_address)
        test.http_service.dstl_set_port(test.server_port)
        test.http_service.dstl_generate_address()
        test.http_service.dstl_get_service().dstl_write_address()
        dstl_check_siss_read_response(test.dut, [test.http_service])

        test.log.step('12. Open service.')
        test.start_threads_and_open_service()

        test.log.step('13. Wait for successful connection open.')
        test.expect(test.http_service.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2200", '"Http connect.*'))

        test.log.step('14. Close connection.')
        test.close_connection_and_stop_threads()
        test.verify_ssh_server_logs("IP_address")

        test.log.step('15. Set value of parameter "secsni" to "1"')
        test.set_and_check_secsni_settings("1")

        test.log.step('16. Open service.')
        test.start_threads_and_open_service()
        test.sleep(10)
        test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.log.step('17. Close connection, clear service profiles.')
        test.close_connection_and_stop_threads()
        test.verify_ssh_server_logs("IP_address", is_sni=True)
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

        test.log.step('18. Stop Wireshark trace tool and check logs.')
        test.log.info('=== TCPDUMP / Wireshark logs verified at every steps "Close Connection" ===')
        test.log.info('=== (Steps: 6, 10, 14, 17) ===')

        try:
            test.ssl_server_thread.join()
            test.ssh_server2_thread.join()
        except AttributeError:
            test.log.error("Problem with join thread.")
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

    def start_threads_and_open_service(test):
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(5)
        test.log.info('Activate TCPDUMP / Wireshark logs')
        test.ssh_server2 = test.ssh_server.clone()  # to run 2 threads in parallel
        test.ssh_server2_thread = test.thread(test.ssh_server2.send_and_receive,
             f"sudo timeout {test.timeout} tcpdump dst port {test.server_port} -A -i ens3 -vv")
        test.sleep(5)
        test.expect(test.http_service.dstl_get_service().dstl_open_service_profile())

    def close_connection_and_stop_threads(test):
        test.expect(test.http_service.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.ssh_server2_thread.join()
        test.sleep(10)

    def verify_ssh_server_logs(test, address, is_sni=False):
        test.log.info('=== Checking the TCPdump log for address occurrence in '
                      '"Client Hello" message ===')
        if is_sni:
            if address == "FQDN_address":
                test.log.info(f"Server Name Indication should be FOUND in TCPdump (network) log"
                              f"- address as FQDN: ...{test.server_fqdn_address}")
                test.expect(re.search(f"\.\.\.{test.server_fqdn_address}",
                                      test.ssh_server2.last_response))
            else:
                test.log.info(f"Server Name Indication should be FOUND in TCPdump (network) log"
                              f"- address as IP: ...{test.server_ip_address}")
                test.expect(re.search(f"\.\.\.{test.server_ip_address}",
                                      test.ssh_server2.last_response))
        else:
            if address == "FQDN_address":
                test.log.info(f"Server Name Indication should be NOT FOUND in TCPdump (network) log"
                              f"- address as FQDN: ...{test.server_fqdn_address}")
                test.expect(not re.search(f"\.\.\.{test.server_fqdn_address}",
                                          test.ssh_server2.last_response))
            else:
                test.log.info(f"Server Name Indication should be NOT FOUND in TCPdump (network) log"
                              f"- address as IP: ...{test.server_ip_address}")
                test.expect(not re.search(f"\.\.\.{test.server_ip_address}",
                                          test.ssh_server2.last_response))

    def set_and_check_secsni_settings(test, secsni_value):
        test.http_service.dstl_set_secsni(secsni_value)
        test.http_service.dstl_get_service().dstl_write_secsni()
        dstl_check_siss_read_response(test.dut, [test.http_service])


if "__main__" == __name__:
    unicorn.main()