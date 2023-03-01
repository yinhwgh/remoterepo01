# author: dirk.goesche@thalesgroup.com
# responsible: dirk.goesche@thalesgroup.com
# location: Berlin
# TC0107481.001

# This testcase tests the scope of the ATT provider certification for testcase tc04 of 19612 vers.20.3.

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.leshan_rest_client import LeshanRESTClient
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import *
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_defined_manufacturer
from dstl.internet_service.lwm2m_service import *
from dstl.identification.check_identification_ati import *


class Test(BaseTest):
    """
    Step 1) Configuration of the module for working together with the Leshan server
    Step 2) Start the LwM2M connection and check the registration status
    Step 3) Actual Testcase:
                 Purpose of this verification is to show conformance with the Device Object Read & Response
                 -LwM2M Server sends a Read (CoAP GET) command on Device Object (ID: /3)
                 -LWM2M Client returns the following node detail and values
                 -LWM2M Server received correct node detail and values from LWM2M Client
                   0: Manufacturer = As submitted to AT&T IOTS Onboarding Tool = Cinterion
                  17: Device Type = As submitted to AT&T IOTS Onboarding Tool  = Smart Device
                   1: Model Number = As submitted to AT&T IOTS Onboarding Tool = PLS83-W
                   2: Serial Number = IMEI
                  18: Hardware Version = As submitted to AT&T IOTS Onboarding Tool
                   3: Firmware Version = As submitted to AT&T IOTS Onboarding Tool
                  19: Software Version = 2 Digit SVN as defined in the PTCRB PPMD specification
    """

    def setup(test):
        test.dut.dstl_detect()
        #   test.dut.dstl_restart()
        test.dut.dstl_unlock_sim()
        test.dut.dstl_register_to_lte()

    def configure_dut(test):

        # syntax of the following lines: at^snlwm2m="cfg","attus","/0/1/0","coap://78.47.86.194:5683"
        # This is the server from AE Berlin
        test.dut.dstl_lwm2m_write_resource_to_mem("attus", "coap://78.47.86.194:5683", "0", "1", "0")
        # set security options to 3: (0=PSK  3=no_sec)
        test.dut.dstl_lwm2m_write_resource_to_mem("attus", "3", "0", "1", "2")
        # set the lifetime to 30 seconds
        test.dut.dstl_lwm2m_write_resource_to_mem("attus", "30", "1", "0", "1")

    def run(test):
        # Step 1
        test.configure_dut()

        # Step 2
        test.dut.dstl_lwm2m_start_service('attus')
        test.sleep(4)
        conn_status = test.dut.dstl_lwm2m_get_serv_conn_status('attus')
        test.log.info(f'The status of the LwM2M connection is: {conn_status}')

        test.dut.dstl_lwm2m_get_stack_status('attus')

        # Get the imei to identify the module endpoint on the server.
        imei = test.dut.dstl_get_imei()
        test.log.info(f'IMEI: {imei}')

        # This is the server from Gejo
        # server_url = 'http://123.56.164.183:10000'

        # This is the server from REN Shiming
        # server_url = 'http://182.92.198.110:8080'

        # This is the public Leshan server (LWM2M Sandbox)
        # server_url = 'https://leshan.eclipseprojects.io/'
        # server_url = 'https://23.97.187.154'

        # This is the server from AE Berlin
        # server_url = 'http://ae.c-wm.net:8080'
        server_url = 'http://78.47.86.194:8080'

        # server_url = 'http://ae.c-wm.net:8080/old/#'

        client = f'urn:imei:{imei}'
        proxy = 'http://10.50.101.11:3128'  # needed when executing script from firmnet
        server_version = '2.0.0'
        test.log.info(f'Server URL: {server_url}, Client endpoint: {client}')
        # Create an instance of LeshanRESTClient.
        lrc = LeshanRESTClient(server_url, client, proxy, server_version)
        # lrc = LeshanRESTClient(server_url, client, server_version)
        # timer added by dirk
        test.sleep(5)
        registered_clients = lrc.get_clients()
        test.log.info(f'Registered clients: {registered_clients}')

        client_is_registered = client in registered_clients

        # Step 3
        if client_is_registered:
            test.log.info(f'Client {client} is registered.')
            # timer added by dirk
            test.sleep(15)
            test.log.info(f' ')

            # 0: Manufacturer = As submitted to AT & T IOTS Onboarding Tool = Cinterion
            test.log.info('Read object "Device" resource "Manufacturer" /3/0/0')
            manufacturer = lrc.read('Device', '0', 'Manufacturer')
            test.log.info(f'The value 3/0/0 Manufacturer is: {manufacturer}')
            definition_manufacturer = test.dut.dstl_get_defined_manufacturer()
            test.log.info(f'The definition for Manufacturer is: {definition_manufacturer}')
            test.expect(manufacturer == definition_manufacturer)
            test.log.info(f' ')

            # 17: Device Type = As submitted to AT&T IOTS Onboarding Tool = Smart Device
            test.log.info('Read object "Device" resource "Device Type" /3/0/17')
            device_type = lrc.read('Device', '0', 'Device Type')
            test.log.info(f'The value 3/0/17 Device Type is: {device_type}')
            test.expect(device_type == "Smart Device")
            test.log.info(f' ')

            #  1: Model Number = As submitted to AT&T IOTS Onboarding Tool (for example: PLS83-W)
            test.log.info('Read object "Device" resource "Model Number" /3/0/1')
            model_number = lrc.read('Device', '0', 'Model Number')
            test.log.info(f'The value 3/0/1 Model Number is: {model_number}')
            # Get the model from the module.
            model_by_atc = test.dut.product + "-" + test.dut.variant
            test.log.info(f'Model by ATC is: {model_by_atc}')
            test.expect(model_number == model_by_atc)
            test.log.info(f' ')

            # 2: Serial Number = IMEI (for example: 004401083617635)
            test.log.info('Read object "Device" resource "IMEI" /3/0/2')
            serial_number = lrc.read('Device', '0', 'Serial Number')
            test.log.info(f'The value 3/0/2 IMEI is: {serial_number}')
            test.expect(serial_number == imei)
            test.log.info(f' ')

            # 18: Hardware Version = As submitted to AT&T IOTS Onboarding Tool (for example:  PLS83_W_R1)
            test.log.info('Read object "Device" resource "Hardware Version" /3/0/18')
            hardware_version = lrc.read('Device', '0', 'Hardware Version')
            test.log.info(f'The value 3/0/18 Hardware Version is: {hardware_version}')
            # get parts of the Hardware Version from the store
            hardware_version_store = test.dut.product + "_" + test.dut.variant + "_R1"
            test.log.info(f'The generated String for the HW version is: {hardware_version_store}')
            test.expect(hardware_version == hardware_version_store)
            test.log.info(f' ')

            # 3: Firmware Version = As submitted to AT&T IOTS Onboarding Tool (for example: 01.002.01.000.438)
            test.log.info('Read object "Device" resource "Firmware Version" /3/0/3')
            firmware_version = lrc.read('Device', '0', 'Firmware Version')
            test.log.info(f'The value 3/0/3 Firmware Version is: {firmware_version}')
            firmware_version_by_atc = test.dut.dstl_check_ati1_response(return_revision=True)
            test.log.info(f'The definition for firmware_version_by_atc is: {firmware_version_by_atc}')
            test.expect(firmware_version == firmware_version_by_atc)
            test.log.info(f' ')

            # 19: Software Version = 2 Digit SVN as defined in the PTCRB PPMD specification  (for example: 01)
            test.log.info('Read object "Device" resource "Software Version" /3/0/19')
            software_version = lrc.read('Device', '0', 'Software Version')
            test.log.info(f'The value 3/0/19 Software Version is: {software_version}')
            imei_sv = test.dut.dstl_check_ati176_response(return_svn=True)
            test.expect(software_version == imei_sv)
            test.log.info(f' ')

        else:
            test.log.error(f'Client {client} is not registered.')

    def cleanup(test):
        test.dut.dstl_restart()


if "__main__" == __name__:
    unicorn.main()
