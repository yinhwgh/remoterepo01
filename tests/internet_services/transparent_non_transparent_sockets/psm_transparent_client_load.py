# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0107270.001, TC0107271.001

import unicorn
from time import time
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_functions import dstl_enable_sms_urc, dstl_send_sms_message
from dstl.configuration.suspend_mode_operation import dstl_enable_psm, dstl_disable_psm


class Test(BaseTest):
    """ To check Module stability while communicating with TCP/UDP Server
    with active PSM enabled on Module.
    Args:
        protocol (String): define protocol to be used: TCP or UDP """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.echo_server = EchoServer("IPv4", test.protocol, test_duration=49)
        dstl_enter_pin(test.dut)
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut))
        test.expect(dstl_enable_sms_urc(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_register_to_network(test.r1)
        test.expect(dstl_select_sms_message_format(test.r1))
        test.expect(dstl_set_sms_center_address(test.r1))
        test.expect(test.r1.at1.send_and_verify('AT+CSMP=17,167,0,0', '.*OK.*'))

    def run(test):
        test.log.h2("Executing test script for: TC0107270.001 Psm{}TransparentClient_load"
                    .format(test.protocol))
        execution_time_in_seconds = 2*24*60*60

        test.log.step('1) Set PSM on Module (e.g. AT+CPSMS=1,,,"00111000","00001111"')
        test.expect(dstl_enable_psm(test.dut, '', '', '00111000', '00001111'))

        test.log.step("2) Attach Module to network")
        test.log.info("This will be done together with next step")

        test.log.step("3) Depends on Module: \r\n"
                      "- define PDP context/NV bearer and activate it using SICA command \r\n"
                      "- define Connection profile using SICS command")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4) Define Transparent {} Client (connection to echo server)"
                      .format(test.protocol))
        test.socket_client = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                           protocol=test.protocol, etx_char=26)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        start_time = time()
        while int(time() - start_time) < execution_time_in_seconds:
            test.log.step("5) Open {} Client and wait for proper URC".format(test.protocol))
            test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("6) Enter transparent (data) mode")
            test.expect(test.socket_client.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("7) Send 1000 bytes of data and receive echo")
            data_package_size = 200
            data_packages = 5
            data = dstl_generate_data(data_package_size)
            test.expect(test.socket_client.dstl_get_service().dstl_send_data(data, expected=data,
                                                                    repetitions=data_packages))
            test.sleep(3)

            test.log.step("8) Exit transparent (data) mode.")
            test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

            test.log.step("9) Check Tx/Rx counters and service state using AT^SISO? command")
            dut_parser = test.socket_client.dstl_get_parser()
            test.expect(dut_parser.dstl_get_service_data_counter('TX')
                        == data_packages*data_package_size)
            if test.protocol == 'TCP':
                test.expect(dut_parser.dstl_get_service_data_counter('RX')
                            == data_packages*data_package_size)
            else:
                test.expect(dut_parser.dstl_get_service_data_counter('RX')
                            >= data_packages*data_package_size*0.8)
            test.expect(dut_parser.dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("10) Close {} Client profile".format(test.protocol))
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())

            test.log.step("11) Wait till Module enters PSM (e.g. check SMONI command)")
            test.expect(test.check_if_module_enters_psm_mode_with_sms())
            test.expect(dstl_delete_all_sms_messages(test.dut))

            test.log.step("12) Repeat steps 5-11 for 2-3 days")

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem with closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("SocketProfile object was not created.")
        test.expect(dstl_disable_psm(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.dut))

    def check_if_module_enters_psm_mode_with_sms(test):
        test.log.info('Checking if SMS can be received on DUT before it enters PSM mode.')
        dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr)
        test.expect(dstl_check_urc(test.dut, ".*CMTI.*", timeout=120))
        test.log.info("Waiting until module enters PSM mode. For some products (e.g. Serval) "
                      "there is no way to check if module entered PSM mode. We can only check that"
                      " SMS cannot be received in PSM mode.")
        for iteration in range(1, 11):
            test.sleep(35 + iteration*5)
            test.dut.at1.read()
            test.dut.at1.read()
            dstl_send_sms_message(test.r1, test.dut.sim.int_voice_nr)
            if dstl_check_urc(test.dut, ".*CMTI.*", timeout=120):
                test.log.info("SMS received. Module haven't entered PSM mode yet.")
                continue
            else:
                test.log.info("SMS not received. Module entered PSM mode.")
                return True
        return False


if "__main__" == __name__:
    unicorn.main()
