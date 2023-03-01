#responsible: shuang.liang@thalesgroup.com
#location: Beijing
#TC0104573.001 Actia_Configuration_HTTPS_GSM
#Hints:
#The parameters such as srv_id, http_server and http_server_port should be defined in local.cfg currently.
#Take an example: http_server="10.163.27.30"

import unicorn
import time
import datetime
import re
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import restart_module
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.http_profile import HttpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState

class Test(BaseTest):
    """  This case is intended to get configuration data through HTTPS connection upon GSM network. """

    def setup(test):

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_get_imei()
        test.dut.dstl_set_scfg_tcp_with_urcs("on")


    def run(test):

        # srv_id = 1
        # http_server = '10.163.27.30'
        # http_server_port = 80
        # secopt = 1

        test.log.info("TC0104573.001 - Actia_Configuration_HTTPS_GSM")
        test.log.info('***************************** Test Begin ******************************')
        test.log.step('Step 1: The module registers to GSM network via UART')
        test.expect(test.dut.dstl_register_to_gsm())

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


        test.log.step(
            'Step 5: Download configuration data about 200 Bytes.')
        http_client.dstl_get_service().dstl_read_return_data(200)

        test.expect(http_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.log.step('Step 6:. Close HTTPS service.')
        test.expect(http_client.dstl_get_service().dstl_close_service_profile())

        test.log.info('********** TC0104573.001 - Actia_Configuration_HTTPS_GSM" END **************')

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
