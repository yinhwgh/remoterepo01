# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105938.001 - GPSDuringTCPsocket_stress_test
# Hints:
# Some parameters should be defined in local.cfg currently,such as echo_server_address, srv_id,
# network_instrument__resource_string = 'GPIB0::28::INSTR' and etc.

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.gnss.gnss import *
from dstl.gnss.smbv import *
from dstl.network_service import register_to_network
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import Command, ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile

class Test(BaseTest):
    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        err_text = 'no SMBV found -> stop testcase'
        test.smbv = SMBV(test.plugins.network_instrument)

        if test.smbv.dstl_check_smbv():
            test.log.com("Setting SMBV")
            test.smbv.dstl_smbv_switch_on_all_system()
        else:
            all_results.append([err_text, 'FAILED'])
            test.log.error(err_text)
            test.expect(False, critical=True)

        test.dut.dstl_detect()

    def run(test):

        test.log.step('Step 1: Module registers to NBIOT network.')
        test.expect(test.dut.dstl_register_to_nbiot())
        test.log.step('Step 2: Configure IP service bearer and TCP socket, then Open TCP service.')
        connection_setup_dut = test.dut.dstl_get_connection_setup_object()
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        client_profile = SocketProfile(test.dut, test.srv_id, connection_setup_dut.dstl_get_used_cid(),
                                       protocol="tcp",
                                       address=test.echo_server_address)
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.expect(client_profile.dstl_get_service().dstl_open_service_profile())
        test.expect(client_profile.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.sleep(2)

        test.log.step('Step 3: Initialise GNSS engine to default setting')
        test.dut.dstl_collect_result('Step 1: Initialise GNSS engine to default setting', test.dut.dstl_init_gnss(restart=False))

        times = 0
        while times < 100:
            test.log.step('Step 4: Send some data through TCP service (for example: 10 bytes).')
            test.log.step('Step 5: Switch on GNSS engine.')
            test.log.step('Step 6: Repeat steps4-5 for 20min and check module’s network registration.')

            test.log.info(
                '************************ ITERATION NUMBER: ' + str(times + 1) + ' *****************************')



            test.dut.dstl_collect_result('Step 5: Switch on GNSS engine', test.dut.dstl_switch_on_engine(3))
            # token = time.time()
            # test.dut.at1.wait_for('.*GSA,A,3.*|.*GSA,A,2.*', 100)
            # ttff = time.time() - token
            # test.dut.dstl_collect_result('Step 6: Determine TTFF 1/27/29 sec (hot/warm/cold): ' + str(ttff), ttff < 30)
            test.sleep(5)
#            test.expect(test.dut.at1.send_and_verify("at+cops?", ".*OK.*"))
            test.dut.dstl_collect_result('Step 6: Switch off GNSS engine', test.dut.dstl_switch_off_engine())
            time.sleep(10)
            test.expect(client_profile.dstl_get_service().dstl_send_sisw_command_and_data(10))
            test.expect(client_profile.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
            test.expect(client_profile.dstl_get_service().dstl_send_sisr_command_and_data(10))
            test.expect(test.dut.at1.send_and_verify("at+cops?", ".*OK.*"))
            test.expect(client_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
            times += 1

        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        test.smbv.dstl_smbv_close()
        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
