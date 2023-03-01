# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107810.001

import unicorn

from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command
from tests.rq6.resmed_ehealth_initmodule_normal_flow import uc_init_module
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import NF_pre_config
from tests.rq6.resmed_ehealth_sendhealthdata_normal_flow import uc_send_healthdata
from core import dstl
from dstl.internet_service.profile.mqtt_profile import MqttProfile
from dstl.auxiliary.ip_server.mqtt_server import MqttServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles

rethread = False


class Test(BaseTest):
    """
     TC0107810.001-Resmed_eHealth_DownloadTaskList_NormalFlow
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        uc_init_module(test, 1)
        trigger_mqtt2(test)

    def run(test):
        NF_pre_config(test)
        test.log.step("Resmed_eHealth_DownloadTaskList_NormalFlow.")
        main_process(test)

    def cleanup(test):
        if test.dut.software_number == "100_038":
            test.log.info("Start downgrade")
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.808_arn01.000.00_lynx_100_038_to_rev00.042_arn01.000.00_lynx_100_028b_resmed_prod02sign.usf"'))
            test.expect(test.dut.at1.send_and_verify(
                'at^snfota="CRC","852b7532d11eecb3f3a2d7a1e731a6d50cf7b93c5cc76bd4fabb77241379c42c"'))
            test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
            test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
            test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
            test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
            test.sleep(5)
            dstl_detect(test.dut)
        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")


def EF_Soft_reset(test, checkstep, restart):
    if checkstep == restart:
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
        test.expect(test.dut.at1.wait_for('^SYSSTART'))
        main_process(test)
        return True
    else:
        return False


def trigger_mqtt(test):
    test.mqtt_server = MqttServer("IPv4", extended=True)
    test.client_id = dstl_get_imei(test.dut)
    test.topic_filter = "car/range"
    test.log.info("MqttSubscribe_basic")
    test.log.step('1) Depends on Module:\r\n''- define pdp context/nv bearer using CGDCONT '
                  'command and activate it using SICA command\r\n'
                  '- define Connection Profile using SICS command')
    test.connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

    test.log.step('2. Define Mqtt Subscribe profile with mandatory set of parameters using'
                  ' SISS command')
    test.expect(test.mqtt_server.dstl_run_mqtt_server())
    test.mqtt_subscribe = MqttProfile(test.dut, "0",
                                      test.connection_setup.dstl_get_used_cid(),
                                      alphabet=1, cmd="subscribe",
                                      topic_filter=test.topic_filter, client_id=test.client_id)
    test.mqtt_subscribe.dstl_set_parameters_from_ip_server(test.mqtt_server)
    test.mqtt_subscribe.dstl_generate_address()
    test.expect(test.mqtt_subscribe.dstl_get_service().dstl_load_profile())

    test.log.step('3) Open Mqtt profile using SISO command')
    test.expect(test.mqtt_subscribe.dstl_get_service().dstl_open_service_profile())

    test.log.step('4) Check service state using AT^SISO? command')
    test.log.info("executed in previous step")

    test.log.step('5) Close Mqtt profile using SISC command')
    test.expect(test.mqtt_subscribe.dstl_get_service().dstl_close_service_profile())
    dstl_kill_ssh_process(test, 'ssh_server', 'mosquitto -p {} -v'.format(test.mqtt_server.port_active),
                          indexes_to_kill=[1])
    # test.mqtt_server.dstl_stop_mqtt_server()
    test.mqtt_server.dstl_server_close_port()


def trigger_mqtt2(test):
    test.topic_filter = "test/basic"
    test.topic = "mqtttest"
    test.client_id = "mqttSub001"
    test.data = "some test data"
    test.qos = "0"
    dstl_reset_internet_service_profiles(test.dut, force_reset=True)
    test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
    test.connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())
    test.mqtt_server = MqttServer("IPv4", extended=True)
    test.expect(test.mqtt_server.dstl_run_mqtt_server())

    test.log.step('=== 1. Create MQTT client profile mandatory parameters only.\n \
                        Dynamic MQTT parameters will be used during connection.\n \
                        srvType - "Mqtt" \n \
                        conId - e.g. 0 \n \
                        address - mqtt://<host>:<port> ===')
    test.mqtt_client = MqttProfile(
        test.dut, '0', test.connection_setup.dstl_get_used_cid(), cmd='subscribe',
        topic=test.topic, topic_filter=test.topic_filter, client_id=test.client_id)
    test.mqtt_client.dstl_set_host(test.mqtt_server.dstl_get_server_ip_address())
    test.mqtt_client.dstl_set_port(test.mqtt_server.dstl_get_server_port())
    test.mqtt_client.dstl_generate_address()
    test.expect(test.mqtt_client.dstl_get_service().dstl_load_profile())

    test.log.step('=== 2. Open MQTT Client profile using SISO command.\
                        Set <optParam> to 2 - dynamic parameters OR dynamic request. ===')
    test.expect(test.mqtt_client.dstl_get_service().dstl_open_service_profile(opt_param=2))

    test.log.step('=== 3. Check if correct URCs appears. ===')
    test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sis_urc_appeared('0', '2500'))
    test.expect(f"Received SUBSCRIBE from {test.client_id}" and
                f"{test.client_id} {test.qos} {test.topic_filter}" in
                test.mqtt_server.dstl_read_data_on_ssh_server())

    test.log.step('=== 4. Configure mandatory SUBSCRIBE mode parameters using SISD command: \n \
                        Cmd - "Subscribe" \n \
                        topicFilter - e.g. "test_topic1;testtopic2;topic312345;topic4;topic_@555". ===')
    test.expect(test.mqtt_client.dstl_get_dynamic_service()
                .dstl_sisd_set_param_mqtt_cmd('subscribe'))
    test.expect(test.mqtt_client.dstl_get_dynamic_service()
                .dstl_sisd_set_param_topic_filter(test.topic))

    test.log.step('=== 5. Send request using SISU command. ===')
    test.expect(test.mqtt_client.dstl_get_dynamic_service().dstl_sisu_send_request())

    test.log.step('=== 6. Check if correct URCs appears and socket/srv state. ===')
    test.log.info("=== URC was checked in previous step ===")
    test.expect(test.mqtt_client.dstl_get_parser().
                dstl_get_service_state() == ServiceState.UP.value)
    test.expect(f"Received SUBSCRIBE from {test.client_id}" and
                f"{test.client_id} {test.qos} {test.topic}" in
                test.mqtt_server.dstl_read_data_on_ssh_server())

    test.log.step('=== 7. Send publish request with one of the topic from server or using '
                  'other service profile. ===')
    test.expect(test.mqtt_server.
                dstl_mqtt_publish_send_request(topic=test.topic, data=test.data))
    test.sleep(10)

    test.log.step('=== 8. Check if SISR URC appear and read data. ===')
    test.expect(test.mqtt_client.dstl_get_urc().dstl_is_sisr_urc_appeared(urc_cause_id='1'))
    test.expect(test.mqtt_client.dstl_get_service()
                .dstl_read_return_data(len(test.data)) == test.data)

    test.log.step('=== 9. Check socket and srv state. ===')
    test.expect(test.mqtt_client.dstl_get_parser().
                dstl_get_service_state() == ServiceState.UP.value)

    test.log.step('=== 10. Check server log. ===')
    test.log.info('=== Corresponding checks were done after proper steps. ===')

    test.log.step('=== 11. Close MQTT Client profile. ===')
    test.expect(test.mqtt_client.dstl_get_service().dstl_close_service_profile())
    dstl_kill_ssh_process(test, 'ssh_server', 'mosquitto -p {} -v'.format(test.mqtt_server.port_active),
                          indexes_to_kill=[1])
    test.mqtt_server.dstl_server_close_port()


def dstl_kill_ssh_process(test, ssh_server_property, process_name, indexes_to_kill=[0]):
    """
    Method allows to kill specified process on server. Allowed only for generic IP server..
    Args:
        ssh_server_property(String): used SSH server property, e.g. 'ssh_server'.
        process_name(String): name of process to be closed (killed).
        indexes_to_kill(String): list of indexes of processes to be killed. Optional parameter. Default value: [0]
    """
    dstl.log.h2("DSTL execute: 'dstl_kill_ssh_process'.")
    if not test.mqtt_server.standard_server:
        if not process_name:
            return
        test.mqtt_server.ssh_server_property_name = ssh_server_property
        ssh_server = eval("dstl.test.{}".format(test.mqtt_server.ssh_server_property_name))
        ssh_server._check_connection()
        ssh_server.send_and_receive('ps -aux | grep "{}"'.format(process_name))
        server_response = ssh_server.last_response.split('\n')
        try:
            for index in indexes_to_kill:
                if 'grep' in server_response[index]:
                    dstl.log.info('No maching process found.')
                else:
                    process_id = server_response[index].replace('  ', ' ').replace('  ', ' ').split(' ')[2]
                    ssh_server.send_and_receive('sudo kill {}'.format(process_id))
        except IndexError:
            dstl.log.warn('Incorrect response - cannot parse process ID.')
    else:
        dstl.expect(False, msg="Extended IpServer is required for execution of this method.", critical=True)


def main_process(test, restart=0):
    test.log.step("1. Configures the IP service connection profile 0 "
                  "with an inactive timeout set to 90 seconds and a private APN using AT^SICS.")
    server_send_data = dstl_generate_data(1500)
    connection_setup = dstl_get_connection_setup_object(test.dut)
    test.expect(connection_setup.dstl_load_internet_connection_profile())
    test.expect(connection_setup.dstl_activate_internet_connection(),
                msg="Could not activate PDP context")
    socket_service = SocketProfile(test.dut, "0", connection_setup.dstl_get_used_cid(),
                                   host=test.ip_address,
                                   port=test.port_number,
                                   protocol="tcp", secure_connection=True, tcp_ot="90")
    socket_service.dstl_generate_address()
    test.expect(socket_service.dstl_get_service().dstl_load_profile())
    if EF_Soft_reset(test, 1, restart):
        return True

    test.log.step("2.  Closes the internet service profile (ID 0) and configures this service profile "
                  "as a secure TCP socket in non-transparent mode (server authentication only)")
    socket_service.dstl_set_secopt("1")
    test.expect(socket_service.dstl_get_service().dstl_write_secopt())
    if EF_Soft_reset(test, 2, restart):
        return True

    test.log.step("3. Open socket profile.")
    test.dut.at1.send_and_verify('AT^SISC=0', 'OK', handle_errors=True)
    test.sleep(5)
    if rethread and restart == 0:
        ssl_server_thread = test.thread(test.ssl_server.dstl_run_ssl_server)
        test.sleep(30)
    test.expect(socket_service.dstl_get_service().dstl_open_service_profile(), critical=True)
    test.expect(socket_service.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
    if EF_Soft_reset(test, 3, restart):
        return True

    test.log.step('4. Server send 1500 data ')
    test.log.info('Server send 1500 data*10 ')
    for i in range(10):
        test.ssl_server.dstl_send_data_from_ssh_server(data=server_send_data, ssh_server_property='ssh_server')
        test.sleep(1)
    if EF_Soft_reset(test, 4, restart):
        return True

    test.log.step("5. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks.")
    for i in range(10):
        test.expect(socket_service.dstl_get_service().dstl_read_data
                    (req_read_length=1500, repetitions=1))
        test.sleep(1)
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.UP.value)
    if EF_Soft_reset(test, 5, restart):
        return True

    test.log.step("6. Closes internet service profile after the successful download of the file.")
    test.expect(socket_service.dstl_get_service().dstl_close_service_profile())
    test.expect(socket_service.dstl_get_parser().dstl_get_service_state(
        at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
    if EF_Soft_reset(test, 6, restart):
        return True

    test.log.step("7. Configure SNFOTA feature (URL, CID, hash).")
    test.expect(test.dut.at1.send_and_verify('at^snfota="urc",1'))
    test.expect(test.dut.at1.send_and_verify('at^snfota="conid",{}'.format(connection_setup.dstl_get_used_cid())))
    test.expect(test.dut.at1.send_and_verify(
        'at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.042_arn01.000.00_lynx_100_028b_to_rev00.808_arn01.000.00_lynx_100_038_resmed_prod02sign.usf"'))
    test.expect(test.dut.at1.send_and_verify(
        'at^snfota="CRC","46281f90efd94b6e296f2df6be8398575b9764692ccb6a752b50feeb740f37a3"'))
    if EF_Soft_reset(test, 7, restart):
        return True

    test.log.step("8. Trigger the download.")
    test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))
    download_succeed = test.dut.at1.wait_for("\\^SNFOTA:act,0,0,100", timeout=180)
    if download_succeed:
        test.log.info("downlaod successfully")
    else:
        test.expect(False, critical=True)
    if EF_Soft_reset(test, 8, restart):
        return True

    test.log.step("9. Trigger the firmware swap process.")
    test.expect(test.dut.at1.send_and_verify('AT^SFDL=2'))
    test.expect(test.dut.at1.wait_for('^SYSSTART', timeout=900))
    if EF_Soft_reset(test, 9, restart):
        return True

    test.log.step("10. Check the module's SW version.")
    test.sleep(5)
    dstl_detect(test.dut)
    test.expect(test.dut.software_number == "100_038")
    if EF_Soft_reset(test, 10, restart):
        return True

    test.log.step("11. Softreset the module (AT+CFUN=1,1).")
    test.expect(test.dut.at1.send_and_verify('AT+CFUN=1,1', 'OK'))
    test.expect(test.dut.at1.wait_for('^SYSSTART'))

    test.log.step("12. Initialize the module.")
    uc_init_module(test, 1)

    test.log.step("13.  Send report to task server via IP services.")
    test.ssh_server.close()
    test.sleep(10)
    NF_pre_config(test)
    uc_send_healthdata(test, 1)


if __name__ == "__main__":
    unicorn.main()
