# responsible: lijuan.li@thalesgroup.com
# location: Beijing
# TC0106041.001

import re
import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.devboard.devboard import dstl_turn_off_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_vbatt_via_dev_board
from dstl.auxiliary.devboard.devboard import dstl_turn_on_igt_via_dev_board


class Test(BaseTest):
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.dut.devboard.send_and_verify("MC:urc=off common", ".*OK.*")
        test.dut.devboard.send_and_verify("MC:time=on", ".*OK.*")
        test.ip_version = 'ipv4'
        test.totaltime1 = 0
        test.totaltime2 = 0
        test.counts = 0

    def smso_thread(test):
        test.dut.devboard.send('AT^SMSO')
        test.dut.devboard.wait_for('PWRIND: 1')

        try:
            response = test.dut.devboard.last_response
            begin_str = 'ASC0: AT^SMSO'
            end_str = 'PWRIND: 1'
            index1 = response.index(begin_str) - 11
            index2 = response.index(end_str) + len(end_str)
            response = response[index1:index2]
            # test.log.info('*****response is\n' + response)
            response = response.replace("\n", "")
            response_list = response.split()
            new_response = ''.join(response_list)
            test.log.info('*****new response is\n' + new_response)
            startTime = re.search(r'(\d+)>ASC0:AT\^SMSO', new_response).group(1)
            estimatedTime1 = re.search(r'(\d+)>ASC0:\^SHUTDOWN', new_response).group(1)
            interval1 = int(estimatedTime1) - int(startTime)
            estimatedTime2 = re.search(r'(\d+)>URC:PWRIND:1', new_response).group(1)
            interval2 = int(estimatedTime2) - int(estimatedTime1)

            test.log.info("Time spent for URC SHUTDOWN : {}".format(interval1))
            test.log.info("Time spent from SHUTDOWN to Power off : {}".format(interval2))

            test.counts = test.counts + 1
            test.totaltime1 = test.totaltime1 + interval1
            test.totaltime2 = test.totaltime2 + interval2
        except:
            test.log.error("Can't count time this loop, please check the log")

        dstl_turn_off_vbatt_via_dev_board(test.dut)
        test.sleep(5)
        dstl_turn_on_vbatt_via_dev_board(test.dut)
        test.sleep(5)
        dstl_turn_on_igt_via_dev_board(test.dut)
        test.dut.at1.wait_for('SYSSTART', 60)

    def run(test):
        iterations = 3000
        data_lenth = 1500

        test.log.info("Executing script for test case: 'TcLoadSendReceiveTcpClient_{}'".format(test.ip_version))

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.echo_server = EchoServer(test.ip_version, "TCP", test_duration=2)

        for iteration in range(iterations + 1):
            test.expect(dstl_enter_pin(test.dut))
            test.log.step(
                "1) Define connection profile or define and activate PDP context""\nIteration: {} of {} - start.".format(
                    iteration, iterations))

            connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version)
            test.expect(connection_setup_object.dstl_load_internet_connection_profile())
            test.expect(connection_setup_object.dstl_activate_internet_connection(), critical=True)

            test.log.step("2) Set {} TCP client socket profile on module".format(test.ip_version))

            test.socket = SocketProfile(test.dut, "1", connection_setup_object.dstl_get_used_cid(), protocol="tcp",
                                        alphabet=1, ip_version=test.ip_version)
            test.socket.dstl_set_parameters_from_ip_server(test.echo_server)
            test.socket.dstl_generate_address()
            test.expect(test.socket.dstl_get_service().dstl_load_profile())

            test.log.step("3) Open service and connect to echo TCP server and wait for write URC. ")

            test.expect(test.socket.dstl_get_service().dstl_open_service_profile(expected=".*O.*"))
            if 'OK' not in test.dut.devboard.last_response:
                test.expect(False, msg="Service was not successfully opened, current iteration will be skipped.")
                test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
                continue
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Send the following data from module to TCP server: \na. 1460 bytes \nb. 12 bytes. "
                          "\nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(data_lenth))

            test.log.step("5) Read data received from TCP echo server. "
                          "\nIteration: {} of {}".format(iteration, iterations))

            test.expect(test.socket.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.socket.dstl_get_service().dstl_read_data(data_lenth)

            test.log.step("6) Release connection. \nIteration: {} of {}".format(iteration, iterations))
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            test.dut.at1.read(append=True)
            test.dut.devboard.read(append=True)

            test.smso_thread()

            if iteration != iterations:
                test.log.step("8) Repeat steps from 1) to 7) {} times using {} profile. "
                              "\nIteration: {} - end.".format(iterations, test.ip_version, iteration))

    def cleanup(test):
        averagetime1 = test.totaltime1 / test.counts
        averagetime2 = test.totaltime2 / test.counts

        test.log.info("Average time for URC pop is {}ms".format(averagetime1))
        test.log.info("Average time from SHUTDOWN to power down is {}ms".format(averagetime2))


if __name__ == "__main__":
    unicorn.main()