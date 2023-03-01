# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0102380.001, TC0102380.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState, Command
from dstl.internet_service.profile.mqtt_profile import MqttProfile


class Test(BaseTest):
    """ To check PUBLISH connection using dynamic hcContLen parameter with MQTT server """

    def setup(test):
        dstl_detect(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_error_message_format(test.dut)
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: "
                      "'TC0102380.001/002 MqttDynamicSisdPublishHcContLen'")
        topic = 'temp/outdoor'
        client_id = dstl_get_imei(test.dut)
        qos = '0'
        hc_cont_len = '6'
        srv_id = '1'
        data_amount = 3
        retain = '0'

        test.log.step('1. Create MQTT client PUBLISH profile. Dynamic MQTT parameters will be'
                      ' used during connection. \r\nIn address field set connackTimeout parameter '
                      '\r\nsrvType - "Mqtt" \r\nconId - e.g. 0 '
                      '\r\naddress - mqtt://<host>:<port>')
        test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=180))
        test.mqtt_client_publish = MqttProfile(test.dut, srv_id,
                                               test.connection_setup.dstl_get_used_cid(),
                                               alphabet=1, cmd="publish", topic=topic,
                                               client_id=client_id)
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        dynamic_service = test.mqtt_client_publish.dstl_get_dynamic_service()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())
        test.sleep(2)

        test.log.step("2. Open MQTT Client profile using SISO command. Set <optParam> to 2 "
                      "– dynamic parameters OR dynamic request")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile(
            opt_param='2'))

        test.log.step("3. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step('4. Configure PUBLISH mode parameters using SISD command: '
                      '\r\nCmd - "Publish" \r\nTopic - "temp/outdoor"\r\nhcContLen - 6 ')
        test.expect(dynamic_service.dstl_sisd_set_param_mqtt_cmd('publish'))
        test.expect(dynamic_service.dstl_sisd_set_param_topic(topic))
        test.expect(dynamic_service.dstl_sisd_set_param_hc_cont_len(hc_cont_len))
        test.expect(dynamic_service.dstl_sisd_get_all_parameters())

        test.log.step("5. Send request using SISU command")
        test.expect(dynamic_service.dstl_sisu_send_request(polling_mode=True))

        test.log.step("6. Write 3 bytes of data")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_send_sisw_command_and_data(
            data_amount))

        test.log.step("7. Write again 3 bytes of data")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_send_sisw_command_and_data(
            data_amount))

        test.log.step("8. Check response of the AT^SISI? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state(
            at_command=Command.SISI_READ) == ServiceState.UP.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_socket_state() ==
                    SocketState.CLIENT.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("TX", at_command=Command.SISI_READ) == data_amount*2)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("RX", at_command=Command.SISI_READ) == 0)

        test.log.step("9. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Check response of the AT^SISI? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state(
            at_command=Command.SISI_READ) ==
                    ServiceState.ALLOCATED.value)
        test.expect(
            test.mqtt_client_publish.dstl_get_parser().dstl_get_socket_state() ==
            SocketState.NOT_ASSIGNED.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("TX", at_command=Command.SISI_READ) == 0)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter
                    ("RX", at_command=Command.SISI_READ) == 0)

        test.log.step("11. Check server log")
        test.expect(
            test.mqtt_server.dstl_check_publish_request(client_id, topic, data_amount*2, qos,
                                                        retain))
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
