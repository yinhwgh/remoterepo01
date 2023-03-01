# author: johann.suhr@thalesgroup.com
# Does not belong to a TC. Only for demonstration purposes.

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.leshan_rest_client import LeshanRESTClient
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import *
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.lwm2m_service import *


class Test(BaseTest):
    """
    Step 1) Check the registration state of the module
    Step 2) Configuration of the module for working together with the Leshan server
    Step 3) Start the LwM2M connection and check the registration status
    Step 4) Actual Testcase:
                - read the lifetime
                - check if lifetime is 60 seconds
                - write 55 to lifetime
                - check if lifetime is 55
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_unlock_sim()
        test.dut.dstl_register_to_lte()

    def configure_dut(test):

        # test.dut.dstl_lwm2m_stop_service('Leshan')
        # test.dut.dstl_lwm2m_stop_service('LeShan')

        #   This is the server address from Gejo: coap://123.56.164.183:10001
        #   This is the server address from REN Shiming: coap://182.92.198.110:5683

        # This is the server from AE Berlin
        test.dut.at1.send_and_verify('"at^snlwm2m="cfg","attus","/0/1/0","coap://78.47.86.194:5683"', "^SNLWM2M: \"cfg\",\"attus\",\"/0/1/0\",\"coap://leshan.eclipseprojects.io:5683\",1,37")
        # set security options: (0=PSK  3=no_sec)
        test.dut.at1.send_and_verify('at^snlwm2m="cfg","attus","/0/1/2",3')
        # set the lifetime to 60 seconds
        test.dut.at1.send_and_verify('at^snlwm2m="cfg","attus","/1/0/1",60')

    def run(test):
        # Step 1
        #test.dut.at1.send_and_verify('AT+CGDCONT?', '+CGDCONT: 1,\"IP\",\"web.vodafone.de\",\"0.0.0.0\",0,0')

        # Step 2
        test.configure_dut()

        # Step 3
        test.dut.dstl_lwm2m_start_service('attus')
        test.dut.dstl_lwm2m_get_serv_conn_status('attus')
        test.sleep(10)
        test.dut.dstl_lwm2m_get_serv_conn_status('attus')
        test.sleep(10)
        test.dut.dstl_lwm2m_get_serv_conn_status('attus')
        test.sleep(10)
        test.dut.dstl_lwm2m_get_serv_conn_status('attus')

        # Get the imei to identify the module endpoint on the server.
        imei = test.dut.dstl_get_imei()
        test.log.info(f'IMEI: {imei}')

        # This is the server from Gejo
        #server_url = 'http://123.56.164.183:10000'

        # This is the server from REN Shiming
        #server_url = 'http://182.92.198.110:8080'

        # This is the public Leshan server (LWM2M Sandbox)
        #server_url = 'https://leshan.eclipseprojects.io/'
        #server_url = 'https://23.97.187.154'

        # This is the server from AE Berlin
        #server_url = 'http://ae.c-wm.net:8080'
        server_url = 'http://78.47.86.194:8080'

        client = f'urn:imei:{imei}'
        proxy = 'http://10.50.101.10:3128'  # needed when executing script from firmnet
        server_version = '1.0.0'  # use as parameter for LeshanRESTClient constructor otherwise version 2.0.0 is assumed

        test.log.info(f'Server URL: {server_url}, Client endpoint: {client}')

        # Create an instance of LeshanRESTClient.
        lrc = LeshanRESTClient(server_url, client, proxy, server_version)

        registered_clients = lrc.get_clients()
        test.log.info(f'Registered clients: {registered_clients}')

        client_is_registered = client in registered_clients

        # Step 4
        if client_is_registered:
            test.log.info(f'Client {client} is registered.')

            test.log.info('Read the Lifetime resource of instance 0 of LwM2M Server object.')
            lifetime = lrc.read('LwM2M Server', '0', 'Lifetime')
            test.log.info(f'The lifetime is: {lifetime}')
            test.expect(lifetime == 60)

            test.log.info('Write the value 55 to the Lifetime resource of instance 0 of LwM2M Server object.')
            lrc.write('LwM2M Server', '0', 'Lifetime', 55)
            test.log.info('Read the Lifetime')
            lifetime = lrc.read('LwM2M Server', '0', 'Lifetime')
            test.expect(lifetime == 55)

        else:
            test.log.error(f'Client {client} is not registered.')

    def cleanup(test):
        test.dut.dstl_restart()


if "__main__" == __name__:
    unicorn.main()
