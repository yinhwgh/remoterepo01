#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0095086.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
import time
class Test(BaseTest):
	"""Testing basic functionality of TCP socket client in non transparent mode including sending End Of Data flag"""

	def setup(test):
		test.check_local_configuration()
		test.dut.dstl_detect()

	def run(test):
		test.log.step('1.Enter PIN and attach module to the network.')
		test.log.step('2.Activate URC mode.')
		test.log.step('3.Depends on product: set Connection Profile (GPRS) / Define PDP Context.')
		test.expect(test.dut.dstl_register_to_network())
		test.expect(test.dut.dstl_set_scfg_tcp_with_urcs("on"))
		connection_setup_dut = dstl_get_connection_setup_object(test.dut)
		test.log.step(
			'4.Setup Internet Service Profile for Transparent UDP Client to the remote UDP Endpoint set etx only for compatibility')
		socket_client = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
		                              protocol="udp", host=test.udp_echo_server_address, port=test.udp_echo_server_port,empty_etx=True)
		socket_client.dstl_generate_address()
		test.expect(socket_client.dstl_get_service().dstl_load_profile())
		test.log.step('5.Depends on product - Activate PDP context.')
		test.expect(connection_setup_dut.dstl_activate_internet_connection())
		test.log.step('6.Check for address assignment.')
		test.expect(test.dut.at1.send_and_verify("AT+CGPADDR={}".format(connection_setup_dut.dstl_get_used_cid()), r".*OK.*"))
		for i in range(1,30):
			test.log.step('7.Open the service and wait for proper URC.')
			test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
			test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
			test.log.step('8.Switch to transparent Mode.')
			test.expect(socket_client.dstl_get_service().dstl_enter_transparent_mode())
			test.log.step('9.Send 1024KB and wait for 2048KB of data.')
			for i in range(0, 256):
				test.expect(socket_client.dstl_get_service().dstl_send_data(dstl_generate_data(4096), expected=""))
				time.sleep(3)
			test.log.step('10.Switch to command mode')
			test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
			test.log.step('11.Check amount of send and received data.')
			test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1024 * 1024)
			test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 1024 * 1024)
			test.log.step('12.Close the connection.')
			test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
			test.log.step('13.Wait 2s and repeat step 7-12 29 times.')
			time.sleep(2)

	def cleanup(test):
		pass
	def check_local_configuration(test):
		try:
			test.udp_echo_server_address
			test.udp_echo_server_port
		except AttributeError:
			test.log.error('Please configure udp_echo_server_address and udp_echo_server_port in local.cfg')


if "__main__" == __name__:
	unicorn.main()
