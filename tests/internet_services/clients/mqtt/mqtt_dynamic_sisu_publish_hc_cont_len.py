#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0102382.001, TC0102382.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """ To check PUBLISH connection using dynamic hcContLen request with MQTT server."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0102382.001/002 MqttDynamicSisuPublishHcContLen'")
        topic = 'weight'
        client_id = '0987654321'
        qos = '2'
        retain = '1'
        data_amount = 12
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client PUBLISH profile. Dynamic MQTT request will be used during connection.\r\n'
                      'srvType - "Mqtt" \r\n conId - e.g. 0 \r\n address - mqtt://<host>:<port>')
        test.mqtt_client_publish = MqttProfile(test.dut, '0', test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                               cmd="publish", topic=topic, client_id=client_id)
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step("2. Open MQTT Client profile using SISO command. \r\n"
                      "Set <optParam> to 2 – dynamic parameters OR dynamic request")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile(opt_param='2'))

        test.log.step("3. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2500"))
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sisw_urc_appeared("2"))

        test.log.step('4. Send request using SISU command. \r\n e.g. AT^SISU=0,"publish","2:weight:1::12"')
        test.expect(test.mqtt_client_publish.dstl_get_dynamic_service()
                    .dstl_sisu_send_request_publish(qos, topic, retain, '', data_amount))

        test.log.step("5. Write 12 bytes of data")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_send_sisw_command_and_data(data_amount))

        test.log.step("6. Check if correct URCs appears.")
        test.expect(test.mqtt_client_publish.dstl_get_urc().dstl_is_sis_urc_appeared("0", "3520", '"{}"'.format(topic)))

        test.log.step("7. Check response of the AT^SISO? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter("TX") == data_amount)

        test.log.step("8. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Check response of the AT^SISO? command")
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(test.mqtt_client_publish.dstl_get_parser().dstl_get_service_data_counter("TX") == 0)

        test.log.step("10. Check server log")
        test.expect(test.mqtt_server.dstl_check_publish_request(client_id, topic, data_amount, qos, retain))
        test.sleep(5)
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
