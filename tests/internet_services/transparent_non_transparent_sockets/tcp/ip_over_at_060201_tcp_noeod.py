#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094384.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles


class Test(BaseTest):
    """This TC checks if socket client service can be opened and closed."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_restart(test.r1))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))
        dstl_set_scfg_urc_dst_ifc(test.r1)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def run(test):
        test.log.h2("Executing test script for: TC0094384.002 IPoverAT_060201_tcp_noeod")

        test.log.step("1. Define and activate PDP context for remote")
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define socket profile for remote: TCP listener")
        test.socket_listener = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open listener service for remote")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        r1_ip_address = test.socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("4. Define and activate PDP context for DUT")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("5. Define service profile for DUT: TCP client")
        test.socket_client = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                      protocol="tcp", host=r1_ip_address, port=65100)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("6. Open client service for DUT, accept on remote side")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_1 = SocketProfile(test.r1, test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(), 1)
        test.expect(test.socket_server_1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("7. DUT: close service")
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command(100, expected='ERROR'))
        test.expect(test.socket_server_1.dstl_get_urc().dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.r1.at1.read()

        test.log.step("8. DUT: Open service")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

        test.log.step("9. REMOTE: Accept connection from DUT")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        test.socket_server_2 = SocketProfile(test.r1, test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(), 1)
        test.expect(test.socket_server_2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_server_2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("10. REMOTE: Close service.")
        test.expect(test.socket_server_2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command(100, expected='ERROR'))
        test.expect(test.socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("11. Close and clear service profiles for client and server")
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server_2.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)


if "__main__" == __name__:
    unicorn.main()
