# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0105032.001, TC0105032.002

import unicorn
from re import search

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Check <willFlag> and related parameters for MQTT connection. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Executing script for test case: 'MqttParamWillFlag'")
        test.timeout = 10
        test.keep_alive_10 = 10
        test.qos = '1'
        test.topic = 'mqtttest'
        test.client_id = '123clientId'
        test.hc_content = '12345'
        test.hc_cont_len = '0'
        test.will_flag_0 = '0'
        test.will_flag_1 = '1'
        test.last_will_message = f'test last_will_message - {test.client_id} disconnected'
        test.last_will_topic = 'test_last_will_topic'
        test.mqtt_server = MqttServer("IPv4", extended=True)

        test.execute_steps(test.will_flag_1, test.will_flag_0)

        test.log.step('12. Test other valid value for willFlag')
        test.log.info('== Steps 1-11 will be repeat for willFlag valid value: 0')
        test.execute_steps(test.will_flag_0, test.will_flag_1)

        test.log.info('== Check setting for willFlag invalid vale: 2 ==\n'
                      '== According to TC Expected Result: '
                      'error should be returned for invalid value. ==')
        test.mqtt_client.dstl_set_will_flag('2')
        test.expect(not test.mqtt_client.dstl_get_service().dstl_write_will_flag())

    def cleanup(test):
        try:
            test.mqtt_server.dstl_mqtt_subscribe_stop_request()
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.mqtt_client.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()

    def set_and_check_will_flag_settings(test, will_flag):
        test.mqtt_client.dstl_set_will_flag(will_flag)
        test.expect(test.mqtt_client.dstl_get_service().dstl_write_will_flag())
        dstl_get_siss_read_response(test.dut)
        test.expect(search(fr'.*SISS: 0,"willFlag","{will_flag}".*', test.dut.at1.last_response))

    def check_siss_will_parameters(test, will_flag, last_retain_value, last_qos_value):
        dstl_get_siss_read_response(test.dut)
        test.expect(search(
            fr'.*SISS: 0,"lastWillRetain","{last_retain_value}".*', test.dut.at1.last_response))
        test.expect(search(
            fr'.*SISS: 0,"lastWillQos","{last_qos_value}".*', test.dut.at1.last_response))
        if will_flag == test.will_flag_1:
            test.expect(search(
                fr'.*SISS: 0,"lastWillMessage","{test.last_will_message}".*',
                test.dut.at1.last_response))
            test.expect(search(
                fr'.*SISS: 0,"lastWillTopic","{test.last_will_topic}".*',
                test.dut.at1.last_response))

    def execute_steps(test, will_flag_main, will_flag_additional):
        last_retain_value = "0" if will_flag_main == test.will_flag_0 else "1"
        last_qos_value = "0" if will_flag_main == test.will_flag_0 else "1"

        test.log.info('== Run MQTT Server ==')
        test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=240))
        test.sleep(test.timeout)

        test.log.step('1. register to network.')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Change "Error Message Format" to 2 with AT+CMEE=2 command.')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('3. Create Mqtt Client profile with PUBLISH. \n'
                      '- Srvtype - Mqtt \n- ConId \n- Address \n- Cmd - publish \n'
                      '- hcContentLen - 0 \n- hcContent - 12345 \n- topic - mqtttest \n-qos 1')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='publish', alphabet="1",
            client_id=test.client_id, hc_cont_len=test.hc_cont_len, hc_content=test.hc_content,
            topic=test.topic, qos=test.qos, keep_alive=test.keep_alive_10)
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step(f'4. Set willFlag to {will_flag_main} and check parameters displayed '
                      f'using AT^SISS?. \nat^siss=x,willflag,{will_flag_main}')
        test.set_and_check_will_flag_settings(will_flag_main)

        test.log.step('5. Set will parameters and check at^siss? to make sure value displayed. \n')
        if will_flag_main == test.will_flag_0:
            test.log.info('== If the Will Flag is set to 0: ==\n'
                          '== the Will QoS and Will Retain fields in the Connect Flags '
                          'must be set to zero ==\n'
                          '== the Will Topic and Will Message fields must NOT be present ==')
            test.log.step(f'at^siss=x,lastWillRetain,{last_retain_value} \n'
                          f'at^siss=x,lastWillQos,{last_qos_value}')
        else:
            test.log.step(f'at^siss=x,lastWillRetain,{last_retain_value} \n'
                          f'at^siss=x,lastWillQos,{last_qos_value} \n'
                          'e.g. at^siss=x,lastWillMessage,testwill \n'
                          'e.g. at^siss=x,lastWillTopic,test1')
        test.mqtt_client.dstl_set_last_will_retain(last_retain_value)
        test.expect(test.mqtt_client.dstl_get_service().dstl_write_last_will_retain())
        test.mqtt_client.dstl_set_last_will_qos(last_qos_value)
        test.expect(test.mqtt_client.dstl_get_service().dstl_write_last_will_qos())
        if will_flag_main == test.will_flag_1:
            test.log.info(f'== lastWillMessage: "{test.last_will_message}" will be set ==\n'
                          f'== lastWillTopic: "{test.last_will_topic}" will be set ==')
            test.mqtt_client.dstl_set_last_will_message(test.last_will_message)
            test.expect(test.mqtt_client.dstl_get_service().dstl_write_last_will_message())
            test.mqtt_client.dstl_set_last_will_topic(test.last_will_topic)
            test.expect(test.mqtt_client.dstl_get_service().dstl_write_last_will_topic())
        test.check_siss_will_parameters(will_flag_main, last_retain_value, last_qos_value)

        test.log.step('6. Open Mqtt Client profile using SISO command and publish data to server.')
        test.expect(test.mqtt_client.dstl_get_service().
                    dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step('7. Disconnect Mqtt Client using antena disconnect.')
        test.log.info('== Instead of disconnect antenna will be realized module detach by CGATT ==')
        test.expect(test.connection_setup.dstl_detach_from_packet_domain())
        test.sleep(test.timeout / 2)
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step('8. Create mqtt client with Subscribe to check published data from '
                      'Topic and lastWillTopic.')
        test.log.info('== Check published data from Topic and lastWillTopic ==')
        test.log.info(f'== Check lastWillTopic "{test.last_will_topic}" ==')
        if will_flag_main == test.will_flag_1:
            test.log.info('== When willFlag is 1 - lastWillTopic should be visible ==')
            test.expect('Will message specified (49 bytes) (r1, q1).'
                        in test.ssh_server_2.last_response)
            test.expect(test.last_will_topic in test.ssh_server_2.last_response)
        else:
            test.log.info('== When willFlag is 0 - lastWillTopic should NOT be visible ==')
            test.expect(
                not 'Will message specified (49 bytes) (r1, q1).' in test.ssh_server_2.last_response)
            test.expect(not test.last_will_topic in test.ssh_server_2.last_response)
        test.log.info(f'== Check publish request - verify topic "{test.topic}" ==')
        test.expect(test.mqtt_server.dstl_check_publish_request(
            test.client_id, test.topic, len(test.hc_content), test.qos))
        test.log.info(f'== Start subscribing topic "{test.last_will_topic}" on server side ==')
        test.expect(test.mqtt_server.dstl_mqtt_subscribe_send_request(
            test.last_will_topic, last_qos_value))
        test.sleep(test.timeout * 3)
        if will_flag_main == test.will_flag_1:
            test.log.info('== When willFlag is 1 - lastWillMessage should be visible ==')
            test.expect(test.last_will_message in test.mqtt_server.dstl_mqtt_subscribe_read_data())
        else:
            test.log.info('== When willFlag is 0 - lastWillMessage NOT specified - '
                          'should NOT be visible ==')
            test.expect(
                not test.last_will_message in test.mqtt_server.dstl_mqtt_subscribe_read_data())
        test.mqtt_server.dstl_mqtt_subscribe_stop_request()

        test.log.step(f'9. Set willFlag to {will_flag_additional} and check parameters '
                      f'displayed using AT^SISS?.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.connection_setup.dstl_attach_to_packet_domain())
        test.sleep(10)
        test.log.info('== Activate Internet Profile ==')
        test.expect(test.connection_setup.dstl_activate_internet_connection())
        test.sleep(test.timeout)
        test.set_and_check_will_flag_settings(will_flag_additional)

        test.log.step('10. Set will parameters and check at^siss? to make sure value displayed.')
        test.log.info('== Will parameters was set in step 5 ==\n'
                      '== Only check at^SISS? will be realized ==')
        test.check_siss_will_parameters(will_flag_main, last_retain_value, last_qos_value)

        test.log.step('11. Open Mqtt Client profile using SISO command and check URC status.')
        test.log.info('== According to TC Expected Result: '
                      'Error for willFlag parameters should be returned. ==')
        test.expect(not test.mqtt_client.dstl_get_service().
                    dstl_open_service_profile(wait_for_default_urc=False))
        test.sleep(test.timeout)
        test.log.info(f'== Check server log - Profile NOT opened - '
                      f'topic "{test.last_will_topic}" should NOT be visible on server side==')
        test.expect(not test.mqtt_server.dstl_check_subscribe_request(
            test.client_id, test.last_will_topic, last_qos_value))

        test.log.info('== Close service profile and stop server ==')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()
        test.sleep(test.timeout)


if "__main__" == __name__:
    unicorn.main()