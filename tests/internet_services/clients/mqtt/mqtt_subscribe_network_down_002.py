# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0104422.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.configuration.network_registration_status import dstl_check_network_registration_urc
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service import register_to_network

class Test(BaseTest):
    """
    TC0104422.002 - MqttSubscribeNetworkDown

    DESCRIPTION
    1.Register to network.
    2. Create Mqtt Client profile‚
        - Srvtype - Mqtt
        - ConId
        - Address
        - ClientId
        - Cmd - Subscribe
        - topic - mqtttest
    3. DUT Send request using AT^SISO=profileId command.
    4. Check if correct URCs appears and AT^SISO?
    5. Enable Server send some data to DUT.
    6. Dont read data on DUT, force module deregister to network or disconnect the antenua.
    7. Check Service status with AT^SISO? and AT^SISI?
    8. Read received data using AT^SISR.
    9. Check Service status with AT^SISO? and AT^SISI?
    10. Close Mqtt Client profile
    11. Reconnect to network and repeat step 1-5,check if DUT subscribe cmd perfom normally.

    INTENTION
    To check if the MQTT Subscribe function work well when network loss.

    """

    def setup(test):
        test.client_id = "subNetDown002"
        test.topic_filter = "mqtttest"
        test.data = "1234567890"
        test.qos = "1"

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("=== TC0104422.002 - MqttSubscribeNetworkDown ===")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('=== 1. Register to network ===')
        test.log.info('=== Module has been registered during setup ===')

        test.log.step('=== 2. Create Mqtt Client profile\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address\n- ClientId\n- Cmd - subscribe\n'
                      '- topic - mqtttest ===')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
            topic_filter=test.topic_filter, client_id=test.client_id)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('=== 3. DUT Send request using AT^SISO=profileId command ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('=== 4. Check if correct URCs appears and AT^SISO? ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('=== 5. Enable Server send some data to DUT ===')
        test.expect(test.mqtt_server.dstl_mqtt_publish_send_request(topic=test.topic_filter,
                                                                    data=test.data, qos=test.qos))

        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.log.step('=== 6. Dont read data on DUT, force module deregister to network'
                      ' or disconnect the antenua. ===')
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2"))
        test.expect(test.dut.dstl_check_network_registration_urc(expected_state="0"))

        test.log.step('=== 7. Check Service status with AT^SISO? and AT^SISI? ===')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state(Command.SISI_READ) == ServiceState.UP.value)

        test.log.step('=== 8. Read received data using AT^SISR. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_read_data(len(test.data)))

        test.log.step('=== 9. Check Service status with AT^SISO? and AT^SISI? ===')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state(Command.SISI_READ) == ServiceState.DOWN.value)

        test.log.step('=== 10. Close Mqtt Client profile ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())

        test.log.step('=== 11. Reconnect to network and repeat step 1-5,check if DUT'
                      ' subscribe cmd perfom normally. ===')
        test.expect(test.dut.dstl_register_to_network())

        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.info('=== Create Mqtt Client profile\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address\n- ClientId\n- Cmd - subscribe\n'
                      '- topic - mqtttest ===')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
            topic_filter=test.topic_filter, client_id=test.client_id)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.info('=== DUT Send request using AT^SISO=profileId command ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())

        test.log.info('=== Check if correct URCs appears and AT^SISO? ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.info('=== Enable Server send some data to DUT ===')
        test.expect(test.mqtt_server.dstl_mqtt_publish_send_request(topic=test.topic_filter,
                                                                    data=test.data, qos=test.qos))

        test.log.info('=== Receive data on DUT ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.expect(test.mqtt_client.dstl_get_service().dstl_read_data(len(test.data)))

        test.log.info('=== Close Mqtt Client profile ===')
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
