# responsible: dominik.tanderys@thalesgroup.com
# location: Wroclaw
# TC0093078.005


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar, \
    dstl_switch_to_command_mode_by_dtr, dstl_switch_to_command_mode_by_pluses
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.serial_interface.serial_interface_flow_control import \
    dstl_check_flow_control_number_after_set
from dstl.configuration.store_user_defined_profile import dstl_store_user_defined_profile


class Test(BaseTest):
    """
    TC0093078.005 - TcTransparentListenerFlowControl
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_restart(test.dut)
        dstl_restart(test.r1)
        dstl_enter_pin(test.dut)
        dstl_enter_pin(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")
        test.srv_id_1 = "0"
        test.data_2048 = 2048
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True, device_interface="at2")

    def run(test):
        test.log.step('1) Define and activate PDP context or define connection profile for '
                      'both modules')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True,
                                                                device_interface="asc_0")
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) Set service profiles: TCP transparent listener on DUT and TCP '
                      'transparent client on remote')
        test.socket_dut = SocketProfile(test.dut, test.srv_id_1,
                                        connection_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp",
                                        host="listener", localport=50000, etx_char=26,
                                        device_interface="asc_0")
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())

        dut_ip_address = \
        test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(
            ip_version='IPv4').split(":")[0]
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.socket_rem = SocketProfile(test.r1, test.srv_id_1,
                                        connection_setup_r1.dstl_get_used_cid(),
                                        device_interface="at2", protocol="tcp", host=dut_ip_address,
                                        port=50000, etx_char="26")

        test.socket_rem.dstl_generate_address()
        test.expect(test.socket_rem.dstl_get_service().dstl_load_profile())

        for flow_control in range(4):
            test.log.info('Perform steps 3-8 changing steps 3 and 6 as listed below. All options '
                          'supported by the tested product shall be tested:')
            test.log.step('3) Set flow control')
            test.expect(dstl_check_flow_control_number_after_set(test.dut, flow_control,
                                                                 serial_port=test.dut.asc_0))
            test.expect(dstl_store_user_defined_profile(test.dut))
            dstl_restart(test.dut)
            test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

            for exit_type in range(3):
                test.log.step('4) Open services and establish connection.')
                test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
                test.expect(test.socket_rem.dstl_get_service().dstl_open_service_profile())
                test.expect(test.socket_dut.dstl_get_urc().
                            dstl_is_sis_urc_appeared(urc_cause="3", urc_info_id="0"))
                test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())


                test.log.step('5) Enter transparent mode, send some data in both direction')
                test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
                test.expect(test.socket_rem.dstl_get_service().dstl_enter_transparent_mode())
                bytes_generated = dstl_generate_data(test.data_2048)
                test.expect(test.socket_dut.dstl_get_service().dstl_send_data(bytes_generated,
                                                                          expected=""))
                test.expect(test.socket_rem.dstl_get_service().dstl_send_data(bytes_generated,
                                                                          expected=""))

                test.log.step('6) DUT exits from transparent mode')
                test.sleep(2)  # sleep so pluses work correctly
                if exit_type == 0:
                    test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface=
                    "asc_0"))

                if exit_type == 1:
                    if not test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26,
                                                                              device_interface=
                                                                              "asc_0")):
                        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut,
                                                                              device_interface=
                                                                              "asc_0"))

                if exit_type == 2:
                    if not test.expect(dstl_switch_to_command_mode_by_dtr(test.dut,
                                                                          device_interface=
                                                                          "asc_0")):
                        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut,
                                                                          device_interface="asc_0"))
                test.expect(dstl_switch_to_command_mode_by_pluses(test.r1, device_interface="at2"))

                test.log.step('7) Check service information')
                test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state(
                    at_command=Command.SISO_WRITE) == ServiceState.CONNECTED.value)
                test.expect(test.socket_rem.dstl_get_parser().dstl_get_service_state(
                    at_command=Command.SISO_WRITE) == ServiceState.UP.value)

                test.expect(
                    test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    test.data_2048)
                test.expect(
                    test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                    test.data_2048)

                test.log.step('8) Close services')
                test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
                test.expect(test.socket_rem.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        dstl_reset_internet_service_profiles(test.dut, profile_id=test.srv_id_1, force_reset=True,
                                             device_interface="asc0")
        dstl_reset_internet_service_profiles(test.r1, profile_id=test.srv_id_1, force_reset=True,
                                             device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_check_flow_control_number_after_set(test.dut, 0,
                                                             serial_port=test.dut.asc_0))
        test.expect(dstl_store_user_defined_profile(test.dut, interface="asc_0"))
        dstl_restart(test.dut)


if "__main__" == __name__:
    unicorn.main()
