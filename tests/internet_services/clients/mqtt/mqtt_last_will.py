#responsible grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0104737.001, TC0104737.002

import unicorn
from re import search
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    """ To check "last will" mechanism of MQTT client."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.mqtt_server = MqttServer("IPv4", extended=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0104737.001/002 MQTTLastWill'")

        test.keep_alive = 15
        test.client_id = "client001"
        last_will_topic = "module/status"
        last_will_message = "{} disconnected".format(test.client_id)
        last_will_qos = 1
        hc_content = "data to publish"
        topic = "topic publish"

        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT publish client profile. Use following parameters (AT^SISS command): '
                      '\r\nsrvType - "Mqtt" \r\nconId - e.g. 0 \r\naddress - mqtt://<host>:<port> \r\nkeepAlive - 15 '
                      '\r\nclientId - client001 \r\nlastWillTopic - "module/status" '
                      '\r\nlastWillMessage - "client001 disconnected" \r\nlastWillQos - 1')
        test.mqtt_client = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                       cmd='publish', topic=topic, hc_content=hc_content, will_flag='1',
                                       client_id=test.client_id, last_will_topic=last_will_topic, keep_alive=test.keep_alive,
                                       last_will_message=last_will_message, last_will_qos=last_will_qos)
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('2. Start subscribing "module/status" topic on server side')
        test.expect(test.mqtt_server.dstl_mqtt_subscribe_send_request(topic_filter=last_will_topic))

        test.log.step("3. Open MQTT Client profile using SISO command. "
                      "Set <optParam> to 2 – dynamic parameters OR dynamic request")
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param='2'))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))

        test.log.step("4. Check server log")
        test.expect(test.mqtt_server.dstl_check_publish_request(test.client_id, topic, len(hc_content)))
        test.sleep(80)
        test.check_keep_alive()

        test.log.step("5. Restart module")
        test.expect(dstl_restart(test.dut))

        test.log.step('6. Check subscribing of "module/status" topic on server side')
        test.sleep(10)
        test.expect(last_will_message in test.mqtt_server.dstl_mqtt_subscribe_read_data())

        test.mqtt_server.dstl_mqtt_subscribe_stop_request()
        test.mqtt_server.dstl_stop_mqtt_server()

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

    def check_keep_alive(test):
        test.log.info('Checking if keepAlive is sending each {}s.'.format(test.keep_alive))
        timestamps = []
        for line in test.ssh_server_2.last_response.split('\n'):
            pingreq_found = search(r'(\d+): Received PINGREQ from {}'.format(test.client_id), line)
            if pingreq_found:
                timestamps.append(pingreq_found.group(1))
        for timestamp in range(len(timestamps)-1):
            test.log.info('Checking if {} - {} is equal to {}s (+1).'.format(timestamps[timestamp+1],
                                                                             timestamps[timestamp], test.keep_alive))
            test.expect(int(timestamps[timestamp+1]) - int(timestamps[timestamp]) - test.keep_alive <= 1)


if "__main__" == __name__:
    unicorn.main()
