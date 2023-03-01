# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0105123.001, TC0105123.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       TC intention: to check support of DH parameter 2048 long.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.step("1. run SSL server with DH parameter 2048 long "
                      "(-dhparam [numbits] for OpenSSL) and ciphersuite "
                      "set for for any DH cipher.")
        test.ssl_server = SslServer("IPv4", "socket_tls", "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384")

        test.log.step("2. on DUT configure tcp client to server")
        test.profile = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(),
                                     protocol="tcp",
                                     host=test.ssl_server.dstl_get_server_ip_address(), secopt="0",
                                     port=test.ssl_server.dstl_get_server_port(),
                                     secure_connection=True)
        test.profile.dstl_generate_address()
        test.expect(test.profile.dstl_get_service().dstl_load_profile())
        test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server,
                                             configuration="DH")
        test.sleep(3)

        test.log.step("3. on DUT open client and exchange data")
        test.expect(test.profile.dstl_get_service().dstl_open_service_profile())
        test.expect(test.profile.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
        data_to_send_from_client = dstl_generate_data(100)
        if test.expect(test.profile.dstl_get_service().dstl_send_sisw_command(100)):
            test.expect(test.profile.dstl_get_service().dstl_send_data(data_to_send_from_client))
        test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
        test.ssl_server_thread.join()
        test.expect(data_to_send_from_client in test.ssh_server.last_response)
        test.expect(test.ssl_server.dstl_compare_cipher_suite(), msg="Incorrect server response!")

    def cleanup(test):
        test.log.step("4. close all connections, remove service profile")
        try:
            test.expect(test.profile.dstl_get_service().dstl_close_service_profile())
            test.expect(test.profile.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket object was not created.")
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
