#responsible: lei.chen@thalesgroup.com
#location: Dalian
#TC0093708.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import SocketState


class Test(BaseTest):
    """ 
    TC0093708.002 - TcpSocketTransparentBasic_IPv4
    TC0093709.002 - TcpSocketTransparentBasic_IPv6
    Intention:
    Testing TCP Socket Transparent Client, including Nagle algorithm timer.
    Testing correct data transmission between modules, socket states and operation of different ways of escaping from transparent mode to command mode.

    description:
    1. Attach modules to the network
    2. Set up internet services for TCP Transparent Socket Client on DUT 
    and TCP Transparent Socket Listener on Remote. Explicitly set up the service to use IPv4. Set Nagle timer to [T =] 20. [E =] ETX not set
    3. Establish connection between modules and enter transparent data mode.
    4. Send [nTx =] 50x (1000 bytes ASCII string) from DUT to Remote, while Remote constantly reads the data.
    5. Escape transparent mode with [ESC =] +++ sequence.
    6. Check socket state and Tx data counter - if +++ sequence is used then the count of data will equal nTx+3 (depending on product).
    7. Enter transparent mode again and receive [nRx =] 5x (1500 bytes ASCII string) from Remote
    8. Escape transparent mode with [ESC =] +++ sequence.
    9. Check socket state, Rx data counter, ackData and unackData
    10. Close connection and check socket state.
    11. Release service profiles on both modules.

    Repeat steps 2-11 with following variations:
    B) T => 480; E => not set;    nTx => 50x (1000 bytes ASCII string); ESC => DTR Toggle;    nRx => 5x (1500 bytes ASCII string).
    C) T => 480; E => ETX=26;     nTx => 50x (1000 bytes ASCII string); ESC => ETX character; nRx => 5x (1500 bytes ASCII string).
    D) T => 20;  E => ETX=26;     nTx => 100x (10 bytes ASCII string);  ESC => ETX character; nRx => 5x (1500 bytes ASCII string); 
    Instead of executing 4-8 in sequence, DUT and Remote send data at the same time. 
    Remote (server) finishes first and sends EOD before all data are sent from DUT (client).
    E) T => 20;  E => ETX=26;     nTx => 50x (1000 bytes ASCII string); ESC => ETX character; 
    nRx => 4x (1445 bytes ASCII string); Last block received by DUT shall contain EOD at the end. Step 8 shall be omitted.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.r1.dstl_detect()
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.dut.dstl_set_scfg_tcp_with_urcs("on")
        test.r1.dstl_set_scfg_tcp_with_urcs("on")

    def run(test):
        if test.ip_version == "IPv4":
            test.log.info("TC0093708.002 - TcpSocketTransparentBasic_IPv4")
            test.ip_version_number = "4"
        else:
            test.log.info("TC0093709.002 - TcpSocketTransparentBasic_IPv6")
            test.ip_version_number = "6"
            
        test.log.step("1.  Attach modules to the network")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.r1.dstl_register_to_network())

        escape_sequance_offset = 3
        
        variables = [[20, None, 50, 1000, '+++', 5, 1500],
                     [480, None, 50, 1000, 'DTR Toggle', 5, 1500],
                     [480, '26', 50, 1000, 'ETX', 5, 1500],
                     [20, '26', 100, 10, 'ETX', 5, 1500],
                     [20, '26', 50, 1000, 'ETX', 4, 1445],
        ]

        for variable in variables:
            t, etx, number_of_blocks_sent_from_client, bytes_to_send_from_client, esc_method,\
                number_of_blocks_sent_from_server, bytes_to_send_from_server = variable

            test.log.step(f"2. Set up internet services for TCP Transparent Socket Client on DUT "
                          f"and TCP Transparent Socket Listener on Remote.\
            Explicitly set up the service to use {test.ip_version}. Set Nagle timer to [T = "
                          f"{t}]. [E = {etx}] ")
            test.connection_setup_dut = dstl_get_connection_setup_object(test.dut,
                                                                         ip_version=test.ip_version)
            test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

            test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True,
                                                                        ip_version=test.ip_version)
            test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

            test.log.h3("Define and open TCP listener service on remote.")
            test.socket_server = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                               host="listener", localport=8888, etx_char="26",
                                               ip_version=test.ip_version_number)

            test.socket_server.dstl_generate_address()
            test.socket_server.dstl_get_service().dstl_load_profile()

            test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_server.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
           
            test.log.step("3. Establish connection between modules and enter transparent data mode.")
            test.log.h3(f"Define and open TCP client on DUT, set nagle_timer parameter to {t}, etx to {etx}.")
            server_ip = test.socket_server.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version=test.ip_version).split(":")

            test.socket_dut = SocketProfile(test.dut, 0,
                                            test.connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp", host=server_ip[0], port=server_ip[1],
                                            nagle_timer=t, etx_char=etx,
                                            ip_version=test.ip_version_number)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.h3("Accept client connection on listener side.")
            test.expect(test.socket_server.dstl_get_urc().dstl_is_sis_urc_appeared())
            test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
            test.expect(test.socket_server.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step(f"4. Send [nTx =] {number_of_blocks_sent_from_client}x ({bytes_to_send_from_client} \
                bytes ASCII string) from DUT to Remote, while Remote constantly reads the data")
            for i in range(number_of_blocks_sent_from_client):
                bytes_generated = dstl_generate_data(bytes_to_send_from_client)
                test.expect(test.socket_dtls.dstl_get_service().dstl_send_data(bytes_generated))
            
            test.log.step(f"5. Escape transparent mode with [ESC = {esc_method}]  sequence")
            test.exit_transparent_mode(esc_method)

            test.log.step(f"6. Check socket state and Tx data counter - \
            if +++ sequence is used then the count of data will equal nTx+3 (depending on product).")
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
            tx_data = test.socket_dut.dstl_get_parser().dstl_get_service_data_counter('TX')
            tx_expect = number_of_blocks_sent_from_client * bytes_to_send_from_client
            test.log.info(f"Read data length is {tx_data}, expect data length is {tx_expect}(+{escape_sequance_offset*2})")
            test.expect(tx_data == tx_expect or tx_data == tx_expect + escape_sequance_offset*2)

            test.log.step(f"7. Enter transparent mode again and receive [nRx = {number_of_blocks_sent_from_server}x\
                 ({bytes_to_send_from_server} bytes ASCII string) from Remote")
            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
            test.expect(test.socket_server.dstl_get_service().dstl_enter_transparent_mode())
            for i in range(number_of_blocks_sent_from_server):
                bytes_generated = dstl_generate_data(bytes_to_send_from_server)
                test.expect(test.socket_dtls.dstl_get_service().dstl_send_data(bytes_generated))

            test.log.step(f"8. Escape transparent mode with [ESC = {esc_method}] sequence.")
            test.exit_transparent_mode(esc_method)

            test.log.step(f"9. Check socket state, Rx data counter, ackData and unackData")
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
            rx_data = test.socket_dut.dstl_get_parser().dstl_get_service_data_counter('RX')
            rx_expect = number_of_blocks_sent_from_server * bytes_to_send_from_server
            test.log.info(f"Read data length is {rx_data}, expect data length is {rx_expect}")
            test.expect(tx_data == rx_expect)
            ack_data = test.socket_dut.dstl_get_parser().dstl_get_service_ack_data()
            unpack_data = test.socket_dut.dstl_get_parser().dstl_get_service_unack_data()
            test.log.info(f"ACK data is {ack_data}.")
            test.log.info(f"unpack data is {unpack_data}.")
            test.expect(ack_data + unpack_data == tx_expect)

    def cleanup(test):
        test.log.step(f"10. Close connection and check socket state")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)

        test.log.step(f"11. Release service profiles on both modules")
        test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())

    def exit_transparent_mode(test, esc_method):
        if esc_method == "+++":
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.r1.dstl_switch_to_command_mode_by_pluses())
        elif 'DTR' in esc_method:
            test.expect(test.dut.dstl_switch_to_command_mode_by_dtr())
            test.expect(test.r1.dstl_switch_to_command_mode_by_dtr())
        elif 'ETX' in esc_method:
            test.expect(test.dut.dstl_switch_to_command_mode_by_etxchar(26))
            test.expect(test.r1.dstl_switch_to_command_mode_by_etxchar(26))


if "__main__" == __name__:
    unicorn.main()
