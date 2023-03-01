#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0102375.001, TC0102375.003

import unicorn
from re import search

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile


class Test(BaseTest):
    """ To check PUBLISH connection using dynamic hcContent parameter with MQTT server. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_set_error_message_format(test.dut))
        test.mqtt_server_port = 1883
        test.prepare_mqtt_server(test.mqtt_server_port)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0102375.001/003 "
                      "MqttDynamicSisdPublishHcContent'")
        topic = 'mqtttest'
        client_id = dstl_get_imei(test.dut)
        qos = '2'
        retain = '1'
        hc_content = 'hello world'
        test.srv_id = '1'

        test.log.step('1. Create MQTT client PUBLISH profile. Dynamic MQTT parameters will be used '
                      'during connection. \r\nIn address field set connackTimeout parameter \r\n'
                      'srvType - "Mqtt" \r\nconId - e.g. 0 \r\n'
                      'address - mqtt://<host>;connackTimeout=10')
        test.mqtt_client_publish = MqttProfile(test.dut, test.srv_id,
                                               test.connection_setup.dstl_get_used_cid(),
                                               alphabet=1, cmd="publish", topic=topic,
                                               client_id=client_id, connack_timeout=10)
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        dynamic_service = test.mqtt_client_publish.dstl_get_dynamic_service()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open MQTT Client profile using SISO command. Set <optParam> to 2 "
                      "– dynamic parameters OR dynamic request")
        test.expect(test.mqtt_client_publish.dstl_get_service().
                    dstl_open_service_profile(opt_param='2'))

        test.log.step("3. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step('4. Configure PUBLISH mode parameters using SISD command: \r\n'
                      'Cmd - "Publish" \r\nQos - 2 \r\nTopic - "mqtttest" \r\nRetain - 1 \r\n'
                      'hcContLen - 0 \r\nhcContent - "hello world"')
        test.expect(dynamic_service.dstl_sisd_set_param_mqtt_cmd('publish'))
        test.expect(dynamic_service.dstl_sisd_set_param_qos(qos))
        test.expect(dynamic_service.dstl_sisd_set_param_topic(topic))
        test.expect(dynamic_service.dstl_sisd_set_param_retain(retain))
        test.expect(dynamic_service.dstl_sisd_set_param_hc_cont_len('0'))
        test.expect(dynamic_service.dstl_sisd_set_param_hc_content(hc_content))
        test.expect(dynamic_service.dstl_sisd_get_all_parameters())

        test.log.step("5. Start subscribing topic 'mqtttest' on server side")
        test.expect(test.mqtt_server.dstl_mqtt_subscribe_send_request(topic, qos))

        test.log.step("6. Send request using SISU command")
        test.expect(dynamic_service.dstl_sisu_send_request(polling_mode=True))

        test.log.step("7. Check if correct URCs appears.")
        test.expect(f'SIS: {test.srv_id},0,3520,"{topic}"' in test.dut.at1.last_response)

        test.log.step("8. Check response of the AT^SISO? command")
        rem_addr = "{}:{}".format(test.mqtt_server.dstl_get_server_ip_address(),
                                  test.mqtt_server_port)
        test.check_siso_response('4', '2', len(hc_content), "\d+.\d+.\d+.\d+:\d+", rem_addr)

        test.log.step("9. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step("10. Check response of the AT^SISO? command")
        test.check_siso_response('2', '1', '0', "0.0.0.0:0", "0.0.0.0:0")

        test.log.step("11. Check if data was received by subscriber and stop subscribing data.")
        test.expect(hc_content in test.mqtt_server.dstl_mqtt_subscribe_read_data())
        test.mqtt_server.dstl_mqtt_subscribe_stop_request()

    def cleanup(test):
        try:
            test.mqtt_server.dstl_mqtt_subscribe_stop_request()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

    def prepare_mqtt_server(test, server_port):
        # this method allows to force usage of specific port 1883 on generic IP server
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.mqtt_server.dstl_server_close_port()
        test.mqtt_server.port_number = server_port
        test.mqtt_server.port_active = server_port
        test.mqtt_server._open_port()

    def check_siso_response(test, service_state, socket_state, rx_count, loc_addr, rem_addr):
        test.dut.at1.send_and_verify('AT^SISO?')
        siso_pattern = r'SISO: {},"Mqtt",{},{},0,{},"{}","{}"'.format(test.srv_id, service_state,
                                                                      socket_state, rx_count,
                                                                      loc_addr, rem_addr)
        test.log.info("Check if module response is matching with pattern: \r\n"
                      "{}".format(siso_pattern))
        test.expect(search(siso_pattern, test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
