# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107975.001

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile


class Test(BaseTest):
    """
    Intention:
    To check correct Module behavior while opening MQTT unsubscribe profile.

    Description:
    1. Depends on Module:
    - define pdp context/nv bearer using CGDCONT command and activate it using SICA command
    - define Connection Profile using SICS command
    2. Define Mqtt Unsubscribe profile with mandatory set of parameters using SISS command
    3. Open Mqtt profile using SISO command
    4. Check service state using AT^SISO? command
    5. Close Mqtt profile using SISC command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.mqtt_server = MqttServer("IPv4", extended=True)
        test.client_id = dstl_get_imei(test.dut)
        test.topic_filter = "car/range"

    def run(test):
        test.log.info("TC0107975.001 MqttUnsubscribe_basic")
        test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                      'command and activate it using SICA command\r\n'
                      '- define Connection Profile using SICS command')
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step('2. Define Mqtt Unsubscribe profile with mandatory set of parameters using'
                      ' SISS command')
        test.expect(test.mqtt_server.dstl_run_mqtt_server())
        test.mqtt_unsubscribe = MqttProfile(test.dut, "0",
                                          test.connection_setup.dstl_get_used_cid(),
                                          alphabet=1, cmd="unsubscribe",
                                          topic_filter=test.topic_filter, client_id=test.client_id)
        test.mqtt_unsubscribe.dstl_set_parameters_from_ip_server(test.mqtt_server)
        test.mqtt_unsubscribe.dstl_generate_address()
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_load_profile())

        test.log.step('3) Open Mqtt profile using SISO command')
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_open_service_profile())

        test.log.step('4) Check service state using AT^SISO? command')
        test.log.info("executed in previous step")

        test.log.step('5) Close Mqtt profile using SISC command')
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_close_service_profile())
        test.mqtt_server.dstl_stop_mqtt_server()

    def cleanup(test):
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_close_service_profile())
        test.expect(test.mqtt_unsubscribe.dstl_get_service().dstl_reset_service_profile())
        try:
            test.mqtt_server.dstl_stop_mqtt_server()
            if not test.mqtt_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")


if "__main__" == __name__:
    unicorn.main()