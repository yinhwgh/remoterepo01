# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0102336.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_register_to_network, dstl_enter_pin
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.select_sms_format import dstl_select_sms_message_format
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.sms.sms_configurations import dstl_set_preferred_sms_memory
from dstl.sms.sms_center_address import dstl_set_sms_center_address
from dstl.sms.sms_functions import dstl_enable_sms_urc, dstl_send_sms_message
from dstl.configuration.suspend_mode_operation import dstl_enable_psm, dstl_disable_psm
from dstl.internet_service.profile_storage.dstl_execute_sips_command import dstl_execute_sips_command
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """ Verify the stability of IP services (UDP).
        Purpose of this test is to simulate operation of an Internet device (UDP endpoint)
        that runs for a long time and communicates low payload periodically.
        The test is intended mainly for modules that implement power saving features,
        e.g. LTE Cat-M or NB-IoT devices."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_register_to_network(test.r1)
        test.expect(dstl_select_sms_message_format(test.r1))
        test.expect(dstl_set_sms_center_address(test.r1))
        test.expect(test.r1.at1.send_and_verify('AT+CSMP=17,167,0,0'))

    def run(test):
        test.log.h2("Executing script for: TC0102336.001 PSMeDRXLongTimeOperationNonTransparentUDP")

        test.log.step("1) enable PSM and eDRX on DUT module.")
        test.expect(dstl_enable_psm(test.dut, '', '', '00111000', '00001111'))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXS=2,4,1001'))

        test.log.step("2) Set up both DUT and Remote as non-transparent UDP socket endpoints. "
                      "Save DUT's internet profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        srv_id = '0'
        test.udp_endpoint = SocketProfile(test.dut, srv_id, connection_setup.dstl_get_used_cid(),
                                          protocol='UDP', port=65100)
        test.udp_endpoint.dstl_generate_address()
        test.expect(test.udp_endpoint.dstl_get_service().dstl_load_profile())
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'save', srv_id))

        test.log.step("3) Open Remote endpoint.")
        test.echo_server = EchoServer("IPv4", 'UDP', test_duration=2)

        test.log.step("4) Reboot the DUT module. Attach to the network again.")
        test.expect(dstl_restart(test.dut))
        dstl_enter_pin(test.dut)
        test.expect(dstl_select_sms_message_format(test.dut))
        test.expect(dstl_delete_all_sms_messages(test.dut))
        test.expect(dstl_set_preferred_sms_memory(test.dut))
        test.expect(dstl_enable_sms_urc(test.dut))

        test.log.step("5) Verify network service of the DUT.")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("6) Open UDP profiles on DUT and Remote.")
        test.expect(dstl_execute_sips_command(test.dut, 'service', 'load', srv_id))
        test.expect(test.udp_endpoint.dstl_get_service().dstl_open_service_profile())

        data_package_size = 1000
        data_packages = 10
        server_address_and_port = '{}:{}'.format(test.echo_server.dstl_get_server_ip_address(),
                                                 test.echo_server.dstl_get_server_port())
        iterations = 16
        for iteration in range(1, iterations+1):
            test.log.step("7) Verify if the module is able to enter power saving mode "
                          "(Connected->Idle->PSM)."
                          "\r\nIteration no. {} of {}".format(iteration, iterations))
            test.expect(test.check_if_module_enters_psm_mode_with_sms())
            test.expect(dstl_delete_all_sms_messages(test.dut))

            test.log.step("8) Periodically send 10 x 1000 bytes of random ASCII data from DUT to "
                          "Remote when DUT is in PSM and receive/read echo data."
                          "\r\nIteration no. {} of {}".format(iteration, iterations))
            test.expect(test.udp_endpoint.dstl_get_service()
                        .dstl_send_sisw_command_and_data_UDP_endpoint(data_package_size,
                                        udp_rem_client=server_address_and_port,
                                        eod_flag='0', repetitions=data_packages, delay_in_ms=200))
            test.expect(test.udp_endpoint.dstl_get_service().dstl_read_data(data_package_size,
                                                                            repetitions=data_packages))

            test.log.step("9) Check Internet service state on DUT side."
                          "\r\nIteration no. {} of {}".format(iteration, iterations))
            test.expect(test.udp_endpoint.dstl_get_parser().dstl_get_service_state()
                        == ServiceState.UP.value)
            test.expect(test.udp_endpoint.dstl_get_parser().dstl_get_service_data_counter('rx')
                        >= data_packages*data_package_size*0.8)

            test.log.step("10) Repeat {} (or more) times - steps 7)-9)".format(iterations-iteration))

        test.expect(test.udp_endpoint.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem with closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        try:
            test.expect(test.udp_endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.udp_endpoint.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("SocketProfile object was not created.")
        test.expect(dstl_disable_psm(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXS=0'))
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
