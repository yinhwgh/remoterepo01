# responsible dominik.tanderys@globallogic.com
# Wroclaw
# TC0105897.001, TC0105897.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles

class Test(BaseTest):
    """To check possibility to connect to azure servers"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_register_to_network(test.dut), critical=True)
        dstl_reset_internet_service_profiles(test.dut,force_reset=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0105897.001 - HTTPS_azure_ciphersuites', "
                      "'TC0105897.002 - HTTPS_azure_ciphersuites'")

        test.log.step("1 clear out current ciphersuite list")
        test.dut.at1.send("at^sbnw=\"ciphersuites\",0")
        test.dut.at1.wait_for(".*OK.*|.*No Cipher Suites file found or loaded.*")

        test.expect(
            test.dut.at1.send_and_verify("at^sbnr=\"ciphersuites\",current", ".*No Cipher Suites file found or loaded.*"))

        for iteration in range(3):
            timeout = 60#longer timeouts due to websites loading slowly
            test.log.info("iteration: {}".format(iteration))

            test.log.step("2 restart module")
            dstl_restart(test.dut)
            test.expect(dstl_register_to_network(test.dut), critical=True)

            test.log.step("3 Set \"Tcp/TLS/Version\" MIN and MAX to 1.2 (or equivalent, so that tls1.2 is used)")
            test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "1.2", "MAX"))

            test.log.step("4 Create HTTPS get profile to https://azuredatacentermap.azurewebsites.net/")
            connection_setup = dstl_get_connection_setup_object(test.dut)
            test.expect(connection_setup.dstl_load_internet_connection_profile())
            test.expect(connection_setup.dstl_activate_internet_connection())
            srv_id = "0"
            con_id = connection_setup.dstl_get_used_cid()
            http_client = HttpProfile(test.dut, srv_id, con_id, http_command="get",
                                      host="azuredatacentermap.azurewebsites.net/", secopt="0",
                                      secure_connection=True)
            http_client.dstl_generate_address()
            test.expect(http_client.dstl_get_service().dstl_load_profile())

            test.log.step("5 set secopt to 0")
            test.log.info("done in previous step")

            test.log.step("6 open profiles")
            test.expect(http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=timeout))

            test.log.step("7 check service states")
            test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("8 close profiles")
            test.expect(http_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("9 set address to https://portal.azure.com/")
            http_client.dstl_set_host("portal.azure.com/")
            http_client.dstl_generate_address()
            test.expect(http_client.dstl_get_service().dstl_load_profile())

            test.log.step("10 open profiles")
            test.expect(http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=timeout))

            test.log.step("11 check service states")
            test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("12 close profiles")
            test.expect(http_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("13 set address to https://us-west-2.console.aws.amazon.com/")
            http_client.dstl_set_host("us-west-2.console.aws.amazon.com/")
            http_client.dstl_generate_address()
            test.expect(http_client.dstl_get_service().dstl_load_profile())

            test.log.step("14 open profiles")
            test.expect(http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=timeout))

            test.log.step("15 check service states")
            test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("16 close profiles")
            test.expect(http_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("17 set address to https://global-root-ca.chain-demos.digicert.com/")
            http_client.dstl_set_host("global-root-ca.chain-demos.digicert.com/")
            http_client.dstl_generate_address()
            test.expect(http_client.dstl_get_service().dstl_load_profile())

            test.log.step("18 open profiles")
            test.expect(http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=timeout))

            test.log.step("19 check service states")
            test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("20 close profiles")
            test.expect(http_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("21 set address to https://baltimore-cybertrust-root.chain-demos.digicert.com/")
            http_client.dstl_set_host("baltimore-cybertrust-root.chain-demos.digicert.com/")
            http_client.dstl_generate_address()
            test.expect(http_client.dstl_get_service().dstl_load_profile())

            test.log.step("22 open profiles")
            test.expect(http_client.dstl_get_service().dstl_open_service_profile())
            test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=timeout))

            test.log.step("23 check service states")
            test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("24 close profiles")
            test.expect(http_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("25 Create socket profile to socktcps://13.92.128.154:443")
            test.socket_service = SocketProfile(test.dut, 0, connection_setup.dstl_get_used_cid(),
                                                secure_connection=True, secopt="0",
                                                host="13.92.128.154", port="443")
            test.socket_service.dstl_generate_address()
            test.expect(test.socket_service.dstl_get_service().dstl_load_profile())

            test.log.step("26 set secopt to 0")
            test.log.info("done in previous step")

            test.log.step("27 open profiles")
            test.expect(test.socket_service.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared("1", timeout=timeout))

            test.log.step("28 check service states")
            test.expect(test.socket_service.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("29 close profiles")
            test.expect(test.socket_service.dstl_get_service().dstl_close_service_profile())

            if iteration is 0:
                test.log.step("30 choose TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 ciphersuite on module")
                test.set_cipher_suite("ECDHE-RSA-AES256-GCM-SHA384")

                test.log.step("31 repeat steps 2-28")

            elif iteration is 1:
                test.log.step("32 TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 ciphersuite on module")
                test.set_cipher_suite("ECDHE-RSA-AES128-GCM-SHA256")

                test.log.step("33 repeat steps 2-28")

    def cleanup(test):
        test.log.step("34 clear out current ciphersuite list")
        test.dut.at1.send("at^sbnw=\"ciphersuites\",0")
        test.expect(test.dut.at1.wait_for(".*OK.*|.*No Cipher Suites file found or loaded.*"))
        dstl_restart(test.dut)

    def set_cipher_suite(test, chosen_cipher):
        test.dut.at1.send("at^sbnw=\"ciphersuites\",\"{}\"".format(len(chosen_cipher)))
        test.dut.at1.wait_for(".*CIPHERSUITES: SEND FILE.*")
        test.sleep(1)
        test.dut.at1.send(chosen_cipher, end="")
        test.dut.at1.wait_for(".*OK.*")


if "__main__" == __name__:
    unicorn.main()
