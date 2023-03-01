#responsible: thomas.hinze@thalesgroup.com
#location: Berlin
#TC0000001.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.internet_service.leshan_rest_client import LeshanRESTClient
from dstl.security.lock_unlock_sim import dstl_unlock_sim
from dstl.network_service.register_to_network import *
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_defined_identification import dstl_defined_manufacturer
from dstl.identification.get_identification import dstl_collect_ati_information_from_other_commands

class Lwm2mHelloWorldTest(BaseTest):
    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_restart()
        #test.dut.dstl_unlock_sim()
        #test.dut.dstl_register_to_gsm()
        pass

    def run(test):

        #server_url = 'http://123.56.164.183:10000'
        try:
            server_url = test.lwm2m1_url
        except AttributeError:
            test.log.info("missing LWM2M server url")
            test.fail()

        #proxy = 'http://10.50.101.10:3128'
        try:
            proxy = test.lwm2m1_proxy
        except AttributeError:
            proxy = None
        test.log.info(f"proxy: {proxy}")

        server_version = '1.0.0'

        # Create an instance of LeshanRESTClient.
        lrc = LeshanRESTClient(server_url, None, proxy, server_version)

        imei = test.dut.dstl_get_imei()
        test.log.info(f'IMEI: {imei}')

        client_ep_name = f'urn:imei:{imei}'
        test.log.info(f'Server URL: {server_url}, Client endpoint: {client_ep_name}')

        test.log.info("Activate context")
        test.dut.at1.send_and_verify('AT^SICA=1,1')

        test.log.info("Start LWM2M client: att")
        test.dut.at1.send_and_verify('AT^SNLWM2M=act,attus,start', ".*OK")

        test.log.warning("Wait until client is started - using poor-mans-solution (sleep)")
        test.sleep(5)

        # check if client is registered
        registered_clients = lrc.get_clients()
        test.log.info(f'Registered clients: {registered_clients}')

        client_is_registered = client_ep_name in registered_clients

        if not client_is_registered:
            test.log.error(f'Client {client_ep_name} is not registered.')
            test.fail()

        test.log.info(f'Client {client_ep_name} is registered.')
        lrc.set_client(client_ep_name)

        test.log.info('get data')
        manufacturer = lrc.read(3,0,0)
        test.log.info(f'manufacturer: {manufacturer}.')
        test.expect(manufacturer == test.dut.dstl_defined_manufacturer())

        test.dut.at1.send_and_verify("AT+CGMM", ".*OK.*")
        response_list = list(filter(None, test.dut.at1.last_response.split('\r\n')))
        cgmm_value = response_list[
            response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value

        model_no = lrc.read(3,0,1)
        test.log.info(f'model_no: {model_no}.')
        test.expect(model_no == cgmm_value)

        serial_no = lrc.read(3,0,2)
        test.log.info(f'serial_no: {serial_no}.')
        test.expect(serial_no == test.dut.dstl_get_imei())

        test.dut.at1.send_and_verify("AT+CGMR", ".*OK.*")
        response_list = list(filter(None, test.dut.at1.last_response.split('\r\n')))
        cgmr_value = response_list[
            response_list.index('OK') - 1]  # The last item is 'OK', the penultimate should be value
        cgmr_value = cgmr_value.replace('REVISION ', '')
        
        fw_version = lrc.read(3,0,3)
        test.log.info(f'fw_version: {fw_version}.')
        test.log.info(f'cgmr_value: {cgmr_value}.')
        test.expect(fw_version == cgmr_value)

    def cleanup(test):
        # nothing to do ...
        # ... if wrong FW version => turn off device, i.e. VBAT off ???
        pass

if "__main__" == __name__:
    unicorn.main()
