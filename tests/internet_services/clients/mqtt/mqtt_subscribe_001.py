# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0102387.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    TC0102387.001 - MqttSubscribe

    DESCRIPTION
   1. Create MQTT client profile mandatory parameters only.
    Dynamic MQTT parameters will be used during connection.
        srvType - "Mqtt"
        conId - e.g. 0
        address - mqtt://<host>:<port>
    2. Open MQTT Client profile using SISO command.
     Set <optParam> to 2 - dynamic parameters OR dynamic request.
    3. Check if correct URCs appears.
    4. Configure mandatory SUBSCRIBE mode parameters using SISD command:
        Cmd - "Subscribe"
        topicFilter - e.g. "test_topic1;testtopic2;topic312345;topic4;topic_@555"
         (For some products to set special characters GSM03.38 in Setting2 in Yaat need to be used).
    5. Send request using SISU command.
    6. Check if correct URCs appears and socket/srv state.
    7. Send publish request with one of the topic from server or using other service profile.
    8. Check if SISR URC appear and read data.
    9. Check socket and srv state.
    10. Check server log.
    11. Close MQTT Client profile.

    INTENTION
    To check basic SUBSCRIBE connection with MQTT server

    """

    def setup(test):
        test.topic_filter = "test/basic"
        test.topic = "mqtttest"
        test.client_id = "mqttSub001"
        test.data = "some test data"
        test.qos = "0"

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("=== TC0102387.001 - MqttSubscribe ===")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('=== 1. Create MQTT client profile mandatory parameters only.\n \
                    Dynamic MQTT parameters will be used during connection.\n \
                    srvType - "Mqtt" \n \
                    conId - e.g. 0 \n \
                    address - mqtt://<host>:<port> ===')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
            topic=test.topic, topic_filter=test.topic_filter, client_id=test.client_id)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('=== 2. Open MQTT Client profile using SISO command.\
                    Set <optParam> to 2 - dynamic parameters OR dynamic request. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))

        test.log.step('=== 3. Check if correct URCs appears. ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))
        test.expect(f"Received SUBSCRIBE from {test.client_id}" and
                    f"{test.client_id} {test.qos} {test.topic_filter}" in
                    test.mqtt_server.dstl_read_data_on_ssh_server())

        test.log.step('=== 4. Configure mandatory SUBSCRIBE mode parameters using SISD command: \n \
                    Cmd - "Subscribe" \n \
                    topicFilter - e.g. "test_topic1;testtopic2;topic312345;topic4;topic_@555". ===')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_mqtt_cmd('subscribe'))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_topic_filter(test.topic))

        test.log.step('=== 5. Send request using SISU command. ===')
        test.expect(test.mqtt_client.dstl_get_dynamic_service().dstl_sisu_send_request())

        test.log.step('=== 6. Check if correct URCs appears and socket/srv state. ===')
        test.log.info("=== URC was checked in previous step ===")
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)
        test.expect(f"Received SUBSCRIBE from {test.client_id}" and
                    f"{test.client_id} {test.qos} {test.topic}" in
                    test.mqtt_server.dstl_read_data_on_ssh_server())

        test.log.step('=== 7. Send publish request with one of the topic from server or using '
                      'other service profile. ===')
        test.expect(test.mqtt_server.
                    dstl_mqtt_publish_send_request(topic=test.topic, data=test.data))

        test.log.step('=== 8. Check if SISR URC appear and read data. ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared(urc_cause_id='1'))
        test.expect(test.mqtt_client.dstl_get_service()
                    .dstl_read_return_data(len(test.data)) == test.data)

        test.log.step('=== 9. Check socket and srv state. ===')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('=== 10. Check server log. ===')
        test.log.info('=== Corresponding checks were done after proper steps. ===')

        test.log.step('=== 11. Close MQTT Client profile. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()
        test.sleep(10)

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn('Problem during closing port on server.')
        except AttributeError:
            test.log.error('Server object was not created.')
        test.mqtt_client.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()
