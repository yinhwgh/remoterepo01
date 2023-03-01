#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0093703.001 ,TC0093704.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses

class Test(BaseTest):
    """
    TC0093703.001 - MultipleTransparentTcpListeners_IPv4
    TC0093704.001 - MultipleTransparentTcpListeners_IPv6
    Check if module supports only one Transparent TCP Listener connection per interface.
    Check if on module can be established more than one Transparent TCP connection simultaneously on different interfaces
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_detect(test.r1)
        dstl_restart(test.dut)
        dstl_restart(test.r1)
        dstl_enter_pin(test.dut)
        dstl_enter_pin(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on", device_interface="at2")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        if test.ip_version == 'IPv6':
            test.dut.at1.send_and_verify('AT+CGPIAF=1', ".*O.*")
        test.srv_id_1 = 1
        test.srv_id_2 = 2

    def run(test):

        test.log.step('1) Define PDP context on DUT and Remote and activate them')
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version,ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_version=test.ip_version)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2) On DUT define and open Transparent TCP Listener profiles (separately for each interface which supports it).')
        test.socket_dut_at1 = SocketProfile(test.dut, test.srv_id_1, connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=50000, etx_char=26,ip_version=test.ip_version)
        test.socket_dut_at2 = SocketProfile(test.dut, test.srv_id_2, connection_setup_dut.dstl_get_used_cid(),device_interface='at2', protocol="tcp",
                                        host="listener", localport=60000, etx_char=26, ip_version=test.ip_version)

        test.log.step('3) On Remote define and open Transparent TCP Clients. Accept connections on DUT.')
        test.socket_dut_at1.dstl_generate_address()
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.socket_dut_at2.dstl_generate_address()
        test.expect(test.socket_dut_at2.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut_at2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at2.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        dut_ip_address = test.socket_dut_at1.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version=test.ip_version).split(":")[0]
        test.socket_client_1 = SocketProfile(test.r1, test.srv_id_1, connection_setup_r1.dstl_get_used_cid(),
                                              protocol="tcp", host=dut_ip_address, port=50000,ip_version=test.ip_version)
        test.socket_client_2 = SocketProfile(test.r1, test.srv_id_2, connection_setup_r1.dstl_get_used_cid(),
                                              protocol="tcp", host=dut_ip_address, port=60000,ip_version=test.ip_version)
        test.socket_client_1.dstl_generate_address()
        test.expect(test.socket_client_1.dstl_get_service().dstl_load_profile())
        test.socket_client_2.dstl_generate_address()
        test.expect(test.socket_client_2.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_client_1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client_2.dstl_get_service().dstl_open_service_profile())

        test.expect(test.socket_dut_at1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(test.socket_dut_at2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut_at2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step('4) Enter data mode on DUT.')
        test.expect(test.socket_dut_at1.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_dut_at2.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step('5) Send 200 bytes of data for each opened profile on every interface.')

        data_1 = dstl_generate_data(200)
        data_2 = dstl_generate_data(200)
        test.expect(
            test.socket_dut_at1.dstl_get_service().dstl_send_data(data_1, expected=""))
        test.expect(test.r1.at1.wait_for('.*\^SISR: 1,1\s.*'))
        test.expect(test.r1.at1.send_and_verify('AT^SISR=1,200',data_1))
        test.expect(
            test.socket_dut_at2.dstl_get_service().dstl_send_data(data_2, expected=""))
        test.expect(test.r1.at1.wait_for('.*\^SISR: 2,1\s.*'))
        test.expect(test.r1.at1.send_and_verify('AT^SISR=2,200', data_2))

        test.log.step('6) Close all transparent connections using +++ or switch DTR to off.')
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface='at2'))

        test.expect(test.socket_dut_at1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut_at2.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client_1.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client_2.dstl_get_service().dstl_close_service_profile())

        test.log.step('7) Delete all defined profiles.')
        test.expect(test.dut.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))
        test.expect(test.dut.at2.send_and_verify(f'at^siss={test.srv_id_2},"srvType","none"'))
        test.expect(test.r1.at1.send_and_verify(f'at^siss={test.srv_id_1},"srvType","none"'))
        test.expect(test.r1.at1.send_and_verify(f'at^siss={test.srv_id_2},"srvType","none"'))

    def cleanup(test):
        test.dut.at1.send_and_verify('AT+CGPIAF=0', ".*O.*")


if "__main__" == __name__:
    unicorn.main()
