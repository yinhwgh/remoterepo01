# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0102389.004

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ To check connection with Mqtt server """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0102389.004 MqttDynamicSisuSubscribe'")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1 Create Mqtt Client profile with only basic parameters\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address')
        test.log.info('Due to KPIs, the following will also be defined:\n'
                      'cmd="subscribe", topic="mqtttest", topic_filter="main/topic", '
                      'client_id="123_client_id"')
        test.mqtt_client = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
            topic='mqtttest', topic_filter='main/topic', client_id='123_client_id')
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('2 Change Error Message Format to 2 with AT+CMEE=2 command')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('3 Open Mqtt Client profile using AT^SISO=profileId,2 command')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))

        test.log.step('4 Check if correct URCs appears')
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))

        test.log.step('5 Send Subscribe request using AT^SISU=profileId command with parameters:\n'
                      '- topicFilter - test/basic \n- topicQos - 1')
        test.expect(test.mqtt_client.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_subscribe(topic_filter='test/basic', topic_qos='1'))

        test.log.step('6 Check if correct URC appears')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "2521", '"test/basic"'))

        test.log.step('7 On server publish some data in topic test/basic')
        test.expect(test.mqtt_server.
                    dstl_mqtt_publish_send_request(topic='test/basic', data='test data'))

        test.log.step('8 Wait for URCs on DUT')
        test.expect(test.mqtt_client.dstl_get_urc().
                    dstl_is_sis_urc_appeared("0", "3488", '".*test/basic.*"'))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))

        test.log.step('9 Read data from topic test/basic using SISR command')
        test.expect(test.mqtt_client.dstl_get_service().dstl_read_return_data(100) == 'test data')

        test.log.step('10 Check service state using AT^SISO? command.')
        test.expect(test.mqtt_client.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('11 Close Mqtt Client profile.')
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