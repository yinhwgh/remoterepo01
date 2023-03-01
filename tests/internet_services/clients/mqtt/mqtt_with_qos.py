# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0104425.001, TC0104425.003

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ To check if the qos level can work well for MQTT publish command. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

    def run(test):
        test.log.info("Executing script for test case: 'TC0104425.001/003 MqttwithQos'")
        test.timeout = 10
        test.data_amount = 10
        test.qos_0 = '0'
        test.qos_1 = '1'
        test.qos_2 = '2'
        test.topic_client = 'mqtttest_client'
        test.topic = 'mqtttest'
        test.client_id = 'MqttClientId'
        test.hc_content = '12345'
        test.hc_cont_len = '0'
        test.mqtt_server = MqttServer("IPv4", extended=True)

        test.execute_steps_1_12(test.qos_1)

        test.log.step('13. Change QOS to 0, repeat step1-12, check MQTT perform status '
                      'with AT^SISI ?.')
        test.execute_steps_1_12(test.qos_0)

        test.log.step('14. Change Qos to 2, repeat step1-12, check MQTT perform status.')
        test.execute_steps_1_12(test.qos_2)

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.mqtt_client.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()

    def execute_steps_1_12(test, qos_value):
        test.log.info('== Run MQTT Server ==')
        test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=240))
        test.sleep(test.timeout)

        test.log.step('1. Register to network.')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Create Mqtt Client profile with only basic parameters e.g.\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address')
        test.log.info('== According to ATC clientId is mandatory - will be set: "MqttClientId" ==\n'
                      '== Additionally will be set: alphabet: 1, cmd: "publish", '
                      'topic: "mqtttest_client", hcContentLen: 0, hcContent: 12345 ==')
        test.mqtt_client = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(),
                                       alphabet="1", client_id=test.client_id,
                                       cmd='publish', topic=test.topic_client,
                                       hc_cont_len=test.hc_cont_len, hc_content=test.hc_content)
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('3. Change "Error Message Format" to 2 with AT+CMEE=2 command.')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('4. Open Mqtt Client profile using AT^SISO=profileId,2 command.')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(
            opt_param='2', wait_for_default_urc=False))

        test.log.step('5 Check if correct URCs appears.')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared(
            "0", "2500", '"Connection accepted on clean session."'))

        test.log.step('6. Create Mqtt Client profile with parameters \n- Cmd - publish \n'
                      '- hcContentLen - 0 \n- hcContent - 12345 \n- topic - mqtttest')
        dynamic_service = test.mqtt_client.dstl_get_dynamic_service()
        test.expect(dynamic_service.dstl_sisd_set_param_mqtt_cmd('publish'))
        test.expect(dynamic_service.dstl_sisd_set_param_hc_cont_len(test.hc_cont_len))
        test.expect(dynamic_service.dstl_sisd_set_param_hc_content(test.hc_content))
        test.expect(dynamic_service.dstl_sisd_set_param_topic(test.topic))

        test.log.step(f'7.Set QOS to {qos_value}.')
        test.expect(dynamic_service.dstl_sisd_set_param_qos(qos_value))

        test.log.step('8. Send publish request using AT^SISU=profileId command')
        if qos_value == test.qos_0:
            test.log.info('== For sending PUBLISH request with Qos = 0 there is no acknowledge '
                          'from server == \n== Verification SIS URC not will be realized ==')
            test.expect(dynamic_service.dstl_sisu_send_request(polling_mode=True))
            test.expect("SISW: 0,2" in test.dut.at1.last_response)
        else:
            test.expect(dynamic_service.dstl_sisu_send_request())

        test.log.step('9. Check if correct URCs appears.')
        test.log.info('== For hcContentLen: 0 - ^SISW: 0,2 expected - '
                      'Checking realized in previous step ==')

        test.log.step('10. Set hcContentLen = 10 and Send 10 bytes using SISW command, '
                      'check if data can be received by server.')
        test.expect(dynamic_service.dstl_sisd_set_param_hc_cont_len('10'))
        test.expect(dynamic_service.dstl_sisu_send_request(polling_mode=True))
        test.log.info('== For hcContentLen: 10 - ^SISW: 0,1 expected ==')
        test.expect("SISW: 0,1" in test.dut.at1.last_response)
        test.expect(test.mqtt_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(test.data_amount))
        if qos_value == test.qos_0:
            test.log.info('== For sending PUBLISH request with Qos = 0 there is no acknowledge '
                          'from server == \n== Verification SIS URC not will be realized == \n'
                          '== Only ^SISW: 0,2 expected after send data for hcContentLen: 10 ==')
        else:
            test.log.info('== After send data for hcContentLen: 10 - ^SISW: 0,2 expected \n'
                          'and ^SIS URC with topic: "mqtttest" ==')
            test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared(
                "0", "3520", '"{}"'.format(test.topic)))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))
        test.log.info("== Check server log will be chec after service close in step 12 ==")

        test.log.step('11. Check service state using AT^SISO? command.')
        if qos_value == test.qos_0:
            test.log.info('== For sending PUBLISH request with Qos = 0 there is no acknowledge '
                          'from server == \n'
                          '== Will be realized check MQTT perform status with AT^SISI ? ==')
            test.expect(test.mqtt_client.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISI_READ) == ServiceState.UP.value)
        else:
            test.expect(test.mqtt_client.dstl_get_parser().
                        dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('12. Close Mqtt Client profile')
        test.log.info('== Close service profile, stop server and deactivate internet connection ==')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()
        test.sleep(test.timeout)
        test.expect(test.connection_setup.dstl_deactivate_internet_connection())
        test.sleep(test.timeout)
        test.log.info("== Check server log ==")
        test.expect(test.mqtt_server.dstl_check_publish_request(
            test.client_id, test.topic, test.data_amount, qos_value))
        if qos_value == test.qos_2:
            test.expect('Sending PUBREC to MqttClientId' in test.ssh_server_2.last_response)
            test.expect('Received PUBREL from MqttClientId' in test.ssh_server_2.last_response)


if "__main__" == __name__:
    unicorn.main()