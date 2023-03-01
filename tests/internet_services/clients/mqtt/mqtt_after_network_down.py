# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0104424.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.configuration.network_registration_status import dstl_check_network_registration_urc
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_deregister_from_network


class Test(BaseTest):
    """
    TC0104424.002 - MqttAfterNetworkDown

    DESCRIPTION
    1.Register to network.
    2. Create Mqtt Client profile with only basic parameters
        - Srvtype - Mqtt
        - ConId
        - Address
        - ClientId
        - topic
    3. Change "Error Message Format" to 2 with AT+CMEE=2 command.
    4. Open Mqtt Client profile using AT^SISO=profileId,2 command.
    5. Check if correct URCs appears.
    6. Create Mqtt Client profile with dynamic parameters using at^sisd=profileId,"setparam",xxx,xxx
        - Cmd - publish
        - hcContentLen - 0
        - hcContent - 12345
        - topic - mqtttest
    7. Set QOS to 1.
    8. Send publish request using AT^SISU=profileId command
    9. Check if correct URCs appears
    10. Force module deregister to network or disconnect the antenua.
    11. Send 10 bytes using SISW command
    12. Check service state using AT^SISO? command.
    13. Reconnect and register to network.
    14. Mqtt need to be re-opened, Check service state using AT^SISO? command.
    15. Send 10 bytes using SISW command
    16. Close Mqtt Client profile

    INTENTION
    To check if the MQTT work well when network down.

    """

    def setup(test):
        test.topic = "mqtttest"
        test.topic_filter = "test/basic"
        test.client_id = "mqttAfterNetworkDown"
        test.data = "1234567890"
        test.data_length = len(test.data)

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, tcp_with_urc="on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("=== TC0104424.002 - MqttAfterNetworkDown ===")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('=== 1. Register to network. ===')
        test.log.info('=== Module has been registered during setup ===')

        test.log.step('=== 2. Create Mqtt Client profile with only basic parameters\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address\n- ClientId\n- topic\n===')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
            topic=test.topic, client_id=test.client_id, topic_filter=test.topic_filter)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('=== 3. Change "Error Message Format" to 2 with AT+CMEE=2 command. ===')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('=== 4. Open Mqtt Client profile using AT^SISO=profileId,2 command. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))

        test.log.step('=== 5. Check if correct URCs appears. ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))

        test.log.step('=== 6. Create Mqtt Client profile with dynamic parameters'
                      ' using at^sisd=profileId,"setparam",xxx,xxx\n - Cmd - publish\n'
                      ' - hcContentLen - 0\n- hcContent - 12345\n- topic - mqtttest ===')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_mqtt_cmd(cmd='publish'))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_hc_cont_len(hc_cont_len=0))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_hc_content(hc_content=test.data))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_topic(topic=test.topic))

        test.log.step('=== 7. Set QOS to 1. ===')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_qos(qos='1'))

        test.log.step('=== 8. Send publish request using AT^SISU=profileId command ===')
        test.expect(test.mqtt_client.dstl_get_dynamic_service().dstl_sisu_send_request())

        test.log.step('=== 9. Check if correct URCs appears ===')
        test.log.info('Check was done in previous step')

        test.log.step('=== 10. Force module deregister to network or disconnect the antenua. ===')
        test.expect(dstl_deregister_from_network(test.dut))
        test.expect(dstl_check_network_registration_urc(test.dut, expected_state="0"))

        test.log.step('=== 11. Send 10 bytes using SISW command. ===')
        test.expect(not test.mqtt_client.dstl_get_service()
                    .dstl_send_sisw_command_and_data(test.data_length))

        test.log.step('=== 12. Check service state using AT^SISO? command. ===')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step('=== 13. Reconnect and register to network. ===')
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('=== 14. Mqtt need to be re-opened, '
                      'Check service state using AT^SISO? command. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('=== 15. Send 10 bytes using SISW command ===')
        test.mqtt_client.dstl_get_dynamic_service().dstl_sisd_clean_param()
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_mqtt_cmd(cmd='publish'))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_topic(topic=test.topic))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisd_set_param_hc_cont_len(hc_cont_len=test.data_length))
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisu_send_request(polling_mode=True))
        test.expect(test.mqtt_client.dstl_get_service()
                    .dstl_send_sisw_command_and_data(test.data_length))

        test.log.step('=== 16. Close Mqtt Client profile ===')
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
