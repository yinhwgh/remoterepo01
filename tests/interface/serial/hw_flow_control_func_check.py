#responsible: wen.liu@thalesgroup.com
#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0103790.001


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.call import switch_to_command_mode
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile

class Test(BaseTest):
    '''
     TC0103790.001 - HWFlowControlFuncCheck
     Intention: Check the function of RTS/CTS pull high and low
     Subscriber: 1
     '''
    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.dut.at1.send_and_verify("AT&F")
        test.dut.at1.send_and_verify("AT&V")
        test.echo_server = EchoServer(ip_version="IPv4", protocol="UDP")

    def run(test):
        test.log.info("Saving response of ATCs and check after RTS OFF->ON.")
        test.dut.at1.send_and_verify('AT')
        at_response = test.dut.at1.last_response
        test.dut.at1.send_and_verify('AT+COPS?')
        cops_response = test.dut.at1.last_response
        test.dut.at1.send_and_verify('AT^SCFG?')
        scfg_response = test.dut.at1.last_response
        test.dut.at1.send_and_verify('AT^SIND?')
        sind_response = test.dut.at1.last_response
        test.dut.at1.send_and_verify('AT+COPN')
        copn_response = test.dut.at1.last_response

        test.log.step("Scenario 1. Toggle OFF RTS line,  all input command will have no response.")
        test.toggle_off_rts()
        test.expect(not test.dut.at1.send_and_verify('AT', '.+', wait_for="", wait_after_send=5,
                                                     timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT', '.+', wait_for="", wait_after_send=5,
                                                     timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT', '.+', wait_for="", wait_after_send=5,
                                                     timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT+COPS?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT+COPS?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT+COPS?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))

        response_of_atcs = at_response*3 + cops_response*3
        test.recover_rts_and_check_response(response_of_atcs)

        test.log.step("Scenario 2. Toggle OFF RTS line,  check AT command which have long return value.")
        test.toggle_off_rts()
        test.expect(not test.dut.at1.send_and_verify('AT^SCFG?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT^SCFG?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT^SCFG?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))

        test.recover_rts_and_check_response(scfg_response, check_times=3, wait_before_read=5)

        test.toggle_off_rts()
        test.expect(not test.dut.at1.send_and_verify('AT^SIND?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT^SIND?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT^SIND?', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))

        test.recover_rts_and_check_response(sind_response, check_times=3, wait_before_read=5)

        test.toggle_off_rts()
        test.expect(not test.dut.at1.send_and_verify('AT+COPN', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT+COPN', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))
        test.expect(not test.dut.at1.send_and_verify('AT+COPN', '.+', wait_for="",
                                                     wait_after_send=5, timeout=5, handle_errors=True))

        test.recover_rts_and_check_response(copn_response, check_times=3, wait_before_read=5)

        test.log.step("")
        connected = test.enter_transparent_mode()
        if connected:
            test.toggle_off_rts()
            send_data = "Sending some data in Transparent mode."
            test.dut.at1.send("Sending some data in Transparent mode.")
            test.expect(not test.dut.at1.send_and_verify('Sending some data in Transparent mode.',
                                                         '.+', wait_for="",wait_after_send=5,
                                                         timeout=5, handle_errors=True))
            test.recover_rts_and_check_response(send_data)
            test.toggle_off_rts()
            test.dut.at1.send(b'+++')
            test.sleep(3)
            test.expect('+++' not in test.dut.at1.read() and 'OK' not in test.dut.at1.last_response)
            test.recover_rts_and_check_response("OK")
        else:
            test.expect(connected, msg="Fail to enter transparent mode, "
                                           "skip test RTS under data mode.")

    def enter_transparent_mode(test):
        pdp_cid = '10'
        internet_profile_id = '1'
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version="IP",
                                                                     ip_public=False)
        test.connection_setup_dut.cgdcont_parameters['cid'] = pdp_cid
        test.connection_setup_dut.dstl_define_pdp_context()
        test.expect(test.connection_setup_dut.dstl_activate_internet_connection())
        test.socket_client = SocketProfile(test.dut, internet_profile_id,
                                           test.connection_setup_dut.dstl_get_used_cid(),
                                           protocol="udp", etx_char=26)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_client.dstl_generate_address()
        test.socket_service = test.socket_client.dstl_get_service()
        test.expect(test.socket_service.dstl_load_profile())

        test.socket_service.dstl_open_service_profile()
        test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1")
        is_connected = test.socket_service.dstl_enter_transparent_mode(internet_profile_id)
        return is_connected

    def recover_rts_and_check_response(test, expect_response, check_times=1, wait_before_read=1):
        test.log.info("Recover RTS, response displays.")
        test.dut.at1.connection.setRTS(True)
        test.sleep(1)
        test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")
        test.sleep(wait_before_read)
        test.dut.at1.read()
        if len(expect_response) < 100:
            output_response = expect_response
        else:
            output_response = expect_response[:10] + '...'
        test.log.info(f"Checking text {output_response} times {check_times} in response.")
        find_response = test.expect(test.dut.at1.verify(expect_response*check_times, test.dut.at1.last_response))
        if not find_response:
            times = check_times - 1
            while times >= 1:
                find_response = test.dut.at1.verify(expect_response*times, test.dut.at1.last_response)
                if find_response:
                    test.log.info(f"Found {times} times response, expected times is {check_times}.")
                    test.expect(find_response)
                    break
                else:
                    test.log.warning(f"Failed to find {times} times response.")
                    test.log.warning("For Viper, it was caused by IPIS100334923 - not to fix.")
                    times -= 1

    def toggle_off_rts(test):
        test.dut.at1.connection.setRTS(False)
        test.sleep(1)
        test.log.h3(f"RTS line state: {test.dut.at1.connection.rts}")

    def cleanup(test):
        if test.dut.at1.connection:
            test.dut.at1.connection.setRTS(True)
            test.sleep(1)
        if not test.dut.at1.send_and_verify('AT', 'OK'):
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
        if hasattr(test, 'test.socket_service') and test.socket_service:
            test.socket_service.dstl_close_service_profile()
        if hasattr(test, 'test.connection_setup_dut') and test.connection_setup_dut:
            test.connection_setup_dut.dstl_deactivate_internet_connection()

if '__main__' == __name__:
    unicorn.main()
