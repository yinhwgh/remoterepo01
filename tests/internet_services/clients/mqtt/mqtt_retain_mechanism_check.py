# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0105130.001 TC0105130.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from datetime import date


class Test(BaseTest):
    """To check retain mechanism of MQTT client and correct URC after SISO command"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.info("Executing script for test case: MqttRetainMechanismCheck")
        today = date.today()
        test.hc_content = "Retained message from {}".format(today)
        test.client_id = '123'
        test.topic = "retain/test"
        test.keep_alive_10 = 10
        test.keep_alive_120 = 120
        test.timeout = 60
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=60))

        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('1. Create MQTT client PUBLISH profile.')
        test.mqtt_client_publish = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1, cmd="publish",
            client_id=test.client_id, hc_cont_len='0', hc_content=test.hc_content,
            connack_timeout="10", topic=test.topic, qos='2', retain="1", topic_qos="2",
            clean_session="0")
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step('2. Open MQTT Client profile using SISO command.')
        test.expect(test.mqtt_client_publish.dstl_get_service().
                    dstl_open_service_profile(expected=".*2501.*Connection accepted on retain "
                                                       "session.*3520.*{}.*".format(test.topic)))

        test.log.step('3. Check if correct URCs appears.')
        test.log.info("executed in last step")

        test.log.step('4. Close MQTT Client profile.')
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step('5. Check server log')
        test.expect(test.mqtt_server.dstl_check_publish_request(
            test.client_id, test.topic, data_size=len(test.hc_content), qos='2', retain="1"))

        test.log.step('6. On server side send SUBSCRIBE request for topic "retain/test"')
        test.expect(test.mqtt_server.dstl_mqtt_subscribe_send_request(test.topic, "1", timeout=10))
        test.expect(test.hc_content in test.mqtt_server.dstl_mqtt_subscribe_read_data())

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn('Problem during closing port on server.')
        except AttributeError:
            test.log.error('Server object was not created.')
        test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client_publish.dstl_get_service().dstl_reset_service_profile()


if "__main__" == __name__:
    unicorn.main()