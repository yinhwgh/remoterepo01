# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0103289.001, TC0103289.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """TC0103289.001, TC0103289.002 Check the behaviour of module during transparent connection and
     maximum number of opened listeners with autoconnect" parameter."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def run(test):
        test.log.step("1)1) Depends on product: "
                      "\n- Set and activate Connection Profile (GPRS) "
                      "\n- Set and activate PDP Context Profile")

        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Set service profiles: max amount of TCP transparent listeners on DUT with"
                      " enabled autoconnect option.")
        test.socket_dut = []
        etx = 26
        for profile_number in range(10):
            current_port = "888" + str(profile_number)
            test.socket_dut.append(SocketProfile(test.dut, profile_number,
                                                 conn_setup_dut.dstl_get_used_cid(),
                                                 protocol="tcp", host="listener",
                                                 localport=current_port, autoconnect=1,
                                                 etx_char=etx))
            test.socket_dut[profile_number].dstl_generate_address()
            test.expect(test.socket_dut[profile_number].dstl_get_service().dstl_load_profile())

        test.log.step("3) Open all defined services on DUT")
        for profile in test.socket_dut:
            test.expect(profile.dstl_get_service().dstl_open_service_profile())

        test.log.step("4) On Remote define the same amount of TCP clients on remote.")
        dut_ip = test.socket_dut[0].dstl_get_parser().dstl_get_service_local_address_and_port(
            ip_version='IPv4').split(":")
        test.socket_rem = []
        for profile_number in range(10):
            current_port = "888" + str(profile_number)
            test.socket_rem.append(SocketProfile(test.r1, profile_number,
                                                 conn_setup_dut.dstl_get_used_cid(),
                                                 protocol="tcp", host=dut_ip[0], port=current_port,
                                                 etx_char=etx, device_interface="at2"))
            test.socket_rem[profile_number].dstl_generate_address()
            test.expect(test.socket_rem[profile_number].dstl_get_service().dstl_load_profile())

        for profile_number in range(6):
            test.log.step("5) On Remote open one client service. Iteration: " + str(profile_number))
            test.expect(test.socket_rem[profile_number].dstl_get_service().
                        dstl_open_service_profile())
            test.expect(test.socket_rem[profile_number].dstl_get_urc().
                        dstl_is_sisw_urc_appeared('1'))

            test.log.step("6) Send 10 x 100 bytes from DUT to Remote and from Remote to DUT "
                          "(in transparent mode)")
            test.expect(test.dut.at1.wait_for("CONNECT"))
            test.expect(test.socket_dut[profile_number].dstl_get_service().
                        dstl_enter_transparent_mode(send_command=False))
            test.expect(test.socket_rem[profile_number].dstl_get_service().
                        dstl_enter_transparent_mode())
            data = dstl_generate_data(100)
            for data_packet_number in range(10):
                test.socket_rem[profile_number].dstl_get_service().dstl_send_data(data, expected="")
                test.socket_dut[profile_number].dstl_get_service().dstl_send_data(data, expected="")

            test.log.step("7) Exit from transparent mode")
            test.sleep(10)
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, etx))
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, etx,
                                                               device_interface="at2"))

            test.log.step("8) Check service information")
            test.expect(test.socket_dut[profile_number].dstl_get_parser().
                        dstl_get_service_state() == ServiceState.CONNECTED.value)
            test.expect(test.socket_dut[profile_number].dstl_get_parser().
                        dstl_get_service_data_counter("rx") == 1000)
            test.expect(test.socket_dut[profile_number].dstl_get_parser().
                        dstl_get_service_data_counter("tx") == 1000)

            test.expect(test.socket_rem[profile_number].dstl_get_parser().
                        dstl_get_service_state() == ServiceState.UP.value)
            test.expect(test.socket_rem[profile_number].dstl_get_parser().
                        dstl_get_service_data_counter("rx") == 1000)
            test.expect(test.socket_rem[profile_number].dstl_get_parser().
                        dstl_get_service_data_counter("tx") == 1000)

            test.log.step("9) Repeat steps 5-9 for other client profiles 5 times "
                          "(max amount not specified in LM, 3 minimum)")

    def cleanup(test):
        test.log.step("10) Close all services on DUT and Remote")
        try:
            for profile_number in range(10):
                test.expect(test.socket_dut[profile_number].dstl_get_service().
                            dstl_close_service_profile())
                test.expect(test.socket_rem[profile_number].dstl_get_service().
                            dstl_close_service_profile())
        except (AttributeError, IndexError):
            test.log.error("Problem with connection to module")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)
        dstl_set_scfg_urc_dst_ifc(test.r1)


if "__main__" == __name__:
    unicorn.main()

