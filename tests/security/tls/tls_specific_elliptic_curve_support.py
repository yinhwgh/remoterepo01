#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0105124.001, TC0105124.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
       to check support of secp256r1, secp384r1, secp521r1 elliptic curves
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
        named_curves = ["Prime256v1", "Secp384r1", "Secp521r1"]
        response_curves_names = ["P-256", "P-384", "P-521"]

        for curve in range(len(named_curves)):

            test.log.info("Now testing: {}".format(named_curves[curve]))
            test.log.step("1. run SSL server with secp256r1 (prime256v1 in openssl) elliptic curve "
                          "(-named_curve for OpenSSL) and ciphersuite set for for any ECDH cipher. e.g. s_server "
                          "-accept 50300 -state -naccept 1 -cipher ECDHE-RSA-AES256-GCM-SHA384 -debug -status_verbose "
                          "-serverpref -cert micCert.pem -certform pem -key mic.pem -keyform pem "
                          "-named_curve prime256v1")
            test.ssl_server = SslServer("IPv4", "socket_tls", "AES128-CCM8")

            test.log.step("2. on DUT configure tcp client to server")
            test.profile = SocketProfile(test.dut, 0, test.connection_setup.dstl_get_used_cid(), protocol="tcp",
                                         host=test.ssl_server.dstl_get_server_ip_address(), secopt="0",
                                         port=test.ssl_server.dstl_get_server_port(), secure_connection=True)
            test.profile.dstl_generate_address()
            test.expect(test.profile.dstl_get_service().dstl_load_profile())
            test.ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server, configuration=named_curves[curve])
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
            test.expect("Shared Elliptic groups: {}".format(response_curves_names[curve])
                        in test.ssh_server.last_response)
            test.expect(test.ssl_server.dstl_compare_cipher_suite(), msg="Incorrect server response!")

            test.log.step("4. repeat steps 1-3 for secp384r1, secp521r1 curves")


    def cleanup(test):
        test.log.step("5. close all connections, remove service profile")
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
