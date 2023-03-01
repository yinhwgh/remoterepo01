# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0102390.003

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ TC0102390.003 - MqttDynamicSisuUnsubscribe

    DESCRIPTION
    1. Create MQTT client publish profile mandatory parameters only. Dynamic MQTT parameters will be
    used during connection.
        srvType - "Mqtt"
        conId - e.g. 0
        address - mqtt://<host>:<port>
    2. Open MQTT Client profile using SISO command. Set <optParam> to 2 – dynamic parameters OR
    dynamic request
    3. Check if correct URCs appears.
    4. Send SUBSCRIBE request using AT^SISU=profileId command with parameters:
        - topicFilter - fuel/level
        - topicQos - 0
    5. Check if correct URC appears.
    6. Check server log
    7. Send UNSUBSCRIBE request using AT^SISU=profileId command with parameters:
        - topicFilter - fuel/level
    8. Check if correct URC appears.
    9. Check server log
    10. Check service state using AT^SISO? command.
    11. Close MQTT Client profile.

    INTENTION
    To check UNSUBSCRIBE connection with MQTT server

    """

    def setup(test):
        test.topic = "fuel/level"
        test.client_id = "sisuUnsub003"
        test.qos = '0'

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.expect(dstl_set_error_message_format(test.dut))

    def run(test):
        test.log.info('=== TC0102390.003 - MqttDynamicSisuUnsubscribe ===')
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client publish profile mandatory parameters only.'
                      'Dynamic MQTT parameters will be used during connection.\n srvType - "Mqtt"\n'
                      'conId - e.g. 0\n address - mqtt://<host>:<port>')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(),
            cmd='publish', topic=test.topic, client_id=test.client_id)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('2. Open MQTT Client profile using SISO command. '
                      'Set <optParam> to 2 – dynamic parameters OR dynamic request.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))

        test.log.step('3. Check if correct URCs appears.')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))

        test.log.step('4. Send SUBSCRIBE request using AT^SISU=profileId command with parameters:'
                      '\n- topicFilter - fuel/level\n- topicQos - 0')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_subscribe(topic_filter=test.topic, topic_qos=test.qos))

        test.log.step('5. Check if correct URC appears.')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '2520', f'"{test.topic}"'))

        test.log.step('6. Check server log.')
        test.mqtt_server.dstl_check_subscribe_request(test.dut, test.client_id, test.topic)

        test.log.step('7. Send UNSUBSCRIBE request using AT^SISU=profileId command with parameters:'
                      '\n- topicFilter - fuel/level')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_unsubscribe(topic_filter=test.topic))

        test.log.step('8. Check if correct URC appears.')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2510", f'"{test.topic}"'))

        test.log.step('9. Check server log.')
        test.mqtt_server.dstl_check_unsubscribe_request(test.dut, test.client_id, test.topic)

        test.log.step('10. Check service state using AT^SISO? command.')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('11. Close MQTT Client profile.')
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