#responsible grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0104421.002, TC0104421.004

import unicorn
from re import search
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response


class Test(BaseTest):
    """ To check SISE response in pooling mode for MQTT service. """

    def setup(test):
        dstl_detect(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "off"))
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
        test.mqtt_server = MqttServer("IPv4", extended=True)

    def run(test):
        test.log.info("Executing script for test case: 'TC0104421.002/004 MqttSISEinPollingMode'")
        test.srv_id = '0'
        hc_content = "Polling mode test"
        client_id = dstl_get_imei(test.dut)
        topic = "pooling/test"
        test.expect(test.mqtt_server.dstl_run_mqtt_server())

        test.log.step('1. Create MQTT client PUBLISH profile using SISS command. \r\n srvType - "Mqtt"'
                      '\r\n conId - e.g. 0\r\n address - mqtt://<host>:<port>\r\n Cmd - "Publish"'
                      '\r\n Topic - "pooling/test"\r\n hcContLen - 0\r\n hcContent - "Polling mode test"')
        test.mqtt_client_publish = MqttProfile(test.dut, test.srv_id, test.connection_setup.dstl_get_used_cid(), alphabet=1,
                                               cmd="publish", topic=topic, client_id=client_id, hc_cont_len='0',
                                               hc_content=hc_content)
        test.mqtt_client_publish.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_client_publish.dstl_generate_address()
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_load_profile())

        test.log.step("2. Execute AT^SISS? an check if connection parameters are correct")
        dstl_check_siss_read_response(test.dut, [test.mqtt_client_publish])

        test.log.step("3. Open MQTT Client profile using SISO command.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_open_service_profile())

        test.log.step("4. Execute AT^SISE command and pool oldest unread event for MQTT profile.")
        test.sleep(20)
        test.check_sise_info('8800')
        test.check_sise_info('2500')

        test.log.step("5. Check MQTT service state using AT^SISO? command.")
        rem_addr = "{}:{}".format(test.mqtt_server.dstl_get_server_ip_address(), test.mqtt_server.dstl_get_server_port())
        test.check_siso_response('4', '2', len(hc_content), "\d+.\d+.\d+.\d+:\d+", rem_addr)

        test.log.step("6. Check AT^SISI response for MQTT profile")
        test.check_sisi_response('4', len(hc_content))

        test.log.step("7. Close MQTT Client profile.")
        test.expect(test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile())

        test.log.step("8. Execute AT^SISE command and pool oldest unread event for MQTT profile.")
        test.check_sise_info('0')

        test.log.step("9. Check MQTT service state using AT^SISO? command.")
        test.check_siso_response('2', '1', '0', "0.0.0.0:0", "0.0.0.0:0")

        test.log.step("10. Check AT^SISI response for MQTT profile")
        test.check_sisi_response('2', '0')

        test.log.step("11. Check server log")
        test.expect(test.mqtt_server.dstl_check_publish_request(client_id, topic, len(hc_content), '0', '0'))
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.mqtt_client_publish.dstl_get_service().dstl_close_service_profile()
        test.mqtt_client_publish.dstl_get_service().dstl_reset_service_profile()

    def check_sise_info(test, info_id):
        test.dut.at1.send_and_verify('AT^SISE={},1'.format(test.srv_id))
        test.expect('SISE: {},{}'.format(test.srv_id, info_id) in test.dut.at1.last_response)

    def check_siso_response(test, service_state, socket_state, rx_count, loc_addr, rem_addr):
        test.dut.at1.send_and_verify('AT^SISO?')
        siso_pattern = r'SISO: {},"Mqtt",{},{},0,{},"{}","{}"'.format(test.srv_id, service_state, socket_state,
                                                                      rx_count, loc_addr, rem_addr)
        test.log.info("Check if module response is matching with pattern: \r\n{}".format(siso_pattern))
        test.expect(search(siso_pattern, test.dut.at1.last_response))

    def check_sisi_response(test, service_state, rx_count):
        test.dut.at1.send_and_verify('AT^SISI={}'.format(test.srv_id))
        sisi_pattern = r'SISI: {},{},0,{},0,0'.format(test.srv_id, service_state, rx_count)
        test.log.info("Check if module response is matching with pattern: \r\n{}".format(sisi_pattern))
        test.expect(search(sisi_pattern, test.dut.at1.last_response))


if "__main__" == __name__:
    unicorn.main()
