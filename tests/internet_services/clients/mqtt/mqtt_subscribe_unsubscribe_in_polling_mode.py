#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0105114.001, TC0105114.002

import unicorn
from re import search

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import \
    dstl_check_siss_read_response


class Test(BaseTest):
    """ To check polling mode for SUBSCRIBE and UNSUBSCRIBE requests. """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.mqtt_server = MqttServer("IPv4", extended=True)

    def run(test):
        test.log.h2("Executing script for test case: "
                    "'TC0105114.001/002 MqttSubscribeUnsubscribeInPollingMode'")
        test.srv_id = '1'
        client_id = dstl_get_imei(test.dut)
        static_topic_filter = "main/topic"
        topic_filter = "car/range"
        topic_qos = '1'
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client SUBSCRIBE profile. Dynamic MQTT parameters will be '
                      'used during connection.\r\n'
                      'srvType - "Mqtt" \r\nconId - e.g. 0 \r\naddress - mqtt://<host>:<port>')
        test.mqtt_client_sub = MqttProfile(test.dut, test.srv_id,
                                           test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                           cmd="subscribe", topic_filter=static_topic_filter,
                                           client_id=client_id)
        test.mqtt_client_sub.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_sub.dstl_generate_address()
        client_service = test.mqtt_client_sub.dstl_get_service()
        client_dynamic_service = test.mqtt_client_sub.dstl_get_dynamic_service()
        test.expect(client_service.dstl_load_profile())

        test.log.step('2. Execute AT^SISS? an check if connection parameters are correct')
        dstl_check_siss_read_response(test.dut, [test.mqtt_client_sub])

        test.log.step('3. Open MQTT Client profile using SISO command. Set <optParam> to 2 '
                      '– dynamic parameters OR dynamic request')
        test.expect(client_service.dstl_open_service_profile(opt_param=2))

        test.log.step('4. Execute AT^SISE command and poll oldest unread event for MQTT profile.')
        test.sleep(20)
        test.check_sise_info('8800')
        test.check_sise_info('2500')
        test.check_sise_info('2520')
        test.expect(test.mqtt_server.dstl_check_subscribe_request(
            client_id, static_topic_filter, clear_buffer=True))

        test.log.step('5. Configure SUBSCRIBE mode parameters using SISD command: \r\n'
                      'Cmd - "Subscribe" \r\ntopicFilter - "car/range" \r\ntopicQos - 1')
        test.expect(client_dynamic_service.dstl_sisd_set_param_mqtt_cmd("subscribe"))
        test.expect(client_dynamic_service.dstl_sisd_set_param_topic_filter(topic_filter))
        test.expect(client_dynamic_service.dstl_sisd_set_param_topic_qos(topic_qos))

        test.log.step('6. Get current value of dynamic parameters defined by AT^SISD command. '
                      'Use "getParam" option')
        test.expect(client_dynamic_service.dstl_sisd_get_param("cmd") == 'subscribe')
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicFilter") == topic_filter)
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicQos") == topic_qos)

        test.log.step('7. Send request using SISU command')
        test.expect(client_dynamic_service.dstl_sisu_send_request(polling_mode=True))

        test.log.step('8. Execute AT^SISE command and poll oldest unread event for MQTT profile.')
        test.sleep(20)
        test.check_sise_info('2521', topic_filter)

        test.log.step('9. Check server response')
        test.expect(test.mqtt_server.dstl_check_subscribe_request(
            client_id, topic_filter, topic_qos))

        test.log.step('10. From server send PUBLISH package to topic "car/range"')
        data_to_publish = 'test data'
        test.expect(test.mqtt_server.dstl_mqtt_publish_send_request(topic_filter, data_to_publish))

        test.log.step('11. Execute AT^SISE command and poll oldest unread event for MQTT profile.')
        test.sleep(20)
        test.check_sise_info('3488', 'topic={}; bytes={}'.format(topic_filter, len(data_to_publish)))

        test.log.step('12. Query number of received bytes within internal buffers of module '
                      'using SISR command')
        test.expect(test.mqtt_client_sub.dstl_get_parser().
                    dstl_get_peek_value_of_data_to_read() == len(data_to_publish))

        test.log.step('13. Read received message using SISR command.')
        test.expect(client_service.dstl_read_return_data(100) == data_to_publish)

        test.log.step('14. Clean all parameters defined by SISD command')
        test.expect(client_dynamic_service.dstl_sisd_clean_param())

        test.log.step('15. Get current value of dynamic parameters defined by AT^SISD command')
        test.expect(client_dynamic_service.dstl_sisd_get_param("cmd") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicFilter") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicQos") == '')

        test.log.step('16. Check MQTT service state using AT^SISO? command.')
        test.expect(test.dut.at1.send_and_verify('AT^SISO?'))
        rem_addr = "{}:{}".format(test.mqtt_server.dstl_get_server_ip_address(),
                                  test.mqtt_server.dstl_get_server_port())
        siso_pattern = r'SISO: {},"Mqtt",4,2,{},0,"{}","{}"'.format(
            test.srv_id, len(data_to_publish), "\d+.\d+.\d+.\d+:\d+", rem_addr)
        test.log.info("Check if module response is matching with pattern: \r\n"
                      "{}".format(siso_pattern))
        test.expect(search(siso_pattern, test.dut.at1.last_response))

        test.log.step('17. Configure UNSUBSCRIBE mode parameters using SISD command: '
                      '\r\nCmd - "Unsubscribe" \r\ntopicFilter - "car/range"')
        test.expect(client_dynamic_service.dstl_sisd_set_param_mqtt_cmd("unsubscribe"))
        test.expect(client_dynamic_service.dstl_sisd_set_param_topic_filter(topic_filter))

        test.log.step('18. Get current value of ALL dynamic parameters defined by AT^SISD command')
        test.expect(client_dynamic_service.dstl_sisd_get_param("cmd") == 'unsubscribe')
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicFilter") == topic_filter)
        test.expect(client_dynamic_service.dstl_sisd_get_param("topicQos") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("topic") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("qos") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("retain") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("hcContent") == '')
        test.expect(client_dynamic_service.dstl_sisd_get_param("hcContLen") == '')

        test.log.step('19. Send request using SISU command')
        test.expect(client_dynamic_service.dstl_sisu_send_request(polling_mode=True))

        test.log.step('20. Execute AT^SISE command and poll oldest unread event for MQTT profile.')
        test.sleep(20)
        test.check_sise_info('2510')

        test.log.step('21. Check server response')
        test.expect(test.mqtt_server.dstl_check_unsubscribe_request(client_id, topic_filter))

        test.log.step('22. From server send PUBLISH package to topic "car/range"')
        new_data_to_publish = 'new test data'
        test.expect(test.mqtt_server.dstl_mqtt_publish_send_request(topic_filter,
                                                                    new_data_to_publish))

        test.log.step('23. Execute AT^SISE command and poll oldest unread event for MQTT profile.')
        test.sleep(20)
        test.check_sise_info('0')

        test.log.step('24. Query number of received bytes within internal buffers of module '
                      'using SISR command')
        test.expect(test.mqtt_client_sub.dstl_get_parser().
                    dstl_get_peek_value_of_data_to_read() == -2)

        test.log.step('25. Check AT^SISI response for MQTT profile')
        test.expect(test.dut.at1.send_and_verify('AT^SISI={}'.format(test.srv_id)))
        sisi_pattern = r'SISI: {},4,{},0,0,0'.format(test.srv_id, len(data_to_publish))
        test.log.info("Check if module response is matching with pattern: \r\n"
                      "{}".format(sisi_pattern))
        test.expect(search(sisi_pattern, test.dut.at1.last_response))

        test.log.step('26. Close MQTT Client profile.')
        test.expect(client_service.dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.mqtt_client_sub.dstl_get_service().dstl_close_service_profile()
        test.mqtt_client_sub.dstl_get_service().dstl_reset_service_profile()

    def check_sise_info(test, info_id, info_text=''):
        test.dut.at1.send_and_verify('AT^SISE={},1'.format(test.srv_id))
        expected_response = 'SISE: {},{}'.format(test.srv_id, info_id)
        if info_text:
            expected_response += ',"{}"'.format(info_text)
        test.log.info('Expected SISE response: {}'.format(expected_response))
        test.expect(expected_response in test.dut.at1.last_response)


if "__main__" == __name__:
    unicorn.main()
