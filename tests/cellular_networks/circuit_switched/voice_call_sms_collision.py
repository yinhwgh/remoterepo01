# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0091960.001, TC0091960.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.configuration import network_registration_status
from dstl.status_control import extended_indicator_control
from dstl.internet_service.connection_setup_service import connection_setup_service
from dstl.internet_service.execution import internet_service_execution
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.sms import sms_configurations
from dstl.sms import delete_sms
from dstl.sms import sms_functions
from dstl.sms import select_sms_format
from dstl.call import setup_voice_call

import re


class Test(BaseTest):
    '''
    TC0091960.001, TC0091960.002 - VoiceCallSmsColision
    Intention: Check behavior during SMS write when incoming SMS, voice call or PING.
    Subscriber: 2， dut with two interfaces, remote module
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()

        test.log.info("********** Preparations for sending SMS ************")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_set_preferred_sms_memory("ME"))
        test.expect(test.dut.dstl_delete_all_sms_messages())
        test.expect(test.r1.dstl_register_to_network())
        test.expect(test.r1.dstl_set_preferred_sms_memory("ME"))
        test.expect(test.r1.dstl_delete_all_sms_messages())
        test.log.info(
            "Unnecessary URC should be disabled in case that impacting the URC buffer for CMTI.")
        test.expect(test.dut.dstl_set_network_registration_urc(domain="eps", urc_mode="0"))

    def run(test):
        r1_cid = '1'
        dut_cid = '1'
        test.socket_server = None
        test.socket_client = None
        test.log.step("1. Enable \"^SREG\"/\"^CREG\" URC to report status of network registration")
        test.dut.dstl_set_common_network_registration_urc(enable=True)

        test.log.step(
            '2. Enables the presentation of URC of following specific: "signal", "message", "call", "rssi", "psinfo" - if supported by WM.')
        test.dut.at1.send_and_verify("AT^SIND?")
        indicator_desp = ["signal", "message", "call", "rssi", "psinfo"]
        for desp in indicator_desp:
            if desp in test.dut.at1.last_response:
                test.dut.dstl_enable_one_indicator(desp)

        test.log.step('3. Enable URCs incoming SMS presentation and delivered SMS.')
        test.expect(test.dut.dstl_enable_sms_urc())
        test.expect(test.r1.dstl_enable_sms_urc())

        test.log.step('4. Set SMS message format to text mode.')
        test.expect(test.dut.dstl_select_sms_message_format("Text"))
        test.expect(test.r1.dstl_select_sms_message_format("Text"))

        test.log.step('5. Open internet connection.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object(ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = test.r1.dstl_get_connection_setup_object(ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        test.socket_server = SocketProfile(test.dut, dut_cid,
                                           connection_setup_dut.dstl_get_used_cid(),
                                           protocol="tcp",
                                           host="listener", localport=50000, etx_char=26,
                                           connect_timeout=30)
        test.socket_server.dstl_generate_address()
        test.expect(test.socket_server.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())
        dut_ip_address = \
            test.socket_server.dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version='IPv4').split(":")[0]
        test.socket_client = SocketProfile(test.r1, r1_cid,
                                           connection_setup_r1.dstl_get_used_cid(),
                                           protocol="tcp", host=dut_ip_address, port=50000)

        test.r1.at1.send_and_verify("AT^SISS?")
        test.r1.at1.send_and_verify("AT^SISO?")
        test.socket_client.dstl_generate_address()
        test.socket_client.dstl_get_service().dstl_load_profile()
        test.socket_client.dstl_get_service().dstl_open_service_profile()
        test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1")
        r1_ip_address = \
            test.socket_client.dstl_get_parser().dstl_get_service_local_address_and_port(
                ip_version='IPv4').split(":")[0]
        test.log.info(f"Fetched dut's IP address is {dut_ip_address}")
        test.log.info(f"Fetched remote module's IP address is {r1_ip_address}")

        test.log.step(
            '6. Try to send SMS enter, after invoking the write command wait for the prompt ">": Prompt ">" is displayed.')
        test.expect(test.dut.at1.send_and_verify(f"AT+CSCA=\"{test.dut.sim.sca}\""))
        test.expect(test.r1.at1.send_and_verify(f"AT+CSCA=\"{test.r1.sim.sca}\""))
        test.expect(
            test.dut.at1.send_and_verify(f"AT+CMGS=\"{test.r1.sim.nat_voice_nr}\"", expect=">",
                                         wait_for=">"))

        test.log.step('10. Start looping steps 7~9')
        loop_times = 10
        for loop_num in range(1, loop_times + 1):
            test.log.step(
                f'Loop {loop_num} of {loop_times} - 7. Send incoming SMS on DUT: SMS is send')
            test.expect(test.r1.dstl_send_sms_message(test.dut.sim.nat_voice_nr, "A SMS to DUT"))
            test.log.step(
                f'Loop {loop_num} of {loop_times} - 8. Try to voice call DUT: Voice call is set.')
            test.expect(test.r1.dstl_voice_call_by_number(test.dut, test.dut.sim.nat_voice_nr, "OK",
                                                          device2_port="at2"))
            test.sleep(2)
            test.expect(test.dut.dstl_release_call('at2'))
            test.expect(test.r1.at1.wait_for("NO CARRIER"))
            test.sleep(2)
            test.log.step(
                f'Loop {loop_num} of {loop_times} - 9. Ping module using AT^SISX, requests ping to DUTs local IP address of the Internet connection profile: PING reply received.')
            expect_ping_result = f"\^SISX: \"Ping\",1,{r1_cid},\"{dut_ip_address}\",\d+".replace(
                '.', '\.')
            r1_execution_obj = internet_service_execution.InternetServiceExecution(test.r1.at1,
                                                                                   con_profile_id=r1_cid)
            if dut_ip_address:
                ping_succeed = r1_execution_obj.dstl_execute_ping(address=dut_ip_address, request=5,
                                                                  timelimit=10000,
                                                                  expected_response=expect_ping_result)
                if ping_succeed:
                    test.log.info("Ping dut successfully.")
                else:
                    test.dut.at2.send_and_verify("AT+CGPADDR")
                    test.dut.at2.send_and_verify("AT^SICA")
                    test.r1.at1.send_and_verify("AT+CGPADDR")
                    test.sleep(2)

            else:
                test.expect(False, msg="Step is skipped because of empty IP Address.")

        test.log.info("********* After finishing sending SMS, received SMS URCs appear *********")
        test.expect(test.dut.at1.send_and_verify("Finish sending SMS for VoiceCallSmsColision",
                                                 end="[CTRL+Z]"))
        expect_urc = ""
        test.log.info(f'Checking total {loop_times} +CMTI: "ME" displays')
        for i in range(1, loop_times + 1):
            expect_urc += "\+CMTI: \"ME\",\d+.*"
        test.expect(test.dut.wait_for(expect_urc, append=True))

    def cleanup(test):
        test.expect(test.dut.dstl_release_call(device_interface="at2"))
        test.expect(test.dut.at1.send_and_verify("exit sms editing", end="[CTRL+Z]", expect=".*",
                                                 wait_for=".*", wait_after_send=1,
                                                 handle_errors=True))
        if test.socket_server:
            test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())
        if test.socket_client:
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())


if "__main__" == __name__:
    unicorn.main()

