#responsible: marek.kocela@globallogic.com
#location: Wroclaw
#TC0105062.001

import unicorn
import time
from time import gmtime
from time import strftime
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Short description:
       To check Module stability while sending and receiving UDP data when eDRX is enabled.

       Detailed description:
       1. Attach Module to NW
       2. Define UDP Client profile (connection to any UDP server)
       3. Open Profile
       4. Send 10KB of data to server and receive 10KB of data from server
       5. Wait 5 minutes
       6. Send 2KB of data to server
       7. Wait 10 minutes
       8. Receive 2KB of data from server
       9. Wait 15 minutes
       10. Send 5KB of data to server
       11. Wait 20 minutes
       12. Receive 5KB of data from server
       13. Wait 60 minutes
       14. Repeat steps 4 - 13 for at least 24 hours"""


    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.log.info("Enable eDRX on DUT with 5.12s eDRX cycle")
        test.expect(test.dut.at1.send_and_verify('AT+CEDRXS=1,4,"0000"', ".*OK.*"))

        test.log.info("Disable PSM on DUT")
        test.expect(test.dut.at1.send_and_verify('AT+CPSMS=0', ".*OK.*"))

        test.log.info("Enable network registration status")
        test.expect(test.dut.at1.send_and_verify('AT+CEREG=5', ".*OK.*"))



    def run(test):

        test.data_block_size_1024 = 1024
        one_loop_repetitions = 17
        test.log.info("Executing script for test case: TC0105062.001 - UDP_eDRX_duration")

        test.log.step("1) Attach Module to NW")
        test.expect(dstl_enter_pin(test.dut))
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Define UDP Client profile (connection to any UDP server)")
        test.udp_client = SocketProfile(test.dut, 0, connection_setup_object.dstl_get_used_cid(), protocol="udp")
        test.echo_server = EchoServer("IPv4", "UDP", test_duration=25)
        test.udp_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.udp_client.dstl_generate_address()
        test.expect(test.udp_client.dstl_get_service().dstl_load_profile())

        test.log.step("3) Open Profile")
        test.expect(test.udp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.udp_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.steps_from_4_to_13()

        test.log.step("14) Repeat steps 4 - 13 for at least 24 hours")
        # 60s * 60m * 24h = 24 hours
        period_time = 60 * 60 * 24
        end_time = time.time() + period_time
        test.sleep(10)

        loop_counter = 1

        while time.time() < end_time:
            test.log.info("Remaining time :{}".format(strftime("%H:%M:%S", gmtime(end_time - time.time()))))
            test.steps_from_4_to_13()
            test.expect(test.udp_client.dstl_get_parser().dstl_get_service_data_counter("TX") ==
                        loop_counter * one_loop_repetitions * test.data_block_size_1024)
            test.expect(test.udp_client.dstl_get_parser().dstl_get_service_data_counter("RX") >=
                        loop_counter * one_loop_repetitions * test.data_block_size_1024 * 0.8)
            loop_counter += 1
        else:
            test.log.info("TC0105062.001 - UDP_eDRX_duration has been ended")

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            else:
                test.log.info("The server port has been closed successfully.")
            test.expect(test.udp_client.dstl_get_service().dstl_close_service_profile())
            test.dut.at1.send_and_verify('AT+CEDRXS=0', ".*OK.*")
            test.dut.at1.send_and_verify('AT&F', ".*OK.*")
            test.dut.at1.send_and_verify('AT&W', ".*OK.*")

        except AttributeError:
            test.log.error("Object was not created.")

    def steps_from_4_to_13(test):
        test.log.step("4) Send 10KB of data to server and receive 10KB of data from server")
        test.expect(test.udp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.data_block_size_1024,
                                                                                       repetitions=10))
        test.expect(test.udp_client.dstl_get_service().dstl_read_data(test.data_block_size_1024, repetitions=10))

        test.log.step("5) Wait 5 minutes")
        test.sleep(300)

        test.log.step("6) Send 2KB of data to server")
        test.expect(test.udp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.data_block_size_1024,
                                                                                       repetitions=2))

        test.log.step("7) Wait 10 minutes")
        test.sleep(600)

        test.log.step("8) Receive 2KB of data from server")
        test.expect(test.udp_client.dstl_get_service().dstl_read_data(test.data_block_size_1024, repetitions=2))

        test.log.step("9) Wait 15 minutes")
        test.sleep(900)

        test.log.step("10) Send 5KB of data to server")
        test.expect(test.udp_client.dstl_get_service().dstl_send_sisw_command_and_data(test.data_block_size_1024,
                                                                                       repetitions=5))

        test.log.step("11) Wait 20 minutes")
        test.sleep(1200)

        test.log.step("12) Receive 5KB of data from server")
        test.expect(test.udp_client.dstl_get_service().dstl_read_data(test.data_block_size_1024, repetitions=5))

        test.log.step("13) Wait 60 minutes")
        test.sleep(3600)


if "__main__" == __name__:
    unicorn.main()
