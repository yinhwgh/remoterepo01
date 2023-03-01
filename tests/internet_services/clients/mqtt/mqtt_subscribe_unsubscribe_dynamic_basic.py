# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107987.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.mqtt_profile import MqttProfile


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior while opening MQTT dynamic profile.

    Description:
    1. Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2. Set Error Message Format to 2 with AT+CMEE=2 command
    3. Create Mqtt Subscribe Client profile with only mandatory set of parameters
    - Srvtype - Mqtt
    - ConId
    - Address
    - CliendId
    - Cmd - subscribe
    - topicFilter - test/basic
    4. Open Mqtt Client profile using AT^SISO=profileId,2 command
    5. Check service state using AT^SISO? command
    6. Define dynamic Mqtt Unsubscribe profile using SISD command
    - Cmd - unsubscribe
    - topicFilter - test/basic (same topic filter as before)
    7. Send dynamic request using AT^SISU=profileId command
    8. Check service state using AT^SISO? command
    9. Close Mqtt Client profile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.client_id = dstl_get_imei(test.dut)
        test.topic_filter = "test/basic"
        test.topic_urc = '"test/basic"'

    def run(test):
        test.log.info("TC0107987.001 MqttSubscribeUnsubscribeDynamic_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Set Error Message Format to 2 with AT+CMEE=2 command')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('3. Create Mqtt Subscribe Client profile with only mandatory set of '
                      'parameters\r\n- Srvtype - Mqtt\r\n- ConId\r\n- Address\r\n- CliendId\r\n'
                      '- Cmd - subscribe\r\n- topicFilter - test/basic')
        test.expect(test.mqtt_server.dstl_run_mqtt_server())
        test.mqtt_client = MqttProfile(test.dut, "0",
                                          test.connection_setup.dstl_get_used_cid(),
                                          alphabet=1, cmd="subscribe",
                                          topic_filter=test.topic_filter, client_id=test.client_id)
        test.mqtt_client.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client.dstl_generate_address()
        dynamic_service = test.mqtt_client.dstl_get_dynamic_service()
        test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

        test.log.step('3) Open Mqtt profile using SISO command')
        test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param='2'))

        test.log.step('4) Check service state using AT^SISO? command')
        test.log.info("executed in previous step")

        test.log.step('6. Define dynamic Mqtt Unsubscribe profile using SISD command\r\n'
                      '- topicFilter\r\n- test/basic (same topic filter as before)')
        test.expect(dynamic_service.dstl_sisd_set_param_mqtt_cmd('unsubscribe'))
        test.expect(dynamic_service.dstl_sisd_set_param_topic_filter(test.topic_filter))

        test.log.step('7. Send dynamic request using AT^SISU=profileId command')
        test.expect(test.dut.at1.send_and_verify('AT^SISU=0', expect='OK'))
        test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0','2510',
                                                                             test.topic_urc))

        test.log.step('8. Check service state using AT^SISO? command')
        test.expect(test.mqtt_client.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.UP.value)

        test.log.step('5) Close Mqtt profile using SISC command')
        test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        test.mqtt_client.dstl_get_service().dstl_close_service_profile()
        test.mqtt_client.dstl_get_service().dstl_reset_service_profile()
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()