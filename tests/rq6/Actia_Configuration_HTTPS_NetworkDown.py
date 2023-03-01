#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0104576.001 Actia_Configuration_HTTPS_NetworkDown
#Hints:
#The parameters such as srv_id, http_server and http_server_port should be defined in local.cfg currently.
#Take an example: http_server="10.163.27.30"
#For this script, you should install win32api. If not, error will occur.

import unicorn
import time
import datetime
import re
import random

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service import register_to_network
from dstl.configuration import shutdown_smso
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar

class Test(BaseTest):

    """
         This case will test to get configuration data through HTTPS connection at the end of the next trip
         when the network is available again, if no network is available.
    """

    def setup(test):

        test.require_package('win32api')
        
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_get_imei()
        test.dut.dstl_set_scfg_tcp_with_urcs("on")


    def run(test):

        import win32api

        # srv_id = 1
        # http_server = '10.163.27.30'
        # http_server_port = 80
        # secopt = 1

        test.log.info("TC0104576.001 - Actia_Configuration_HTTPS_NetworkDown")
        test.log.info('***************************** Test Begin ******************************')
        test.log.step('Step 1: The module registers to Cat.M network via UART')
        test.expect(test.dut.dstl_register_to_lte())

        test.log.step('Step 2: Set properties')
        test.log.info("2.1. Enables extended status information +CREG.")
        test.expect(test.dut.at1.send_and_verify('at+creg=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        test.log.info("2.2. Enable error result code with verbose (string) values.")
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        test.log.info("2.3. activate DCD line for internet service (at&c=2)")
        test.expect(test.dut.at1.send_and_verify('AT&C2', '.*OK.*'))
        test.log.info("2.4. Display current configuration.")
        test.expect(test.dut.at1.send_and_verify('at&v', '.*OK.*'))

        test.log.step('Step 3: Define HTTPS connection context.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object()
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        con_id = connection_setup_dut.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, 1, con_id, http_command="get", host=test.https_server_ipv4,
                                  port=test.https_server_port_ipv4, secopt=1, secure_connection=True)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.log.step('Step 4: Open HTTPS connection.')
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                    '"Http connect {}:{}"'.format(test.https_server_ipv4, test.https_server_port_ipv4)))
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.sleep(2)

        test.log.info('Step 5: Adjust attenuator to make network unavailable')
        try_time = 0
        while (try_time < 3):
            win32api.MessageBox(0, "Please adjust attenuator to make network unavailable! Then click 'OK' button.",
                                "MessageBox", 0)
            time.sleep(3)
            test.dut.at1.send_and_verify('AT^SMONI', append=False)
            if '^SMONI: Searching' in test.dut.at1.last_response or '^SMONI: SEARCH' in test.dut.at1.last_response:
                test.log.info('Network is unavailable now!')
                break
            else:
                test.log.error('Network is still available, please adjust attenuator!')
                try_time = try_time + 1
        time.sleep(5)


        test.log.info('Step 6: Adjust attenuator to make network available again and the module shuts down.')
        test.expect(test.dut.dstl_shutdown_smso())

        test.log.step('Step 7: The module registers to Cat.M network via UART')
        test.expect(test.dut.dstl_register_to_lte())

        test.log.step('Step 8: Set properties')
        test.log.info("8.1. Enables extended status information +CREG.")
        test.expect(test.dut.at1.send_and_verify('at+creg=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        test.log.info("8.2. Enable error result code with verbose (string) values.")
        test.expect(test.dut.at1.send_and_verify('at+cmee=2', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        test.log.info("8.3. activate DCD line for internet service (at&c=2)")
        test.expect(test.dut.at1.send_and_verify('AT&C2', '.*OK.*'))
        test.log.info("8.4. Display current configuration.")
        test.expect(test.dut.at1.send_and_verify('at&v', '.*OK.*'))
        test.log.info("8.5. Enables Ciphering Status Change Indication.")
        test.expect(test.dut.at1.send_and_verify('at^sind=is_cert,1', '.*OK.*'))

        test.log.step('Step 9: Configure IPv4 or IPv6 transparent TCPS socket connection.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object()
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        client_profile = SocketProfile(test.dut, 1, connection_setup_dut.dstl_get_used_cid(),
                                       protocol='tcp', host=test.tcps_echo_server_ipv4, port=test.tcps_echo_server_port_ipv4,
                                       etx_char='26', secopt=1, secure_connection=True)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.log.step('Step 10: Open transparent TCPS socket.')
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.dut.at1.wait_for('SISW: ' + str(1) + ',1')
        test.sleep(2)

        test.log.step(
            'Step 11: Enter transparent mode and send data about 500B~2KB every 5 minutes during a long time(10 hours).')
        test.expect(client_profile.dstl_get_service().dstl_enter_transparent_mode())

        tStart = time.time()
        times = 0
        # Send buffered data every 5 minutes, keep 10 hours
        while (time.time() - tStart - 300 * times >= 0):
            test.log.info(
                '************************ ITERATION NUMBER: ' + str(times + 1) + ' *****************************')
            sBufferedDataIn = 'A'
            randomnumber = random.randint(500, 2048)
            for i in range(1, randomnumber):
                sBufferedDataIn = sBufferedDataIn + 'A'
            test.dut.at1.send(sBufferedDataIn)
            test.dut.devboard.send('AT')
            test.dut.devboard.send_and_verify('MC:ASC0', append=False)
            if '>MC:   DCD0: 0' in test.dut.devboard.last_response:
                test.log.info('PASS: Response OK.')
            else:
                test.log.error('FAIL: Response NOK')

            time.sleep(300)  # 5 minutes interval
            times += 1
            if times == 120:
                break

        test.log.info('Step 12: Send summary data 2KB~3KB.')
        sSummaryDataIn = 'B'
        for i in range(1024 * 2, 1024 * 3):
            sSummaryDataIn = sSummaryDataIn + 'B'
        test.dut.at1.send(sSummaryDataIn)

        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, int('26')))
        test.expect(client_profile.dstl_get_parser().dstl_get_service_state(at_command=Command.SISO_WRITE)
                    == ServiceState.UP.value)

        test.log.info('Step 13: Close TCPS service.')
        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

        test.log.step('Step 14: Define HTTPS connection context.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object()
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        con_id = connection_setup_dut.dstl_get_used_cid()
        http_client = HttpProfile(test.dut, 1, con_id, http_command="get", host=test.https_server_ipv4,
                                  port=test.https_server_port_ipv4, secopt=1, secure_connection=True)
        http_client.dstl_generate_address()
        test.expect(http_client.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.log.step('Step 15: Open HTTPS connection.')
        test.expect(http_client.dstl_get_service().dstl_open_service_profile())
        test.expect(http_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2200",
                                                                        '"Http connect {}:{}"'.format(test.https_server_ipv4,
                                                                                                      test.https_server_port_ipv4)))
        test.expect(http_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
        test.sleep(2)

        test.log.step(
            'Step 16: Download configuration data about 200 Bytes.')
        http_client.dstl_get_service().dstl_read_return_data(200)

        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.log.step('Step 17:. Close HTTPS service.')
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())

        test.log.info('********** TC0104576.001 - Actia_Configuration_HTTPS_NetworkDown END **************')

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
