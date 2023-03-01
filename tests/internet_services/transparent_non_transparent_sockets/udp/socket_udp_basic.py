#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0085357.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Testing UDP data transfer"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")

    def run(test):
        test.log.info("Executing script for test case: 'TC0085357.001 SocketUdpBasic'")

        test.log.step("1. DUT - Set PDP context and activate it or set Connection Profile")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version='IPv4', ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. DUT - Set UDP Endppoint Service Profile with localport = 1"
                      "(Non-Transparent UDP Endpoint \"sockudp://:<localPort>\")")
        test.socket_endpoint = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(),
                                             protocol="udp", localport='1')
        test.socket_endpoint.dstl_generate_address()
        test.expect(test.socket_endpoint.dstl_get_service().dstl_load_profile())

        test.log.step("3. DUT - Open connection wait for SIS URC")
        test.expect(test.socket_endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared("5"))
        dut_ip_address_and_port = test.socket_endpoint.dstl_get_parser()\
            .dstl_get_service_local_address_and_port('IPv4')

        test.log.step("4. Remote - Set PDP context and activate it or set Connection Profile")
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_version='IPv4')
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("5. Remote - Set UDP Client Service Profile - connection to DUT: "
                      "\"sockudp[s]://<host>:<remotePort>[;port=<localPort>]\"")
        test.socket_client = SocketProfile(test.r1, "1", connection_setup_dut.dstl_get_used_cid(),
                                           protocol="udp", address=dut_ip_address_and_port)
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("6. Remote - Open connection")
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("7. DUT - Send data 1460x5 = 7300 to remote UDP client")
        test.log.info("First send any data from client to endpoint to get IP address and port.")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(3))
        test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_endpoint.dstl_get_service().dstl_read_data(3))
        r1_ip_address_and_port = test.socket_endpoint.dstl_get_service().dstl_get_udp_rem_client()

        test.expect(test.socket_endpoint.dstl_get_service().dstl_send_sisw_command_and_data_UDP_endpoint(1460,
                                                                r1_ip_address_and_port, eod_flag='0', repetitions=5))

        test.log.step("8. DUT - Receive data from remote module 1460x5=7300")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1460, repetitions=5))
        test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_endpoint.dstl_get_service().dstl_read_data(1460, repetitions=5))

        test.log.step("9. DUT - Check Read URC ^SISR: x,1: receive data 1460x2 from other module without reading")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1460, repetitions=2))
        test.expect(test.socket_endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step("10. Remote - send 1460x20 bytes")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1460, repetitions=20))

        test.log.step("11. DUT - check rxdropped data(SISR: x,3 if supported for lost data)")
        test.log.info("'rxdropped' data is not supported for tested product - step will be skipped.")

        test.log.step("12. DUT - Read the rest of data and check amount of received data")
        test.expect(test.socket_endpoint.dstl_get_service().dstl_read_data(1460, repetitions=2+20))
        test.expect(test.socket_endpoint.dstl_get_parser().dstl_get_service_data_counter('rx') >= 0.8*1460*(5+2+20))

        test.log.step("13. Release connection")

    def cleanup(test):
        try:
            test.expect(test.socket_endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_endpoint.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_client.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
