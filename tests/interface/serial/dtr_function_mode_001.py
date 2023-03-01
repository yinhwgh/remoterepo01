#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0010205.001, TC0010205.004

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode
from dstl.call.setup_voice_call import dstl_is_data_call_supported
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    """
    TC0010205.001, TC0010205.004 - DTRFunctionMode
    The module shall be able to set the DSR line of the RS232 interface to either always on or on while it is in data mode.
    Subscribers: 2, dut & remote

    """

    def setup(test):
        test.dut.dstl_detect()
        test.log.info(f"DTR Status: {test.dut.at1.connection.dsrdtr}")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.dut.at1.send_and_verify("AT^SCFG?")
        scfg_response = test.dut.at1.last_response.lower()
        if "gpio/mode/dcd0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dcd0\",\"std\"")
        if "gpio/mode/dtr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dtr0\",\"std\"")
        if "gpio/mode/dtr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dtr0\",\"std\"")
        test.dut.dstl_switch_off_at_echo()

    def run(test):
        test.log.h3("Total 30 steps in WebImacs will be split to 5 loops for AT&D0, AT&D1, AT&D2, "
                    "AT&F, AT&D in scripts.")
        commands_to_test={
            "AT&D0": "ME ignores status of DTR line",
            "AT&D1": "ME should switch to command mode and can be switch back to data mode with ATO",
            "AT&D2": "ME should switch to command mode",
            "AT&F": "Same with AT&D2, ME should switch to command mode",
            "AT&D": "Same with AT&D0, ME ignores status of DTR line"
        }
        for test.command, description in commands_to_test.items():
            if test.command in ('AT&F', 'AT&D2'):
                d_value = '2'
            elif test.command in ('AT&D', 'AT&D0'):
                d_value = '0'
            else:
                d_value = '1'

            test.log.step(f"{test.command} 1. Set {test.command} parameter- {description}")
            test.expect(test.dut.at1.send_and_verify(test.command, "OK"))
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(d_value)))
            
            # Since Viper and Serval does not support data call, CSD connection part was not debugged.
            test.log.step(f"{test.command} 2. Establish CSD connection.")
            if test.dut.dstl_is_data_call_supported():
                is_connected = test.setup_mt_data_call()
                if not is_connected:
                    test.log.expect(is_connected, msg="Fail to setup data call, skip steps 3, 4, 5, 6, 7")
                else:
                    test.toggle_dtr_functionality(start_step=3, d_value=d_value)
                    test.release_data_call()
            else:
                test.log.info("Module does not support Data Call, skip steps 3, 4, 5, 6, 7 for CSD. ")
            

            test.log.step(f"{test.command} 8. Initiate PPP connection.")
            test.dut.at1.send_and_verify("AT+CREG?")
            test.dut.at1.send_and_verify("AT+COPS?")
            test.sleep(10)
            ppp_connect = test.dut.at1.send_and_verify("atd*99#", "CONNECT", wait_for="CONNECT")
            if ppp_connect:
                test.sleep(1)
                test.toggle_dtr_functionality(start_step=9, d_value=d_value)
            else:
                test.log.expect(ppp_connect, msg="Failed to establish PPP connection, steps 9~13 skipped.")

            test.log.step(f"{test.command} 14. Initiate transparent connection.")
            is_connected = test.setup_socket_transparent_connection()
            if is_connected:
                test.sleep(1)
                test.toggle_dtr_functionality(start_step=15, d_value=d_value, connection='T')
                test.socket_service.dstl_close_service_profile()
            else:
                test.expect(is_connected, msg="Failed to enter transparent mode, skip 15~19 steps.")

    def setup_mt_data_call(test):
        test.log.info("******** Setup data call from remote module to dut ********")
        test.r1.dstl_register_to_network()
        test.r1.at1.send(f"ATD{test.dut.sim.int_data_nr}")
        is_ring = test.dut.at1.wait_for("RING")
        is_connect = False
        if is_ring:
            test.dut.at1.send("ata")
            is_connect = test.r1.wait_for("CONNECT", append=True)
        else:
            test.log.error("Module did receive RING when setting up data call.")
        return is_connect

    def release_data_call(test):
        test.log.info("List the active calls at ASC0 of the calling party.")
        test.expect(test.dut.at1.send_and_verify("AT+CLCC",".*CLCC: 1,1,0,1,0.*"))
        test.log.info("Release the call at dut of the called party.")
        test.expect(test.dut.at1.send_and_verify("ath", ".*OK.*"))
        test.expect(test.r1.at1.wait_for("NO CARRIER"))

    def toggle_dtr_functionality(test, start_step, d_value, connection='PPP'):
        test.toggle_dtr()
        if d_value == '0':
            test.log.step(f"{test.command} {start_step}: Toogle DTR line, should be ignored.")
            not_cmd_mode = test.expect(not test.dut.at1.wait_for('OK|NO CARRIER', timeout=10))
            if not_cmd_mode:
                test.log.step(f"{test.command} {start_step + 1}: Switch to AT command mode.")
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.sleep(2)
                test.log.step(f"{test.command} {start_step + 2}: Return to data mode.")
                if connection == 'PPP':
                    test.expect(test.dut.at1.send_and_verify("ATD*99#", "CONNECT", wait_for="CONNECT"))
                else:
                    test.expect(test.dut.at1.send_and_verify("AT^SIST=1", "CONNECT", wait_for="CONNECT"))

            test.log.step(f"{test.command} {start_step + 3}: Toggle DTR line, should be ignored.")
            test.toggle_dtr()
            not_cmd_mode = test.expect(not test.dut.at1.wait_for('OK|NO CARRIER', timeout=10))
            if not_cmd_mode:
                test.log.step(f"{test.command} {start_step + 4}: Abort PPP connection.")
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.sleep(2)

        elif d_value == '1':
            test.log.step(f"{test.command} {start_step}: Toogle DTR line, ME should switch to "
                          f"command mode.")
            cmd_mode = test.expect(test.dut.at1.wait_for('OK', timeout=10))
            if not cmd_mode:
                if "NO CARRIER" in test.dut.at1.last_response:
                    test.log.error("OK should return , while returned is NO CARRIER.")
                else:
                    test.log.info("Fail to abort connection with DTR ON-> OFF.")
                    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                    test.sleep(2)

            test.log.step(f"{test.command} {start_step + 1}: Return to data mode.")
            test.expect(test.dut.at1.send_and_verify("ATO", "CONNECT", wait_for="CONNECT"))

            test.log.step(f"{test.command} {start_step + 2}: Abort PPP/Transparent connection.")
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.sleep(2)
        # d_value is '2'
        else:
            test.log.info(f"{test.command} {start_step}: Toogle DTR line, (check if NO CARRIER appears).")
            if connection == 'PPP':
                expect = 'NO CARRIER'
                unexpect = 'OK'
            else:
                expect = 'OK'
                unexpect = 'NO CARRIER'
            cmd_mode = test.expect(test.dut.at1.wait_for(expect, timeout=10))
            if not cmd_mode:
                if unexpect not in test.dut.at1.last_response:
                    test.log.error("Fail to terminate connection with DTR ON->OFF.")
                    test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                    test.sleep(2)
                else:
                    test.log.error(f"{expect} should return , while returned is {unexpect}.")
        test.log.info("Toggle DTR ON to enable URC.")
        test.toggle_on_dtr()

    def toggle_dtr(test):
        if test.dut.at1.connection.dsrdtr:
            test.log.info("Setting DTR to OFF.")
            test.dut.at1.connection.setDTR(False)
        test.log.info("Toggling DTR ON->OFF")
        test.dut.at1.connection.setDTR(True)
        test.sleep(0.5)
        test.dut.at1.connection.setDTR(False)

    def toggle_on_dtr(test):
        if not test.dut.at1.connection.dsrdtr:
            test.log.info("Setting DTR to ON.")
            test.dut.at1.connection.setDTR(True)

    def setup_socket_transparent_connection(test):
        test.log.info("******** Setup socket connection ********")
        socket_profile_id = '1'
        if not (hasattr(test, 'socket_service') and test.socket_service):
            test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
            test.connection_setup_dut.cgdcont_parameters['cid'] = '10'
            test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
            test.echo_server = EchoServer("IPv4", "UDP")
            test.client = SocketProfile(test.dut, socket_profile_id,
                                        test.connection_setup_dut.dstl_get_used_cid(),
                                        protocol="udp", etx_char="26")
            test.client.dstl_set_parameters_from_ip_server(test.echo_server)
            test.client.dstl_generate_address()
            test.socket_service = test.client.dstl_get_service()
            test.expect(test.socket_service.dstl_load_profile())

        open_socket = test.socket_service.dstl_open_service_profile()
        if not open_socket:
            test.log.info("Socket may already open, close and try reopen.")
            test.socket_service.dstl_close_service_profile()
            test.socket_service.dstl_open_service_profile(e)
        is_connected = test.client.dstl_get_urc().dstl_is_sisw_urc_appeared("1")
        if is_connected:
            test.log.info("******** Socket connection is established, entering transparent mode "
                          "********")
            is_connected = test.socket_service.dstl_enter_transparent_mode()
            if not is_connected:
                test.log.error("Failed to enter transparent mode.")
                test.expect(test.socket_service.dstl_close_service_profile())
                test.sleep(5)
        else:
            test.log.error("Failed to establish socket connection.")
            test.expect(test.socket_service.dstl_close_service_profile())
            test.sleep(5)
        return is_connected

    def cleanup(test):
        if not test.dut.at1.send_and_verify("AT", "OK", timeout=10, handle_errors=True):
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        if hasattr(test, 'socket_service') and test.socket_service:
            test.socket_service.dstl_close_service_profile()
        if hasattr(test, 'connection_setup_dut') and test.connection_setup_dut:
            test.connection_setup_dut.dstl_deactivate_internet_connection()
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))
        test.dut.dstl_switch_on_at_echo()

if "__main__" == __name__:
    unicorn.main()