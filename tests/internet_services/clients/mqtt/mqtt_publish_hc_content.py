#responsible grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0102368.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile


class Test(BaseTest):
    """ To check basic PUBLISH connection with MQTT server."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0102368.001 MqttPublishHcContent'")
        hc_content = "lorem ipsum"
        client_id = '123'
        topic = "gemalto"
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client PUBLISH profile. Use only static parameters (AT^SISS command):'
                      '\r\n * srvType - "Mqtt" \r\n * conId - e.g. 0 \r\n * address - mqtt://<host>:<port> '
                      '\r\n * Cmd - "Publish" \r\n * Topic - "gemalto" \r\n * hcContLen - 0 '
                      '\r\n * hcContent - "lorem ipsum"')
        test.mqtt_client_publish = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                               cmd="publish", topic=topic, client_id=client_id, hc_cont_len='0',
                                               hc_content=hc_content)
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open MQTT Client profile using SISO command.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile())

        test.log.step("3. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step("4. Check server log")
        test.expect(test.mqtt_server.dstl_check_publish_request(client_id, topic, len(hc_content), '0', '0'))

        test.log.step("5. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()
