# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0094383.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """This TC checks if socket client service can send data to TCP Listener."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_enter_pin(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0094383.001 - "
                      "IPoverAT_030101_tcp_client_sisw'")
        test.log.step("1. Define and activate PDP context for remote")
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define socket profile for remote: TCP listener")
        srv_id = 0
        test.socket_rem = SocketProfile(test.r1, srv_id, test.connection_setup_r1.
                                        dstl_get_used_cid(), protocol="tcp", host="listener",
                                        localport=65100)
        test.socket_rem.dstl_generate_address()
        test.expect(test.socket_rem.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open listener service for remote")
        test.expect(test.socket_rem.dstl_get_service().dstl_open_service_profile())
        remote_ip_address = \
            test.socket_rem.dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version='IPv4').split(":")[0]

        test.log.step("4. Define and activate PDP context for DUT")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("5. Define service profile for DUT: TCP client")
        test.socket_dut = SocketProfile(test.dut, srv_id, test.connection_setup_dut.
                                        dstl_get_used_cid(), protocol="tcp", host=remote_ip_address,
                                        port=65100)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

        test.log.step("6. Open client service for DUT, accept on remote side")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_rem.dstl_get_urc().dstl_is_sis_urc_appeared("1", ""+str(srv_id+1)))
        test.socket_server_1 = SocketProfile(test.r1, test.socket_rem.dstl_get_urc().
                                             dstl_get_sis_urc_info_id(),
                                             test.connection_setup_r1.dstl_get_used_cid())
        test.expect(test.socket_server_1.dstl_get_service().dstl_open_service_profile())

        test.log.step("7. Send 15 bytes from client, read data on server side (50 times in total)")
        data_15 = 15
        loops = 50
        test.transfer_data(test.socket_dut, test.socket_server_1, data_15, loops)

        test.log.step("8. Check amount of sent and received data")
        test.expect(test.socket_server_1.dstl_get_parser().dstl_get_service_data_counter("RX") ==
                    data_15*loops)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("TX") ==
                    data_15*loops)

        test.log.step("9. Send end of data flag from client")
        test.expect(test.socket_dut.dstl_get_service().dstl_send_sisw_command(0, "1"))
        test.sleep(3)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)
        test.expect(test.socket_dut.dstl_get_service().dstl_send_sisw_command(data_15,
                                                                              expected=".*ERROR.*"))
        test.expect(test.socket_server_1.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

    def cleanup(test):
        test.log.step("10. Close and clear service profiles for client and server")
        test.expect(test.socket_rem.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_rem.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server_1.dstl_get_service().dstl_reset_service_profile())

    def transfer_data(test, socket_profile_dut, socket_profile_rem, data_15, loops):
        data_to_send = dstl_generate_data(data_15)

        for x in range(loops):
            test.expect(socket_profile_dut.dstl_get_service().dstl_send_sisw_command(data_15))
            test.expect(socket_profile_dut.dstl_get_service().dstl_send_data(data_to_send))

            test.expect(socket_profile_rem.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
            test.expect(socket_profile_rem.dstl_get_service().dstl_read_data(data_15))
            test.expect(socket_profile_rem.dstl_get_service().dstl_get_confirmed_read_length() ==
                        data_15)


if "__main__" == __name__:
    unicorn.main()