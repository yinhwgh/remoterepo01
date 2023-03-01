# responsible: renata.bryla@globallogic.com
# location: Wroclaw
# TC0107306.001

import re
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
from dstl.internet_service.profile_storage.dstl_get_siss_read_response import \
    dstl_get_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """ Check keep alive time interval for MQTT client """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0107306.001 MqttParamKeepAlive'")
        test.hc_content = "12345"
        test.client_id = '123'
        test.topic = "mqtttest"
        test.keep_alive_10 = 10
        test.keep_alive_120 = 120
        test.timeout = 60
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. register to network.')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Change "Error Message Format" to 2 with CMEE=2 command.')
        test.expect(dstl_set_error_message_format(test.dut))

        test.log.step('3. Create Mqtt Client profile with PUBLISH.\n'
                      '- Srvtype - Mqtt \n- ConId \n- Address \n- Cmd - publish \n'
                      '- hcContentLen - 0 \n- hcContent - 12345 \n- topic - mqtttest \n-qos - 1')
        test.mqtt_client_publish = MqttProfile(
            test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1, cmd="publish",
            client_id=test.client_id, hc_cont_len='0', hc_content=test.hc_content,
            topic=test.topic, qos='1')
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step('4.Check <KeepAlive> default value')
        dstl_get_siss_read_response(test.dut)
        test.expect(not re.search(r'"keepAlive"', test.dut.at1.last_response))

        test.execute_steps_5_11(test.keep_alive_10)

        test.log.step('12.Repeat steps 5-11 with different KeepAlive parameters, '
                      'analyze IP trace logs.')
        test.log.info('---> Check if ping request are printed on the server realized in step 8')
        test.log.info(f'---> Steps will be repeat for <KeepAlive> value: {test.keep_alive_120}')

        test.execute_steps_5_11(test.keep_alive_120)

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn('Problem during closing port on server.')
        except AttributeError:
            test.log.error('Server object was not created.')
        test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile(expected="OK|ERROR")
        test.mqtt_client_publish.dstl_get_service().dstl_reset_service_profile()

    def execute_steps_5_11(test, keep_alive_value):
        timeout_long = test.timeout*7 if keep_alive_value == test.keep_alive_120 else test.timeout*3
        if keep_alive_value == test.keep_alive_120:
            test.log.info('-> Once again run MQTT server and update Internet Service Setup Profile')
            test.expect(test.mqtt_server.dstl_run_mqtt_server(timeout=900))
            test.sleep(test.timeout / 6)
            test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
            test.mqtt_client_publish.dstl_generate_address()
            test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step(f'5.Set <KeepAlive> to {keep_alive_value} '
                      f'and check at^siss? to make sure value displayed.')
        test.mqtt_client_publish.dstl_set_keep_alive(keep_alive=keep_alive_value)
        test.mqtt_client_publish.dstl_get_service().dstl_write_keep_alive()
        dstl_get_siss_read_response(test.dut)
        test.expect(re.search(fr'.*SISS: 0,"keepAlive","{keep_alive_value}".*',
                              test.dut.at1.last_response))

        test.log.step('6.Enable IP tracing (e.g. with Wireshark).')
        test.log.info('=== PING REQUEST will be printed on the server. ===\n'
                      '=== Wireshark is not needed here. ===')

        test.log.step('7.Open Mqtt Client profile using SISO command.')
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile())

        test.log.step(f'8.Wait few minutes (check if ping request are printed on the server '
                      f'after every {keep_alive_value}s)')
        test.expect(test.mqtt_server.dstl_check_publish_request(
            test.client_id, test.topic, len(test.hc_content), qos='1'))
        test.sleep(timeout_long)
        test.check_keep_alive(keep_alive_value)

        test.log.step('9. Check service state.')
        test.expect(test.mqtt_client_publish.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.UP.value)

        test.log.step('10. Close socket service.')
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())
        test.log.info('-> According to TC Expected Result - '
                      'check if mqtt client status changed to "Allocated"')
        test.expect(test.mqtt_client_publish.dstl_get_parser().
                    dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.mqtt_server.dstl_stop_mqtt_server()
        test.sleep(10)

        test.log.step('11. Stop IP tracing.')
        test.log.info('=== IP tracing not needed. ===')

    def check_keep_alive(test, keep_alive_value):
        test.log.info(f'-> Checking if <KeepAlive> is sending each {keep_alive_value}s.')
        timestamps = []
        for line in test.ssh_server_2.last_response.split('\n'):
            pingreq_found = re.search(rf'(\d+): Received PINGREQ from {test.client_id}', line)
            if pingreq_found:
                timestamps.append(pingreq_found.group(1))
        for timestamp in range(len(timestamps) - 1):
            test.log.info(f'Checking if {timestamps[timestamp + 1]} - {timestamps[timestamp]} '
                          f'is equal to {keep_alive_value}s (+1).')
            test.expect(
                int(timestamps[timestamp + 1]) - int(timestamps[timestamp]) - keep_alive_value <= 1)


if "__main__" == __name__:
    unicorn.main()