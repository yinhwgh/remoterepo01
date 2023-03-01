# responsible: bartlomiej.mazurek2@globallogic.com
# location: Wroclaw
# TC0102369.001, TC0102369.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    TC0102369.002 - MqttPublishHcContLen

    DESCRIPTION
    1. Create MQTT client PUBLISH profile. Use only static configuration (AT^SISS command):
        srvType - "Mqtt"
        conId - e.g. 0
        address - mqtt://<host>:<port>
        clientId - "publishHcContLen002"
        Cmd - "Publish"
        Topic - "thales"
        hcContLen - 15
        Qos - 1
    2. Open MQTT Client profile using SISO command.
    3. Check if correct SIS URC appears.
    4. Check if correct SISW URC is displayed.
    5. Write 15 bytes of data
    6. Check server log
    7. Try to write data once again
    8. Close MQTT Client profile.

    INTENTION
    To check PUBLISH connection using hcContentLen parameter with MQTT server.

    """

    def setup(test):
        test.topic = "thales"
        test.client_id = "publishHcContLen002"
        test.hc_cont_len = 15
        test.qos = "1"

        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("=== TC0102369.002 - MqttPublishHcCont ===")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('=== 1. Create Mqtt client PUBLISH profile. Use only static configuration'
                      ' (AT^SISS command): ===\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address\n- ClientId\n- Cmd - "Publish"\n-'
                      ' topic - "thales"\n- hcContLen - 15\n- qos - "1" ')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='publish',
            topic=test.topic, client_id=test.client_id, hc_cont_len=test.hc_cont_len, qos=test.qos)
        test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
        test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('=== 2. Open MQTT Client profile using SISO command. ===')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())

        test.log.step('=== 3. Check if correct SIS URC appears. ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))

        test.log.step('=== 4. Check if correct SISW URC is displayed. ===')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step('=== 5. Write 15 bytes of data ===')
        test.expect(test.mqtt_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.hc_cont_len))

        test.log.step('=== 6. Check server log ===')
        test.expect(test.mqtt_server.dstl_check_publish_request(test.client_id, test.topic,
                                                                test.hc_cont_len, test.qos))
        test.sleep(5)
        test.expect("Sending PUBACK to publishHcContLen002 (m1, rc0)" in
                    test.mqtt_server.dstl_read_data_on_ssh_server())

        test.log.step('=== 7. Try to write data once again ===')
        test.expect(not test.mqtt_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.hc_cont_len))

        test.log.step('=== 8. Close MQTT Client profile. ===')
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
