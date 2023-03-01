#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0010200.001, TC0010200.003

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call import switch_to_command_mode
from dstl.call.setup_voice_call import dstl_is_data_call_supported
from dstl.auxiliary.ip_server.echo_server import EchoServer


class Test(BaseTest):
    """
    TC0010200.001, TC0010200.003 -  DSRFunctionMode
    The module shall be able to set the DSR line of the RS232 interface to either always on or on while it is in data mode.
    Subscribers: 2, dut & remote
    Designed for Viper: Not finished yet.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())
        test.socket_profile_id = 1
        test.dut.at1.send_and_verify("AT^SCFG?")
        scfg_response = test.dut.at1.last_response.lower()
        if "gpio/mode/dcd0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dcd0\",\"std\"")
        if "gpio/mode/dsr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dsr0\",\"std\"")
        if "gpio/mode/dtr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dtr0\",\"std\"")
        test.atd1 = test.dut.at1.send_and_verify("AT&D1", "OK")


    def run(test):
        # Steps 14 ~ 26 in TC description are same with 1 ~ 13, implement them as another loop together with step 27 & 28, total 4 loops.
        test.commands_to_test={
            "AT&S0": "DSR line is always ON.",
            "AT&S1": "ME in test.command mode: DSR is OFF. ME in data mode: DSR is ON.",
            "AT&S": "Same with AT&S0",
            "AT&f": "Same with AT&S0",
        }
        for test.command, description in test.commands_to_test.items():
            test.log.step(f"{test.command} Step 1. Set {test.command} - {description}")
            test.expect(test.dut.at1.send_and_verify(test.command, "OK"))
            if "&S1" in test.command:
                s_value = '1'
                cmd_state = "OFF"
            else:
                s_value = '0'
                cmd_state = "ON"
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&S{}.*".format(s_value)))
            test.check_dsr_state(cmd_state)

            test.log.step(f"{test.command} Step 2. Setup a CSD call between both modules or setup socket connetion.")
            is_connected = False
            data_mode_type = "CSD"
            if test.dut.dstl_is_data_call_supported():
                is_connected = test.setup_mt_data_call()
                if not is_connected:
                    test.log.error("Fail to setup data call, setup socket connection instead.")
                    is_connected, socket_service = test.setup_socket_transparent_connection()
                    data_mode_type = "Socket"
            else:
                is_connected, socket_service = test.setup_socket_transparent_connection()
                data_mode_type = "Socket"
                
            test.log.step(f"{test.command} Step 3. Check the DSR line state after the successful call has been established.")
            if is_connected:
                # Steps 4 & 5 are implemented into check_dsr_in_command_data_mode
                test.check_dsr_in_command_data_mode(dsr_value=s_value, data_mode_type=data_mode_type, step_index=4)
                test.log.step("Step 6. Release the call from remote.")
                test.sleep(2)
                test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
                test.sleep(5)
                if data_mode_type == "CSD":
                    test.release_data_call()
                else:
                    test.sleep(2)
                    socket_service.dstl_close_service_profile()
                    test.sleep(5)
            else:
                test.log.error("Fail to setup data call or socket transparent connetion, skip steps 4, 5, 6")

            test.log.step(f"{test.command} Step 7. Check the DSR line state.")
            test.check_dsr_state(cmd_state)
            
            test.log.step(f"{test.command} Step 8. Initiate PPP connection.")
            test.dut.at1.send_and_verify("AT+CREG?")
            test.dut.at1.send_and_verify("AT+COPS?")
            test.sleep(10)
            test.expect(test.dut.at1.send_and_verify("atd*99#", "CONNECT", wait_for="CONNECT"))
            test.dut.at1.wait_for(".+", timeout=5)

            test.log.step(f"{test.command} Step 9. Check the DSR line state.")
            # Steps 10 & 11 were implemented into check_dsr_in_command_data_mode
            test.check_dsr_in_command_data_mode(dsr_value=s_value, data_mode_type="PPP", step_index=10)

            test.log.step(f"{test.command} Step 12. Abort the PPP connection.")
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())

            test.log.step(f"{test.command} Step 13. Check the DSR line state.")
            test.check_dsr_state(cmd_state)
            
                
    def check_dsr_state(test, expect_state):
        dsr_state = test.dut.at1.connection.dsr
        if expect_state == 'ON' and dsr_state == True:
            test.log.info("DSR line is ON as expected.")
        elif expect_state == 'OFF' and dsr_state == False:
            test.log.info("DSR line is OFF as expected.")
        else:
            line_state = "ON" if dsr_state == True else "OFF"
            test.expect(line_state == expect_state, msg=f'DSR line is {line_state}, '
            f'while it should be {expect_state} - {test.command}')
    
    def setup_mt_data_call(test):
        test.log.info("******** Setup data call from remote module to dut ********")
        test.r1.at1.send(f"ATD{test.dut.sim.int_data_nr}")
        is_ring = test.dut.at1.wait_for("RING")
        is_connect = False
        if is_ring:
            test.dut.at1.send("ata")
            is_connect = test.r1.wait_for("CONNECT")
            is_connect = is_connect and test.dut.wait_for("CONNECT", append=True)
        else:
            test.log.error("Module did receive RING when setting up data call.")
        return is_connect
    
    def release_data_call(test):
        test.log.info("List the active calls at ASC0 of the calling party.")
        test.expect(test.dut.at1.send_and_verify("AT+CLCC",".*CLCC: 1,1,0,1,0.*"))
        test.log.info("Release the call at dut of the called party.")
        test.expect(test.dut.at1.send_and_verify("ath", ".*OK.*"))
        test.expect(test.r1.at1.wait_for("NO CARRIER"))
        
    def setup_socket_transparent_connection(test):
        test.log.info("******** Setup socket connection ********")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.echo_server = EchoServer("IPv4", "UDP")
        test.client = SocketProfile(test.dut, test.socket_profile_id,
                                    connection_setup_dut.dstl_get_used_cid(), protocol="udp",
                                    etx_char=26)
        test.client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client.dstl_generate_address()
        socket_service = test.client.dstl_get_service()
        test.expect(socket_service.dstl_load_profile())

        open_socket = socket_service.dstl_open_service_profile()
        if not open_socket:
            test.log.info("Socket may already open, close and try reopen.")
            socket_service.dstl_close_service_profile()
            socket_service.dstl_open_service_profile()
        is_connected = test.client.dstl_get_urc().dstl_is_sisw_urc_appeared("1")
        if is_connected:
            test.log.info("******** Socket connection is established, entering transparent mode********")
            test.dut.at1.send(f"AT^SIST={test.socket_profile_id}")
            is_connected = test.dut.at1.wait_for("CONNECT", timeout=10)
            if not is_connected:
                test.log.error("Failed to enter transparent mode.")
                test.expect(socket_service.dstl_close_service_profile())
                test.sleep(5)
        else:
            test.log.error("Failed to establish socket connection.")
            test.expect(socket_service.dstl_close_service_profile())
            test.sleep(5)
        return is_connected,socket_service
    
    def check_dsr_in_command_data_mode(test, dsr_value, data_mode_type="PPP", step_index="4"):
        # data_mode_type should be "PPP" or "CSD" or "Socket"
        if dsr_value == '1':
            command_mode_state = 'OFF'
        else:
            command_mode_state = 'ON'
        data_mode_atc = "ATO" if data_mode_type in ("PPP", "CSD") else f"AT^SIST={test.socket_profile_id}"
        # Check DSR state before setting back to cmd mode
        test.check_dsr_state("ON")
        if test.atd1 == True:
            test.log.step(f"{test.command} Step {step_index}. Switch to cmd mode and check DSR line state.")
            step_index += 1
            test.sleep(2)
            exit = test.dut.dstl_switch_to_command_mode_by_pluses()
            if not exit and 'ERROR' not in test.dut.at1.last_response:
                test.log.info(f'Fail to switch to test.command mode with +++, try with DTR line - '
                              f'AT&S{dsr_value}')
                exit = test.dut.dstl_switch_to_command_mode_by_dtr()
            if exit:
                test.check_dsr_state(command_mode_state)
                test.log.step(f"{test.command} Step {step_index}. Return to data mode and check DSR line state.")
                test.expect(test.dut.at1.send_and_verify(data_mode_atc, "CONNECT",
                                                         wait_for="CONNECT", timetout=60))
                test.check_dsr_state("ON")
            else:
                test.expect(exit, msg=f'Fail to switch to test.command mode neither with +++ or DTR line '
                                      f'- AT&S{dsr_value}')
        else:
            test.log.info(f"Module does not support AT&D1, skip step {step_index} and {step_index + 1}")
            
    def cleanup(test):
        test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

if "__main__" == __name__:
    unicorn.main()