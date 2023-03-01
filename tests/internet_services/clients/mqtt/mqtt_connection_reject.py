# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0104428.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.get_internet_service_error_report import \
    dstl_get_internet_service_error_report
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    TC0104428.002 - MqttConnectionReject

    DESCRIPTION
    1. Register to network.
    2. Create Mqtt Client profile.
        - Srvtype - Mqtt
        - ConId
        - Address
        - Cmd - publish
        - hcContentLen - 0
        - hcContent - 12345
        - topic - mqtttest
        - qos - 1
    3. Open Mqtt Client profile using SISO command, Check if URCs appears.
    4. Publish data to server.
    5. Force server to send DISCONNECT packet, check DUT status.
    6. AT^SISC=0 disconnect DUT.
    7. Re-open DUT using SISO command and force server reject the connection.
    8. Check if URCs appears.
    9. AT^SISC=0 disconnect DUT.
    10. Enable mqtt server ,DUT re-connect to server.
    11. Publish data to server and check profile status with AT^SISI? and AT^SISE?
    12. Close DUT.

    INTENTION
    To check if the MQTT work well when connection disconnect and reject by Server.

    """

    def setup(test):
        test.topic_filter = "test/basic"
        test.topic = "mqtttest"
        test.client_id = "mqttConReject"
        test.data = "12345"
        test.qos = "1"

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("=== TC0104428.002 - MqttConnectionReject ===")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('=== 1. Register to network. ===')
        test.log.info('=== Module has been registered during setup ===')

        test.log.step('=== 2. Create Mqtt Client profile\n- Srvtype - Mqtt \n- ConId \n'
                      '- Address\n- Cmd - publish\n- hcContentLen - 0\n- hcContent - 12345\n'
                      '- topic - mqtttest\n- qos - 1\n===')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='publish',
            topic=test.topic, client_id=test.client_id, topic_filter=test.topic_filter,
            qos=test.qos, hc_cont_len=0, hc_content=test.data)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('=== 3. Open Mqtt Client profile using SISO command, Check if URCs appears. '
                      '===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))

        test.log.step('=== 4. Publish data to server. ===')
        test.log.info("Data was published during opening of the profile in the previous step.")
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "3520", f'"{test.topic}"'))

        test.log.step('=== 5. Force server to send DISCONNECT packet, check DUT status. ===')
        test.mqtt_server.dstl_stop_mqtt_server()
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step('=== 6. AT^SISC=0 disconnect DUT. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())

        test.log.step('=== 7. Re-open DUT using SISO command and force server reject the '
                      'connection. ===')
        test.expect(test.mqtt_client.dstl_get_service().
                    dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step('=== 8. Check if URCs appears. ===')
        test.expect('^SIS: 0,0,20,"Connection timed out"' in test.dut.at1.last_response)

        test.log.step('=== 9. AT^SISC=0 disconnect DUT. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())

        test.log.step('=== 10. Enable mqtt server ,DUT re-connect to server. ===')
        test.mqtt_server.dstl_run_mqtt_server()
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('=== 11. Publish data to server and check profile status with AT^SISI? and '
                      'AT^SISE? ===')
        test.log.info("Data was published during opening of the profile in the previous step.")
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "3520", f'"{test.topic}"'))
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)
        test.expect(dstl_get_internet_service_error_report(test.dut, 0, info_mode=0))

        test.log.step('=== 12. Close DUT. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()

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
