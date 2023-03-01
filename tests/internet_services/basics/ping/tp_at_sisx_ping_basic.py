#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0094345.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: This procedure provides the possibility of basic tests for the test and write command of At^SISX
    for parameter <service>="Ping".
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_server = EchoServer(ip_version="IPv4", protocol="TCP")
        test.ip_server_address = test.ip_server.dstl_get_server_ip_address()

    def run(test):
        min_requests = 1
        max_requests = 30
        min_timelimit = 200
        max_timelimit = 10000
        requests_number = 4
        test.allowed_loss_percentage = 10
        test.log.step("1. Restart the module (AT+CFUN=1,1) and wait for URC ^SYSSTART.")
        test.expect(dstl_restart(test.dut))

        test.log.step("2. Define internet connection profile or PDP context.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. Try to set test command (AT^SISX=?).")
        test.expect(test.dut.at1.send_and_verify("AT^SISX=?", expect="CME ERROR: SIM PIN required",
                                                 wait_for="CME ERROR: SIM PIN required", timeout=10))

        test.log.step("4. Try to set write command (AT^SISX=ping,x,\"[IP_Address]\").")
        test.ping_execution = InternetServiceExecution(test.dut, cid)
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address,
                                                          expected_response="CME ERROR: SIM PIN required"))

        test.log.step("5. Enter PIN.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("6. Detach from PS network.")
        test.expect(connection_setup.dstl_detach_from_packet_domain())

        test.log.step("7. Check test command (AT^SISX=?).")
        test.expect(test.dut.at1.send_and_verify("AT^SISX=?", expect="OK", wait_for="OK", timeout=10))
        test.expect("SISX: \"Ping\",(1-16),,({}-{}),({}-{})"
                    .format(min_requests, max_requests, min_timelimit, max_timelimit) in test.dut.at1.last_response)
        test.expect("SISX: \"HostByName\",(1-16)" in test.dut.at1.last_response)
        test.expect("SISX: \"Ntp\",(1-16)" in test.dut.at1.last_response)

        test.log.step("8. Check write command with correct parameters (AT^SISX=ping,x,\"[IP_Address]\",4).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, request=requests_number,
                                                          expected_response="CME ERROR: no network service"))

        test.log.step("9. Attach to PS network and activate PDP context if applicable.")
        test.expect(connection_setup.dstl_activate_internet_connection())

        test.log.step("10. Check write command with correct parameters (AT^SISX=ping,x,\"[IP_Address]\").")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK"))
        packet_statistic = test.ping_execution.dstl_get_packet_statistic()
        test.expect(packet_statistic[0] == min_requests)
        test.expect(packet_statistic[1] == min_requests)

        test.log.step("11. Check write command with correct parameters (AT^SISX=ping,x,\"[IP_Address]\",4).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK",
                                                          request=requests_number))
        packet_statistic = test.ping_execution.dstl_get_packet_statistic()
        test.expect(packet_statistic[0] == requests_number)
        test.expect(packet_statistic[1] >= requests_number * 0.9)
        test.expect(packet_statistic[3] < test.allowed_loss_percentage)

        test.log.step("12. Check write command with correct parameters (AT^SISX=ping,x,\"[IP_Address]\",8,1000).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK",
                                                          request=8, timelimit=1000))
        test.verify_ping_stats(requests_number=8)

        test.log.step("13. Set parameter <request=0> with command (AT^SISX=ping,x,\"[IP_Address]\",0).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, request=0,
                                                          expected_response="CME ERROR: invalid index"))

        test.log.step("14. Set parameter <request=max of supported value> with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",<max of supported value>).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK",
                                                          request=max_requests))
        test.verify_ping_stats(requests_number=max_requests)

        test.log.step("15. Set parameter <request=max of supported value + 1 more> with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",<max of supported value + 1 more>).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, request=max_requests + 1,
                                                          expected_response="CME ERROR: invalid index"))

        test.log.step("16. Set parameter <timelimit=min of supported value - 1 value > with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",1,<min of supported value - 1 value >).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, timelimit=min_timelimit - 1,
                                                          request=1, expected_response="CME ERROR: invalid index"))

        test.log.step("17. Set parameter <timelimit=min of supported value> with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",30,<min of supported value>).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK",
                                                          request=max_requests, timelimit=min_timelimit))
        test.verify_ping_stats(requests_number=max_requests)

        test.log.step("18. Set parameter <timelimit=max of supported value> with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",2,<max of supported value>).")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, expected_response="OK",
                                                          request=2, timelimit=max_timelimit))
        test.verify_ping_stats(requests_number=2)

        test.log.step("19. Set parameter <timelimit=max of supported value + 1 more> with command (AT^SISX=ping,x,"
                      "\"[IP_Address]\",3,<max of supported value + 1 more>). ")
        test.expect(test.ping_execution.dstl_execute_ping(address=test.ip_server_address, timelimit=max_timelimit + 1,
                                                          request=3, expected_response="CME ERROR: invalid index"))

    def verify_ping_stats(test, requests_number):
        packet_statistic = test.ping_execution.dstl_get_packet_statistic()
        test.expect(packet_statistic[0] == requests_number)
        test.expect(packet_statistic[1] >= requests_number * 0.9)
        test.expect(packet_statistic[3] <= test.allowed_loss_percentage)

    def cleanup(test):
        try:
            if not test.ip_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
