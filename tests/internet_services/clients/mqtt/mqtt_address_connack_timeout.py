#responsible grzegorz.dziublinski@globallogic.com
#Wroclaw
#TC0105171.001, TC0105171.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from time import time


class Test(BaseTest):
    """ Basic check address syntax with connackTimeout parameter. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_restart(test.dut))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_reset_internet_service_profiles(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

    def run(test):
        test.log.info("Executing script for test case: 'TC0105171.001/002 MqttAddressConnackTimeout'")
        connack_timeouts = [None, 45, 20]
        test.socket_dynamic_profiles = []

        test.log.info("Create and open TCP listener service on r1 module.")
        test.socket_listener = SocketProfile(test.r1, "0", test.connection_setup_r1.dstl_get_used_cid(),
                                             protocol="tcp", host="listener", localport=65100)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        r1_ip_address = test.socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("1. Create MQTT client PUBLISH profile. Static parameters should be used.")
        test.log.info("Step 1 will be executed together with step 2.")
        test.mqtt_client = MqttProfile(test.dut, '0', test.connection_setup_dut.dstl_get_used_cid(),
                                       alphabet=1, cmd="publish", host=r1_ip_address, port=65100,
                                       topic="topicConnackTimeout", client_id='8765', user='testMqttUser',
                                       passwd='testMqttPasswd', are_concatenated=True)

        for connack_timeout in connack_timeouts:
            test.log.step("2. For address parameters use syntax: user name, password, "
                          "(address to the TCP listener on Remote) without connackTimeout; "
                          "e.g. mqtt://[username][:password]@host[:port]")
            if connack_timeout:
                test.mqtt_client.dstl_set_connack_timeout(connack_timeout)
            test.mqtt_client.dstl_generate_address()
            test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

            test.log.step("3. Check Internet Service Profile AT^SISS.")
            dstl_check_siss_read_response(test.dut, [test.mqtt_client])

            test.log.step("4. Check service and socket state AT^SISO.")
            test.expect(test.mqtt_client.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
            test.expect(test.mqtt_client.dstl_get_parser().dstl_get_socket_state() == SocketState.NOT_ASSIGNED.value)

            test.log.step("5. Open MQTT Client profile using AT^SISO.")
            if connack_timeout == connack_timeouts[2]:
                test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))
            else:
                test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile())
            start_time = time()
            test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0','8800','"Mqtt connect.*"'))
            if test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('1'):
                test.socket_dynamic_profiles.append(SocketProfile(test.r1, test.socket_listener
                                                                  .dstl_get_urc().dstl_get_sis_urc_info_id(), '1'))
                test.r1.at1.read()

            if not connack_timeout:
                connack_timeout = 5
            urc_appeared = test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '502',
                                    '"Connection Refused, server unavailable."', timeout=int(connack_timeout)*2)
            if test.expect(urc_appeared, msg="Expected URC not appeared."):
                urc_end_time = int(time() - start_time)
                test.log.info("URC appeared after {} seconds. Expected value: {} seconds."
                              .format(urc_end_time, connack_timeout))
                test.expect(urc_end_time - connack_timeout < connack_timeout / 2,
                                msg="URC appeared, but not in expected time.")

            test.log.step("6. Check service and socket state AT^SISO.")
            test.expect(test.mqtt_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
            test.expect(test.mqtt_client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)

            test.log.step("7. Close connection.")
            test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())

            if connack_timeout == 5:
                test.log.step("8. Repeat steps 2-7, but for address parameters use syntax: user name, password, "
                              "(address to the TCP listener on Remote) and connackTimeout parameter = 45 sec; "
                              "e.g. mqtt://[username][:password]@host[:port];connackTimeout=45")
            if connack_timeout == connack_timeouts[1]:
                test.log.step("9. Repeat steps 2-7, but using different value for connackTimeout parameter "
                              "(open service using dynamic request e.g at^siso=0,2 and check result)")

    def cleanup(test):
        try:
            test.socket_listener.dstl_get_service().dstl_close_service_profile()
            test.socket_listener.dstl_get_service().dstl_reset_service_profile()
            test.mqtt_client.dstl_get_service().dstl_close_service_profile()
            test.mqtt_client.dstl_get_service().dstl_reset_service_profile()
            for socket_profile in test.socket_dynamic_profiles:
                socket_profile.dstl_get_service().dstl_close_service_profile()
                socket_profile.dstl_get_service().dstl_reset_service_profile()
        except AttributeError:
            test.log.error("Object was not created.")


if "__main__" == __name__:
    unicorn.main()
