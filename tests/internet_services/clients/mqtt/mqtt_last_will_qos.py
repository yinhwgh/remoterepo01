# responsible: maciej.gorny@globallogic.com
# location: Wroclaw
# TC0105120.001, TC0105120.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ To basic check of lastWillQos mechanism."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_error_message_format(test.dut))
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0105120.001/002 MqttLastWillQos'")

        test.client_id = 'TestModuleLastWillID666'
        test.last_will_topic = 'MqttLastWillQos_topic'
        last_will_message = "Basic check of lastWillQos mechanism"
        last_will_retain = 1

        test.log.step('1. Create MQTT client profile. Use following parameters '
                      '(AT^SISS command), e.g: \r\nsrvType - "Mqtt" \r\nconId - 0 '
                      '\r\naddress - mqtt://<host>:<port> \r\nkeepAlive - 20 '
                      '\r\nclientId - client007 \r\nlastWillTopic - "status" '
                      '\r\nlastWillMessage - "Shaken, not stirred" \r\nlastWillRetain - 1')
        test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=220))
        test.sleep(3)
        test.mqtt_client = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(),
                                       cmd='subscribe', alphabet=1, keep_alive=20,
                                       last_will_topic=test.last_will_topic,
                                       client_id=test.client_id,
                                       last_will_message=last_will_message, topic_filter="test",
                                       last_will_retain=last_will_retain, will_flag='1')
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('2. Start subscribing lastWillTopic from the previous step on server side')
        test.expect(test.mqtt_server.dstl_mqtt_subscribe_send_request(
            topic_filter=test.last_will_topic))

        test.log.step("3. Open MQTT Client profile using SISO command. \r\n"
                      "Set <optParam> to 2 – dynamic parameters OR dynamic request")
        test.open_profile()

        test.log.step("4. Wait at least 20 seconds.")
        test.sleep(20)

        test.log.step("5. Check server log.")
        test.check_server_log(0)

        test.log.step("6. Close MQTT Client profile..")
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("7. Check server log.")
        test.expect('Sending PUBLISH to' not in test.ssh_server_2.last_response)

        test.log.step("8. Set SISS lastWillQos parameter to 2")
        test.mqtt_client.dstl_set_last_will_qos(2)
        test.expect(test.mqtt_client.dstl_get_service().dstl_write_last_will_qos())

        test.log.step("9. Open MQTT Client profile using SISO command. \r\n"
                      "Set <optParam> to 2 – dynamic parameters OR dynamic request")
        test.open_profile()
        test.sleep(5)

        test.log.step("10. Check server log.")
        test.check_server_log(2)

        test.log.step("11. Close MQTT Client profile..")
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()
        test.mqtt_server.dstl_mqtt_subscribe_stop_request()
        test.sleep(5)

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            test.mqtt_server.dstl_mqtt_subscribe_stop_request()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.mqtt_client.dstl_get_service().dstl_close_service_profile()
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()

    def open_profile(test):
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param='2',
                                                                        wait_for_default_urc=False))
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2500", '"Connection accepted on clean session."'))

    def check_server_log(test, q_value):
        test.expect('New client connected' in test.ssh_server_2.last_response)
        test.sleep(1)
        test.expect(test.client_id in test.ssh_server_2.last_response)
        test.sleep(1)
        test.expect('c1' in test.ssh_server_2.last_response)
        test.sleep(1)
        test.expect('Will message specified (36 bytes) (r1, q{}).'.format(q_value)
                    in test.ssh_server_2.last_response)
        test.sleep(1)
        test.expect(test.last_will_topic in test.ssh_server_2.last_response)
        test.expect(not test.mqtt_server.dstl_check_publish_request(test.client_id, topic='.*',
                                                                    data_size=".*", qos='.*',
                                                                    retain='.*'))


if "__main__" == __name__:
    unicorn.main()
