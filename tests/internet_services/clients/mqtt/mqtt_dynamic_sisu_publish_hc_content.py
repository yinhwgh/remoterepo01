#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0102381.001, TC0102381.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState, Command


class Test(BaseTest):
    """ To check PUBLISH connection using dynamic hcContent request with MQTT server"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0102381.001/003 MqttDynamicSisuPublishHcContent'")
        topic = 'Test TC0102381.001/003 MqttDynam'
        hc_content = 'Test data12'
        client_id = 'TestModule0987654321666'
        qos = '1'
        retain = 0
        data_amount_0 = 0
        fqdn_address = test.mqtt_server.dstl_get_server_FQDN()
        test.expect(test.mqtt_server.dstl_run_mqtt_server())
        test.sleep(2)

        test.log.step('1. Create MQTT client PUBLISH profile. Dynamic MQTT request will be used during connection.\r\n'
                      'In address field set connackTimeout parameter\r\n srvType - "Mqtt" \r\nconId - e.g. 0'
                      '\r\naddress - mqtt://<host>:<port>;connackTimeout=7')
        test.mqtt_client_publish = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                               cmd="publish", topic=topic, client_id=client_id, connack_timeout="60")
        test.mqtt_client_publish.dstl_set_host(fqdn_address)
        test.mqtt_client_publish.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open MQTT Client profile using SISO command. \r\n"
                      "Set <optParam> to 2 – dynamic parameters OR dynamic request")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile(opt_param='2'))

        test.log.step("3. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.sleep(3)

        test.log.step('4. Send request using SISU command. \r\n e.g. e.g. AT^SISU=0,"publish","1:price:1:35:0"')
        test.expect(test.mqtt_client_publish.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_publish(qos, topic, retain, hc_content, data_amount_0))

        test.log.step("5. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "3520", '"{}"'.format(topic)))

        test.log.step("6. Check response of the AT^SISI? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_READ) ==
                    ServiceState.UP.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("TX", at_command=Command.SISI_READ) == len(hc_content))
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("RX", at_command=Command.SISI_READ) == 0)

        test.log.step("7. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step("8. Check response of the AT^SISI? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state(at_command=Command.SISI_READ) ==
                    ServiceState.ALLOCATED.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("TX", at_command=Command.SISI_READ) == data_amount_0)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("RX", at_command=Command.SISI_READ) == data_amount_0)

        test.log.step("9. Check server log")
        test.expect(test.mqtt_server.dstl_check_publish_request(client_id, topic, len(hc_content), qos, retain))
        test.sleep(5)
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile()
        test.mqtt_client_publish.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
