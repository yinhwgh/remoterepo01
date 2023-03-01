#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0085124.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim
from dstl.auxiliary.devboard import devboard
from dstl.network_service import customization_network_types
from dstl.call import setup_voice_call
from dstl.call import switch_to_command_mode
from dstl.configuration import check_sync_status_for_sled
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.auxiliary.ip_server.echo_server import EchoServer

import re

class Test(BaseTest):
    """
    TC0085124.002 - TpSled
    Intention:
    Verification of LED feature provided by the device's STATUS line.
    Every possible operating mode of AT^SLED command is to be checked,
    with a few LED flash period parameter values for 2nd operating mode.
    Perform voice call steps only with products which supported this feature.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_lock_sim())
        test.echo_server = EchoServer("IPv4", "TCP")

    def run(test):
        sled_modes = ['1', '2']
        loop_number = 0
        # network_types = test.dut.dstl_customized_network_types()
        # network_types = [network_type.lower() for network_type, supported in network_types.items() if supported]
        network_types = ["gsm"]
        for sled_mode in sled_modes:
            loop_number += 1
            test.log.step(f"{loop_number}.1. Set <mode> with ^SLED write command")
            test.expect(test.dut.at1.send_and_verify(f"AT^SLED={sled_mode}"))
            test.expect(test.dut.at1.send_and_verify(f"AT^SLED?", f"\^SLED: {sled_mode}"))

            test.log.step(f"{loop_number}.2. Store AT command settings to user defined profile - AT&W")
            test.expect(test.dut.at1.send_and_verify("AT&W"))

            test.log.step(f"{loop_number}.3. Restart tested device")
            test.expect(test.dut.dstl_restart())

            test.log.step(f"{loop_number}.4. Check ^SLED <mode> with read command")
            test.expect(test.dut.at1.send_and_verify(f"AT^SLED?", f"\^SLED: {sled_mode}"))

            test.log.step(f"{loop_number}.5. Check STATUS line state with AT^MCSYNC on McTest")
            test.expect(test.dut.at1.send_and_verify("AT+CPIN?", "SIM PIN"))
            test.expect(test.dut.dstl_check_sync_status_for_sled(sled=sled_mode))

            test.log.step(f"{loop_number}.6. Enter SIM PIN")
            test.expect(test.dut.dstl_enter_pin())

            for network_type in network_types:
                if hasattr(test.dut, f"dstl_register_to_{network_type}"):
                    test.log.step(f"{loop_number}.7.1. Register to selected generation")
                    register_to_network = eval(f"test.dut.dstl_register_to_{network_type}")
                    test.expect(register_to_network())

                    test.log.step(f"{loop_number}.7.2. Check STATUS line state")
                    test.expect(test.dut.dstl_check_sync_status_for_sled(sled=sled_mode, registered=True, data_transfer=False))

                    test.log.step(f"{loop_number}.7.3. Perform MOC to REMOTE, connect to incoming call on REMOTE")
                    call_succeed = test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr, "OK")

                    test.log.step(f"{loop_number}.7.4. Check STATUS line state")
                    if call_succeed:
                        test.expect(test.dut.dstl_check_sync_status_for_sled(sled=sled_mode, registered=True, data_transfer=False))
                    else:
                        test.expect(call_succeed, msg="Fail to make call, skip checking line state.")

                    test.log.step(f"{loop_number}.7.5. Establish data connection, for example Dial-up, SWWAN, Transparent")
                    is_connected = test.enter_transparent_mode(profile_id=1)

                    test.log.step(f"{loop_number}.7.6. Check STATUS line state")
                    if is_connected:
                        thread_transfer_data = test.thread(test.thread_transfer_data)
                        thread_check_sync_state = test.thread(test.expect,
                                                              test.dut.dstl_check_sync_status_for_sled(
                                                                  sled=sled_mode,
                                                                  registered=True, data_transfer=True))
                        thread_transfer_data.join()
                        thread_check_sync_state.join()
                    else:
                        test.expect(is_connected, msg="Fail to enter transparent mode, "
                                                      "skip checking SYNC line for data transfer.")
                    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                    test.expect(test.socket_service.dstl_close_service_profile())

                else:
                    test.expect(False, msg=f"No dstl to register to {network_type}.")

    def cleanup(test):
        if not test.dut.at1.send_and_verify('AT', 'OK'):
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        if hasattr(test, 'test.socket_service') and test.socket_service:
            test.socket_service.dstl_close_service_profile()
        if hasattr(test, 'test.connection_setup_dut') and test.connection_setup_dut:
            test.connection_setup_dut.dstl_deactivate_internet_connection()

    def enter_transparent_mode(test, profile_id):
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IP", ip_public=False)
        pdp_cid = ""
        # Since if there is a pdp context already activated, another one with the same type and apn
        # cannot be activated anymore.
        # Try already defined and activated context, if cannot work, then define a new one.
        test.log.info("Reading activated cids.")
        test.dut.at1.send_and_verify("AT+CGATT=1", "OK")
        test.dut.at1.send_and_verify("AT+CGATT?", "OK")
        test.dut.at1.send_and_verify("AT+CGACT?", "OK")
        activated_cids = re.findall('\+CGACT: (\d+),1', test.dut.at1.last_response)
        if activated_cids:
            test.dut.at1.send_and_verify("AT+CGDCONT?", "OK")
            for cid in activated_cids:
                if re.search('\+CGDCONT: {cid},".*","IMS"', test.dut.at1.last_response):
                    continue
                else:
                    pdp_cid = cid
                    break
        if pdp_cid:
            test.connection_setup_dut.cgdcont_parameters['cid'] = pdp_cid
            activated = test.dut.dstl_activate_internet_connection()
            if not activated:
                pdp_cid = ""
        if not pdp_cid:
            test.log.info("Using a different cid for internet services.")
            pdp_cid = '10'
            test.connection_setup_dut.cgdcont_parameters['cid'] = pdp_cid
            test.connection_setup_dut.dstl_define_pdp_context()
            test.expect(test.connection_setup_dut.dstl_activate_internet_connection())

        test.socket_client = SocketProfile(test.dut, profile_id, test.connection_setup_dut.dstl_get_used_cid(),
                               protocol="udp", etx_char=26)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_client.dstl_generate_address()
        test.socket_service = test.socket_client.dstl_get_service()
        test.expect(test.socket_service.dstl_load_profile())

        test.socket_service.dstl_open_service_profile()
        is_connected = test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1")
        if is_connected:
            is_connected = test.socket_service.dstl_enter_transparent_mode(profile_id)
        return is_connected

    def thread_transfer_data(test):
        for i in range(5):
            test.dut.at1.send('abc')
            test.sleep(2)

if '__main__' == __name__:
    unicorn.main()


