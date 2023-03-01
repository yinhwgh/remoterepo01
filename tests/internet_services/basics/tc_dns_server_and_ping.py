#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0085355.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.execution.internet_service_execution import InternetServiceExecution
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC intention: Setting right/wrong DNS1 and DNS2 address and activate context.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.ip_server = EchoServer("IPv4", "TCP")
        test.incorrect_dns1 = "192.168.50.50"
        test.incorrect_dns2 = "192.168.50.51"
        test.correct_dns1 = "8.8.8.8"
        test.correct_dns2 = "8.8.4.4"
        test.requests_number = 10

    def run(test):
        restart_needed = test.dut.project == "SERVAL" or "VIPER"
        test.log.step("1. Enter PIN if not entered yet.")
        dstl_enter_pin(test.dut)

        test.log.step("2. Define PDP context.")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())
        test.cid = test.connection_setup.dstl_get_used_cid()

        test.log.step("3. Define correct based on IPv4: dns1 and dns2 values (eg. Google DNS).")
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns1\",\"{}\"".format(test.cid, test.correct_dns1)))
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns2\",\"{}\"".format(test.cid, test.correct_dns2)))

        test.log.step("4. Activate defined context (if applicable - restart the module and enter the PIN earlier).")
        if restart_needed:
            test.restart_and_enter_pin(test)
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("5. Ping chosen site (FQDN) with 10 repetitions.")
        ip_server_address = test.ip_server.dstl_get_server_FQDN()
        ping_execution = InternetServiceExecution(test.dut.at1, test.cid)
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number))
        # additional check if % of lost packets is not grater than 20%
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= test.requests_number*0.2)

        test.log.step("6. Deactivate context.")
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

        test.log.step("7. Define wrong dns1.")
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns1\",\"{}\"".format(test.cid, test.incorrect_dns1)))

        test.log.step("8. Activate defined context (if applicable - restart the module and enter the PIN earlier).")
        if restart_needed:
            test.restart_and_enter_pin(test)
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("9. Ping chosen site (FQDN) with 10 repetitions.")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= test.requests_number*0.2)

        test.log.step("10. Deactivate context.")
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

        test.log.step("11. Define wrong dns1 and dns2.")
        test.log.info("Wrong dns1 was already defined in Step 7.")
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns2\",\"{}\"".format(test.cid, test.incorrect_dns2)))

        test.log.step("12. Activate defined context (if applicable - restart the module and enter the PIN earlier).")
        if restart_needed:
            test.restart_and_enter_pin(test)
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("13. Ping chosen site (FQDN) with 10 repetitions.")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number))
        test.expect(len(ping_execution.dstl_get_time_statistic())==0)

        test.log.step("14. Deactivate context.")
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

        test.log.step("15. Define correct dns2.")
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns2\",\"{}\"".format(test.cid, test.correct_dns2)))

        test.log.step("16. Activate defined context (if applicable - restart the module and enter the PIN earlier).")
        if restart_needed:
            test.restart_and_enter_pin(test)
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("17. Ping chosen site (FQDN) with 10 repetitions.")
        test.expect(ping_execution.dstl_execute_ping(ip_server_address, request=test.requests_number))
        test.expect(ping_execution.dstl_get_packet_statistic()[2] <= test.requests_number*0.2)

        test.log.step("18. Deactivate context.")
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())

    def cleanup(test):
        test.log.info("Restoring DNS settings to default values.")
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns1\",\"0.0.0.0\"".format(test.cid)))
        test.expect(test.dut.at1.send_and_verify("AT^SICS={},\"dns2\",\"0.0.0.0\"".format(test.cid)))
        try:
            test.ip_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

    @staticmethod
    def restart_and_enter_pin(test):
        test.log.info("Serval detected - additional module restart is needed to use the new DNS addresses.")
        dstl_restart(test.dut)
        dstl_enter_pin(test.dut)
        test.dut.at1.send_and_verify("AT^SICS?")


if "__main__" == __name__:
    unicorn.main()
