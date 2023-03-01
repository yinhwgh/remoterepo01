# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0096164.001, TC0096164.002

import random
from time import gmtime, strftime, time

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service \
    import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.get_internet_service_error_report \
    import dstl_get_internet_service_error_report
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ TC intention: IPIS100223835, IPIS100218856 retests.
    Testing stability of FTP service working under weak network conditions. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.dut_addresses = test.connection_setup.dstl_get_pdp_address()
        test.ftp_server = FtpServer("IPv4", extended=True, test_duration=5)

    def run(test):
        test.log.info("Executing script for test case: 'TC0096164.001/002 "
                      "LoadFtpConnectInWeakNetworkConditions'")

        test.log.step("1) Set up 3 FTP PUT clients to the server - specify different file names. "
                      "Set TcpMR for each profile to maximum.")
        ftp_client_1 = test.define_ftp_put_service('1', 'file_1.txt')
        ftp_client_2 = test.define_ftp_put_service('2', 'file_2.txt')
        ftp_client_3 = test.define_ftp_put_service('3', 'file_3.txt')

        script_execution_time = 4*60*60
        end_time = time() + script_execution_time
        while time() < end_time:
            test.log.step("2) Set TCP Overall Timeout for each profile. Setting shall be different "
                          "on each profile and changed on each iteration. TcpOT <30,90>")
            overall_timeout_1 = random.randint(30, 50)
            ftp_client_1.dstl_set_tcp_ot(overall_timeout_1)
            test.expect(ftp_client_1.dstl_get_service().dstl_write_tcpot())
            overall_timeout_2 = random.randint(51, 70)
            ftp_client_2.dstl_set_tcp_ot(overall_timeout_2)
            test.expect(ftp_client_2.dstl_get_service().dstl_write_tcpot())
            overall_timeout_3 = random.randint(71, 90)
            ftp_client_3.dstl_set_tcp_ot(overall_timeout_3)
            test.expect(ftp_client_3.dstl_get_service().dstl_write_tcpot())

            test.log.step("3) Open each profile.")
            test.expect(ftp_client_1.dstl_get_service().dstl_open_service_profile())
            test.expect(ftp_client_2.dstl_get_service().dstl_open_service_profile())
            test.expect(ftp_client_3.dstl_get_service().dstl_open_service_profile())

            test.log.step("4) Write small amount of data on each profile. "
                          "Check Tx data count for each profile.")
            size = 100
            test.expect(ftp_client_1.dstl_get_service().dstl_send_sisw_command_and_data(size))
            test.expect(ftp_client_1.dstl_get_parser().dstl_get_service_data_counter('tx') == size)
            test.expect(ftp_client_2.dstl_get_service().dstl_send_sisw_command_and_data(size))
            test.expect(ftp_client_2.dstl_get_parser().dstl_get_service_data_counter('tx') == size)
            test.expect(ftp_client_3.dstl_get_service().dstl_send_sisw_command_and_data(size))
            test.expect(ftp_client_3.dstl_get_parser().dstl_get_service_data_counter('tx') == size)

            test.log.step("5) Block IP traffic on server side.")
            test.expect(test.ftp_server.dstl_server_block_incoming_traffic(test.dut_addresses[0]))

            test.log.step("6) Write small amount of data on each profile again, time between first "
                          "and last write is limited to 10% of current smallest TcpOT setting. "
                          "Start time count for each profile separately, right after service "
                          "accepted data to send.")
            test.sleep(overall_timeout_1/10)
            test.expect(ftp_client_1.dstl_get_service().dstl_send_sisw_command_and_data(size,
                                                                        skip_data_check=True))
            start_time_1 = time()
            test.sleep((overall_timeout_2-overall_timeout_1)/10)
            test.expect(ftp_client_2.dstl_get_service().dstl_send_sisw_command_and_data(size,
                                                                        skip_data_check=True))
            start_time_2 = time()
            test.sleep((overall_timeout_3-overall_timeout_2)/10)
            test.expect(ftp_client_3.dstl_get_service().dstl_send_sisw_command_and_data(size,
                                                                        skip_data_check=True))
            start_time_3 = time()

            test.log.step('7) Wait for "Connection timed out" URC, up to 180 seconds independently'
                          ' on each profile. Stop time count for each profile if URC received '
                          'or time limit exceeded.')
            test.check_timeout_urc('1', ftp_client_1, start_time_1, overall_timeout_1)
            test.check_timeout_urc('2', ftp_client_2, start_time_2, overall_timeout_2)
            test.check_timeout_urc('3', ftp_client_3, start_time_3, overall_timeout_3)

            test.log.step("8) Unblock IP traffic on server side.")
            test.expect(test.ftp_server.dstl_server_accept_incoming_traffic())

            test.log.step("9) Read Internet Service Error Report for each profile.")
            test.expect(dstl_get_internet_service_error_report(test.dut, '1', info_mode='1')
                        == ['20', 'Connection timed out'])
            test.expect(dstl_get_internet_service_error_report(test.dut, '2', info_mode='1')
                        == ['20', 'Connection timed out'])
            test.expect(dstl_get_internet_service_error_report(test.dut, '3', info_mode='1')
                        == ['20', 'Connection timed out'])

            test.log.step("10) Check service state and socket state for each profile.")
            test.check_service_and_socket_state(ftp_client_1, ServiceState.DOWN.value,
                                                SocketState.CLIENT.value)
            test.check_service_and_socket_state(ftp_client_2, ServiceState.DOWN.value,
                                                SocketState.CLIENT.value)
            test.check_service_and_socket_state(ftp_client_3, ServiceState.DOWN.value,
                                                SocketState.CLIENT.value)

            test.log.step("11) Close all opened service profiles. Check service state "
                          "and socket state for each profile.")
            test.expect(ftp_client_1.dstl_get_service().dstl_close_service_profile())
            test.expect(ftp_client_2.dstl_get_service().dstl_close_service_profile())
            test.expect(ftp_client_3.dstl_get_service().dstl_close_service_profile())
            test.check_service_and_socket_state(ftp_client_1, ServiceState.ALLOCATED.value,
                                                SocketState.NOT_ASSIGNED.value)
            test.check_service_and_socket_state(ftp_client_2, ServiceState.ALLOCATED.value,
                                                SocketState.NOT_ASSIGNED.value)
            test.check_service_and_socket_state(ftp_client_3, ServiceState.ALLOCATED.value,
                                                SocketState.NOT_ASSIGNED.value)

            test.log.step("12) Wait 5 minutes (FTP server releases sockets).")
            test.sleep(5*60)

            test.log.step("13) Repeat steps 2-12 for about 4 hours.")
            test.log.info("Remaining time: {}".format(strftime("%H:%M:%S",
                                                               gmtime(end_time - time()))))

    def cleanup(test):
        try:
            if not test.ftp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.ftp_server.dstl_ftp_server_clean_up_directories()
        except AttributeError:
            test.log.error("Object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def define_ftp_put_service(test, profile_id, file_name):
        ftp_client = FtpProfile(test.dut, profile_id, test.connection_setup.dstl_get_used_cid(),
                                alphabet="1", command="put", files=file_name, tcp_mr=30)
        ftp_client.dstl_set_parameters_from_ip_server(ip_server=test.ftp_server)
        ftp_client.dstl_generate_address()
        test.expect(ftp_client.dstl_get_service().dstl_load_profile())
        return ftp_client

    def check_timeout_urc(test, profile_id, ftp_client, start_time, overall_timeout):
        test.log.info('Checking SIS URC for profile no. {}'.format(profile_id))
        if test.expect(ftp_client.dstl_get_urc()
                               .dstl_is_sis_urc_appeared('0', '20', '"Connection timed out"', 180),
                       msg="Expected URC not appeared."):
            urc_end_time = int(time() - start_time)
            test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                          .format(urc_end_time, overall_timeout))
            test.expect(urc_end_time - overall_timeout < overall_timeout/10,
                        msg="URC appeared, but not in expected time.")

    def check_service_and_socket_state(test, ftp_client, service_state, socket_state):
        test.expect(ftp_client.dstl_get_parser().dstl_get_service_state() == service_state)
        test.expect(ftp_client.dstl_get_parser().dstl_get_socket_state() == socket_state)


if __name__ == "__main__":
    unicorn.main()
