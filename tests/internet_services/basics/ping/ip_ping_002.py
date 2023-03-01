#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0024329.002, TC0024329.005

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin
from threading import Thread


class Test(BaseTest):
    """ TC intention: This test checks ping functionality. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.ip_server = EchoServer("IPv4", "TCP", extended=True)

        test.execute_step_1()

        test.used_address = test.ip_server.dstl_get_server_ip_address()
        test.ping_execution = InternetServiceExecution(test.dut, test.cid)

        test.execute_step_2(request_1=10, request_2=1, request_3=30)

        test.log.step("3. Call ping command with different <request> values that do not match the allowed range (-1/0/31)")
        cmd_error = ".*ERROR.*"
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=-1, expected_response=cmd_error))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=0, expected_response=cmd_error))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=31, expected_response=cmd_error))

        test.execute_step_4(timelimit_1=500, timelimit_2=5000, timelimit_3=10000)

        test.log.step("5. Call ping command with different <timelimit> values that do not match the allowed range 198/199/10001)")
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=198, expected_response=cmd_error))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=199, expected_response=cmd_error))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=10001, expected_response=cmd_error))

        test.execute_steps_6_to_8()

        test.log.step("9. Deactivate connection profile or PDP context")
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

        test.log.step("10. Try to call ping command")
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, expected_response=cmd_error))

        test.log.step("11. Repeat steps 1,2,4,6-8 using FQDN address and different values for <timelimit> and <request>")
        test.used_address = test.ip_server.dstl_get_server_FQDN()
        test.execute_step_1()
        test.execute_step_2(request_1=7, request_2=18, request_3=26)
        test.execute_step_4(timelimit_1=480, timelimit_2=1312, timelimit_3=8654)
        test.execute_steps_6_to_8()

    def execute_step_1(test):
        test.log.step("1. Define connection profile or PDP context and activate it.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()
        test.dut_ip_addresses = test.connection_setup.dstl_get_pdp_address()

    def execute_step_2(test, request_1, request_2, request_3):
        test.log.step("2. Call ping command with different <request> values ({}/{}/{})".format(request_1, request_2, request_3))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=request_1))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= request_1 * 0.2)
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=request_2))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= request_2 * 0.2)
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=request_3))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= request_3 * 0.2)

    def execute_step_4(test, timelimit_1, timelimit_2, timelimit_3):
        test.log.step("4. Call ping command with different  <timelimit> values ({}/{}/{})"
                      .format(timelimit_1, timelimit_2, timelimit_3))
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=timelimit_1))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= 10 * 0.2)
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=timelimit_2))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= 10 * 0.2)
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=10, timelimit=timelimit_3))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[2] <= 10 * 0.2)

    def execute_steps_6_to_8(test):
        threads = [Thread(target=test.execute_step_6), Thread(target=test.block_unblock_icmp)]
        for thread in threads:
            thread.start()
        for thread in threads[::-1]:
            thread.join()

    def execute_step_6(test):
        test.log.step("6. Call ping command with equals 30")
        test.expect(test.ping_execution.dstl_execute_ping(test.used_address, request=30,
                                                          check_packet_statistics=False))
        test.expect(test.ping_execution.dstl_get_packet_statistic()[3] > 0)
        test.expect(test.ping_execution.dstl_get_packet_statistic()[3] < 100)

    def block_unblock_icmp(test):
        if test.dut.project == "VIPER":
            test.sleep(0.3)
        else:
            test.sleep(1)
        test.log.step("7. During the ping execution, activate a firewall that the \"pinged\" host is not reachable")
        test.expect(test.ip_server.dstl_server_block_ping_function(test.dut_ip_addresses[0]))

        test.log.step("8. After some not successful ping requests, the firewall is deactivated " +
                      "--> the host is reachable again")
        test.sleep(16)
        test.is_icmp_accepted = test.expect(test.ip_server.dstl_server_accept_ping_function())

    def cleanup(test):
        try:
            test.ip_server.dstl_server_close_port()
            if not test.is_icmp_accepted:
                test.expect(test.ip_server.dstl_server_accept_ping_function())
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
