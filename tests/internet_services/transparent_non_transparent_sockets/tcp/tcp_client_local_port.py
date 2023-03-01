#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0107159.001, TC0107158.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response


class Test(BaseTest):
    """Two Modules are needed (DUT and Remote)
Two SIM Cards with public (static) addresses are needed
Netcat TCP listeners can be used instead of REM Module."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_enter_pin(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_enter_pin(test.r1))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def run(test):

        test.log.step("1) Power on and attach Modules to network.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True, ip_version=test.ip_version)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) On DUT and REM depends on product:\r\n"
                      "- define pdp context/nv bearer (for public/static {0}) using CGDCONT command and activate "
                      "it using SICA command\r\n"
                      "- define connection profile (for public/static {0}) using SICS command\r\n".format(
            test.ip_version))
        test.log.info("executed in previous step")

        test.log.step("3) On REM define {} TCP listener.".format(test.ip_version))
        socket_listener = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100, ip_version=test.ip_version, alphabet=1)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        if test.ip_version == "IPv4":
            r1_ip_address = \
                socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]
        else:
            r1_ip_address = "{}{}".format(
                socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv6').split("]:")[0], "]")

        test.log.step("4) On DUT define:\r\n"
                      "- {0} Non-transparent TCP Client with local port parameter in address field (e.g. ;port=50000)"
                      "\r\n"
                      "- {0} Transparent TCP Client with local port parameter in address field (e.g. ;port=60000)\r\n"
                      .format(test.ip_version))
        localport_1 = "50000"
        localport_2 = "60000"
        socket_client_non_transp = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                                 protocol="tcp", host=r1_ip_address, port=65100, localport=localport_1,
                                                 ip_version=test.ip_version, alphabet=1)
        socket_client_non_transp.dstl_generate_address()
        test.expect(socket_client_non_transp.dstl_get_service().dstl_load_profile())

        socket_client_transp = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(), etx_char="26",
                                             protocol="tcp", host=r1_ip_address, port=65100, localport=localport_2,
                                             ip_version=test.ip_version, alphabet=1)
        socket_client_transp.dstl_generate_address()
        test.expect(socket_client_transp.dstl_get_service().dstl_load_profile())

        test.log.step("5) On DUT check if ports are correctly defined using AT^SISS? command.")
        dstl_check_siss_read_response(test.dut, [socket_client_non_transp, socket_client_transp])
        test.expect(test.dut.at1.send_and_verify("AT^SISS?"))
        test.expect("port={}".format(localport_1) in test.dut.at1.last_response)
        test.expect("port={}".format(localport_2) in test.dut.at1.last_response)

        test.log.step("6) On REM open TCP listener.")
        test.log.info("executed in step 3")

        test.log.step("7) On DUT open Non-transparent TCP Client (accept client on Listener).")
        test.expect(socket_client_non_transp.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server_1 = SocketProfile(test.r1, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                        connection_setup_r1.dstl_get_used_cid())
        test.expect(socket_server_1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_server_1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("8) On DUT and REM check if Client port is correct according to SISS settings.")
        test.check_remoteport(socket_server_1, localport_1)
        test.check_localport(socket_client_non_transp, localport_1)

        test.log.step("9) On DUT open Transparent TCP Client (accept client on Listener).")
        test.expect(socket_client_transp.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server_2 = SocketProfile(test.r1, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                        connection_setup_r1.dstl_get_used_cid())
        test.expect(socket_server_2.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_server_2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("10) On DUT and REM check if Client port is correct according to SISS settings.")
        test.check_remoteport(socket_server_2, localport_2)
        test.check_localport(socket_client_transp, localport_2)

        test.log.step("11) Exchange some data between Listener and Clients.")
        test.exchange_data(socket_client_non_transp, socket_server_1)
        test.exchange_data(socket_client_transp, socket_server_2)

        test.log.step("12) Check Tx/Rx counters and service/socket states using AT^SISO? command.")
        test.check_counters(socket_client_non_transp)
        test.check_counters(socket_client_transp)
        test.check_counters(socket_server_1)
        test.check_counters(socket_server_2)

        test.log.step("13) Close all profiles.")
        test.expect(socket_client_non_transp.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client_transp.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_server_2.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def exchange_data(test, profile_1, profile_2):
        test.expect(profile_1.dstl_get_service().dstl_send_sisw_command_and_data(1500))
        test.expect(profile_2.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(profile_2.dstl_get_service().dstl_read_data(1500))
        test.expect(profile_2.dstl_get_service().dstl_send_sisw_command_and_data(1500))
        test.expect(profile_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(profile_1.dstl_get_service().dstl_read_data(1500))

    def check_counters(test, profile):
        test.expect(profile.dstl_get_parser().dstl_get_service_data_counter("RX") == 1500)
        test.expect(profile.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500)

    def check_localport(test, profile, localport):
        if test.ip_version == "IPv4":
            test.expect(profile.dstl_get_parser().dstl_get_service_local_address_and_port("IPv4").
                        split(":")[1] == localport, msg="wrong localport")
        else:
            test.expect(profile.dstl_get_parser().dstl_get_service_local_address_and_port("IPv6").
                        split("]:")[1] == localport, msg="wrong localport")

    def check_remoteport(test, profile, localport):
        if test.ip_version == "IPv4":
            test.expect(profile.dstl_get_parser().dstl_get_service_remote_address_and_port("IPv4").
                        split(":")[1] == localport, msg="wrong localport")
        else:
            test.expect(profile.dstl_get_parser().dstl_get_service_remote_address_and_port("IPv6").
                        split("]:")[1] == localport, msg="wrong localport")


if "__main__" == __name__:
    unicorn.main()
