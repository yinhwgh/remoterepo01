# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0104427.004

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
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_compare_internet_service_profiles import \
    dstl_compare_internet_service_profiles
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ To check cleanSession parameter during connection with MQTT server """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_error_message_format(test.dut))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.log.step('Precondition: Define PDP context for Internet services and activate '
                      'Internet service connection or create a GPRS connection profile.')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0104427.004 MqttParamcleanSession'")
        test.timeout = 10
        test.topic = 'mqtttest'
        test.topic_filter = 'main/topic'
        test.topic_subscribe = 'clean/session'
        test.qos_1 = '1'
        test.client_id = 'module01'
        test.hc_content = '12345'
        test.hc_cont_len = '0'
        test.clean_session_0 = "0"
        test.clean_session_1 = "1"
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client profile. Dynamic MQTT parameters will be used during '
                      'connection. \nSrvtype - Mqtt \nconId - e.g. 0 \n'
                      'address - mqtt://<host>:<port> \nclientId - e.g. "module01" \n'
                      'cleanSession - 0')
        test.log.info('== Additionally will be set: alphabet: 1, cmd: "subscribe", gos: 1, '
                      'topic: "mqtttest", topic_filter: "main/topic", '
                      'hcContentLen: 0, hcContent: 12345 ==')
        test.mqtt_client = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(),
                                       clean_session=test.clean_session_0, alphabet="1",
                                       qos=test.qos_1, client_id=test.client_id, cmd='subscribe',
                                       topic=test.topic, topic_filter=test.topic_filter,
                                       hc_cont_len=test.hc_cont_len, hc_content=test.hc_content)
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('2. Check response of the AT^SISS? command.')
        profiles_list_all = dstl_get_siss_read_response(test.dut)
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               profiles_list_all)

        test.log.step('3. Open MQTT Client profile using SISO command.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(
            opt_param='2', wait_for_default_urc=False))

        test.log.step('4. Check if correct URC appears.')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2501'))

        test.log.step('5. Send SUBSCRIBE request for "clean/session" topic using SISU command')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_subscribe(test.topic_subscribe, test.qos_1))

        test.log.step('6. Check if correct URC appears.')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '2521', f'"{test.topic_subscribe}"'))

        test.log.step('7. Check server log')
        test.check_server_logs(test.clean_session_0)

        test.log.step('8. Close MQTT Client profile.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.sleep(test.timeout)

        test.log.step('9. Open MQTT Client profile using SISO command.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(
            opt_param='2', wait_for_default_urc=False))
        test.sleep(test.timeout)

        test.log.step('10. On server side send PUBLISH package to "clean/session" topic.')
        test.expect(test.mqtt_server.
                    dstl_mqtt_publish_send_request(topic=test.topic_subscribe, data='test data'))

        test.log.step('11. Wait for new data URC notification')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "3488", f'".*{test.topic_subscribe}.*"'))

        test.log.step('12. Try to read data using SISR command')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.mqtt_client.dstl_get_service().
                    dstl_read_return_data(len('test data')) == 'test data')

        test.log.step('13. Close MQTT Client profile.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.sleep(test.timeout)

        test.log.step('14. Set cleanSession parameter to 1')
        test.mqtt_client.dstl_set_clean_session(test.clean_session_1)
        test.expect(test.mqtt_client.dstl_get_service().dstl_write_clean_session())

        test.log.step('15. Check response of the AT^SISS? command.')
        profiles_list_all_new = dstl_get_siss_read_response(test.dut)
        dstl_compare_internet_service_profiles(test.dut, dstl_get_siss_read_response(test.dut),
                                               profiles_list_all_new)

        test.log.step('16. Open MQTT Client profile using SISO command.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(
            opt_param='2', wait_for_default_urc=False))
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '2520', f'"{test.topic_filter}"'))

        test.log.step('17. Check server log')
        test.sleep(test.timeout)
        test.check_server_logs(test.clean_session_1)

        test.log.step('18. On server side send PUBLISH package to "clean/session" topic.')
        test.expect(test.mqtt_server.
                    dstl_mqtt_publish_send_request(topic=test.topic_subscribe, data='test data'))
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '2520', f'"{test.topic_filter}"'))

        test.log.step('19. Try to read data using SISR command')
        test.expect(not test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(not test.mqtt_client.dstl_get_service().
                    dstl_read_return_data(100) == 'test data')

        test.log.step('20. Close MQTT Client profile.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()
        test.sleep(test.timeout)

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.mqtt_client.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()

    def check_server_logs(test, clean_session_value):
        test.log.info('Verify server log - wait for: .*New client connected from.*as '
                      fr'{test.client_id} \(.*, c{clean_session_value},.*\)')
        test.expect(search(
            fr'.*New client connected from.*as {test.client_id} \(.*, c{clean_session_value},.*\)',
            test.ssh_server_2.last_response))
        test.log.info(fr'Verify server log - wait for: Received SUBSCRIBE from {test.client_id}')
        test.expect(search(fr'Received SUBSCRIBE from {test.client_id}',
                           test.ssh_server_2.last_response))
        test.log.info(
            fr'Verify server log - wait for: .*{test.topic_subscribe} \(QoS {test.qos_1}\)')
        test.expect(search(fr'.*{test.topic_subscribe} \(QoS {test.qos_1}\)',
                           test.ssh_server_2.last_response))


if "__main__" == __name__:
    unicorn.main()