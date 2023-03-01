#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0105203.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.network_service import network_monitor
from dstl.call import setup_voice_call
from dstl.auxiliary import restart_module
from dstl.configuration import set_autoattach
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer

class Test(BaseTest):
    """
    TC0105203.001 - CSFB_MO_MT_Call
    """
    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        test.expect(test.r1.dstl_register_to_network())
        test.echo_server = EchoServer(ip_version="IPv4", protocol="TCP")
        test.cid = "1"

    def run(test):
        test.log.step("1. Register module to LTE network.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"', "OK"))
        test.expect(test.dut.dstl_enable_ps_autoattach())
        test.expect(test.dut.dstl_restart())
        test.expect(test.dut.dstl_register_to_network())
        test.attempt(test.dut.at1.send_and_verify,"AT+COPS?", ",7\s+", sleep=5, retry=5)

        test.log.step("2. Establish TCP connection with echo server.")
        test.internet_connection_dut = dstl_get_connection_setup_object(test.dut, ip_version='IP', ip_public=False)
        test.internet_connection_dut.cgdcont_parameters['cid'] = test.cid
        test.internet_connection_dut.dstl_define_pdp_context()
        test.socket_client = SocketProfile(test.dut, "1", test.cid,
                                      protocol="tcp", etx_char=26)
        test.socket_client.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        test.internet_connection_dut.dstl_activate_internet_connection()
        test.log.info(f"Opening IP Service for TCP context {test.cid}.")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))
        test.send_and_read_data(keep_connection=True)

        test.log.step("3. Make a call from remote to DUT, DUT answer the call.")
        test.expect(test.r1.dstl_voice_call_by_number(test.dut, test.dut.sim.nat_voice_nr))
        test.sleep(2)
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=False, expect_status=0))
        fb_cs = test.dut.dstl_monitor_network_act()
        test.expect(fb_cs in ('2G','3G'))
        if fb_cs == '2G':
            test.log.step("3.1 Fall back to 2G, data connection lost, "
                          "impossible to send data as CSFB happened")
            test.send_and_read_data(keep_connection=False)
        else:
            test.log.step("3.2 Fall back to 3G, data connection kept, "
                          "possible to send data as CSFB - 3G happens")
            test.send_and_read_data(keep_connection=True)

        test.log.step('4. DUT release the call. Verify data connection re-established, and send data'
                      'is possible')
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        if fb_cs == '2G':
            test.expect(test.dut.at1.wait_for("\^SISR.*", append=True, timeout=10))
            test.expect(test.dut.dstl_monitor_network_act() == '4G')
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == test.data_100, msg=f'Echo data - "{read_data}" is not equal to sent data.')
        else:
            test.expect(test.dut.dstl_monitor_network_act() == '4G')
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == "", msg=f'Data should have been read during call.')

        test.send_and_read_data(keep_connection=True)

        test.log.step("5. Make a call from DUT to remote, remote answer the call. Data connection lost,"
                      "no possible to send data as CSFB happened")
        test.expect(test.dut.dstl_voice_call_by_number(test.r1, test.r1.sim.nat_voice_nr))
        test.sleep(2)
        test.expect(test.dut.dstl_check_voice_call_status_by_clcc(is_mo=True, expect_status=0))
        fb_cs = test.dut.dstl_monitor_network_act()
        test.expect(fb_cs in ('2G','3G'))
        if fb_cs == '2G':
            test.log.step("3.1 Fall back to 2G, data connection lost, "
                          "impossible to send data as CSFB happened")
            test.send_and_read_data(keep_connection=False)
        else:
            test.log.step("3.2 Fall back to 3G, data connection kept, "
                          "possible to send data as CSFB - 3G happens")
            test.send_and_read_data(keep_connection=True)

        test.log.step('6. DUT release the call. Verify data connection re-established, and send data'
                      'is possible')
        test.dut.dstl_release_call()
        test.r1.dstl_release_call()
        if fb_cs == '2G':
            test.expect(test.dut.at1.wait_for("\^SISR.*", append=True, timeout=10))
            test.expect(test.dut.dstl_monitor_network_act() == '4G')
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == test.data_100, msg=f'Echo data - "{read_data}" is not equal to sent data.')
        else:
            test.expect(test.dut.dstl_monitor_network_act() == '4G')
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == "", msg=f'Data should have been read during call.')
        test.send_and_read_data(keep_connection=True)


    def cleanup(test):
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.internet_connection_dut.dstl_deactivate_internet_connection())
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"', "OK"))
        test.expect(test.dut.dstl_restart())

    def send_and_read_data(test, keep_connection):
        test.expect(
            test.socket_client.dstl_get_service().dstl_send_sisw_command(req_write_length=100))
        test.data_100 = dstl_generate_data(100)
        test.expect(test.socket_client.dstl_get_service().dstl_send_data(test.data_100))
        if not keep_connection:
            test.expect(not test.dut.at1.wait_for("\^SISR.*", append=True, timeout=10))
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == "", msg='No data should be read when CSFB - 2G happens.')
        else:
            test.expect(test.dut.at1.wait_for("\^SISR.*", append=True, timeout=10))
            read_data = test.socket_client.dstl_get_service().dstl_read_return_data(100)
            test.expect(read_data == test.data_100, msg=f'Echo data - "{read_data}" is not equal to sent data.')



if '__main__' == __name__:
    unicorn.main()
