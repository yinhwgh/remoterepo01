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

class Lwm2mATcommandTest(BaseTest):
    def setup(test):
        #test.dut.dstl_detect()
        #test.dut.dstl_restart()
        #test.dut.dstl_unlock_sim()
        #test.dut.dstl_register_to_gsm()
        pass

    def handle_response(test, exp_resp):
        if "OK" == exp_resp:
            #expect OK
            if exp_resp in test.dut.at1.last_response:
                test.log.info("expected response "+exp_resp+" received")
            else:
                test.log.info("!!! unexpected other response: "+test.dut.at1.last_response)
        else:
            # expect other...
            expected_response = exp_resp
            if "+CME ERROR: not found" == exp_resp:
                expected_response2="22"
            elif "+CME ERROR: unknown" == exp_resp:
                expected_response2="100"
            elif "+CME ERROR: operation temporary not allowed" == exp_resp:
                expected_response2="256"
            elif "+CME ERROR: operation not allowed" == exp_resp:
                expected_response2="302"
            elif "+CME ERROR: operation not supportet" == exp_resp:
                expected_response2="303"
            #elif "+CME ERROR: xxx" == exp_resp:
            #    expected_response2="???"
            else:
                expected_response2="???"

            if expected_response in test.dut.at1.last_response:
                test.log.info("expected response "+expected_response+" received")
            elif expected_response2 in test.dut.at1.last_response:
                test.log.info("expected response "+expected_response2+"="+expected_response+" received")
            else:
                if "+CME ERROR: " in test.dut.at1.last_response:
                    test.log.info("!!! unexpected CME ERROR response: "+test.dut.at1.last_response)
                else:
                    test.log.info("!!! unexpected other response: "+test.dut.at1.last_response)

    def snlwm2m_cmd(test, lwm2m_cmd, par_2, par_3, par_4, par_5, par_6, exp_rsp, timeout_val, sleep_val):
        # SNLWM2M command
        if par_2 != "":
            int_par_2 = ","+par_2
        else:
            int_par_2 = ""
        
        if par_3 != "":
            int_par_3 = ","+par_3
        else:
            int_par_3 = ""
        
        if par_4 != "":
            int_par_4 = ","+par_4
        else:
            int_par_4 = ""
        
        if par_5 != "":
            int_par_5 = ","+par_5
        else:
            int_par_5 = ""
        
        if par_6 != "":
            int_par_6 = ","+par_6
        else:
            int_par_6 = ""
        
        if exp_rsp == "":
            int_exp_rsp = "OK"
        else:
            int_exp_rsp = exp_rsp

        #test.log.info("parameters:\n"+lwm2m_cmd+" "+par_2+" "+par_3+" "+par_4+" "+par_5+" "+par_6+"\n"+exp_rsp)
        #test.log.info("internal parameters:\n"+int_par_2+" "+int_par_3+" "+int_par_4+" "+int_par_5+" "+int_par_6+"\n"+int_exp_rsp)
        test.log.info("command:\nat^snlwm2m="+lwm2m_cmd+int_par_2+int_par_3+int_par_4+int_par_5+int_par_6, "\nresponse:\n"+int_exp_rsp, "timeout="+timeout_val, "sleep="+sleep_val)
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m='+lwm2m_cmd+int_par_2+int_par_3+int_par_4+int_par_5+int_par_6, int_exp_rsp, timeout_val))
        Lwm2mATcommandTest.handle_response(test, int_exp_resp)
        test.sleep(sleep_val)

    def snlwm2m_act_cmd(test, client_id, start_stop, exp_rsp):
        Lwm2mATcommandTest.snlwm2m_cmd(test, "act", client_id, start_stop, "", "", "", exp_rsp, 5, 1)

    def snlwm2m_regupd_cmd(test, client_id, reg_num, exp_rsp):
        Lwm2mATcommandTest.snlwm2m_cmd(test, "act", client_id, "regUpdate", reg_num, "", "", exp_rsp, 5, 1)

    def snlwm2m_cfg_coap_cmd(test, client_id, dest_adr, coap_srv, coap_res, exp_rsp):
        # SNLWM2M cfg coap command example: client_id="attus", dest_adr="/0/0/0", coap_srv="coap://78.8.146.92:10040", coap_res="0,24"
        # example command:                  AT^SNLWM2M="cfg","attus","0/0/0","coap://78.8.146.92:10040"
        #         response:                 ^SNLWM2M: "cfg","attus","0/0/0","coap://78.8.146.92:10040",0,24
        if exp_rsp != "":
            expected_response = exp_rsp
        else:
            expected_response = "^SNLWM2M: \"cfg\",\""+client_id+"\",\""+dest_adr+"\",\""+coap_srv+"\","+coap_res

        Lwm2mATcommandTest.snlwm2m_cmd(test, "cfg", client_id, dest_adr, coap_srv, "", "", expected_response, 5, 5)

    def snlwm2m_cfg_coap_req(test, client_id, dest_adr, coap_srv, coap_res, exp_rsp):
        if exp_resp != "":
            expected_response = esp_rsp
        else:
            expected_response = "^SNLWM2M: \"cfg\",\""+client_id+"\",\""+dest_adr+"\",\""+coap_srv+"\","+coap_res

        Lwm2mATcommandTest.snlwm2m_cmd(test, "cfg", client_id, dest_adr, coap_srv, "", "", expected_response, 5, 5)

    # ######################################################################

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

        client_id="attus"
        dest_addr="/0/0/0"
        coap_server1="coap://78.8.146.92:10030"
        coap_server2="coap://78.8.146.92:10040"

        Lwm2mATcommandTest.snlwm2m_act_cmd(test, client_id, "start", "OK")
        
        Lwm2mATcommandTest.snlwm2m_cfg_coap_cmd(test, client_id, dest_addr, coap_server1, "0,24", "")

        Lwm2mATcommandTest.snlwm2m_cfg_coap_cmd(test, client_id, dest_addr, "", "", "^SNLWM2M: \"cfg\",\""+client_id+"\",\""+dest_addr+"\",\""+coap_server1+"\",0,24")

        Lwm2mATcommandTest.snlwm2m_cfg_coap_cmd(test, client_id, dest_addr, coap_server2, "0,24", "")

        Lwm2mATcommandTest.snlwm2m_cfg_coap_cmd(test, client_id, dest_addr, "", "", "^SNLWM2M: \"cfg\",\""+client_id+"\",\""+dest_addr+"\",\""+coap_server2+"\",0,24")

        Lwm2mATcommandTest.snlwm2m_act_cmd(test, client_id, "stop", "OK")
        
################# TODO add more AT commands ####################

    def cleanup(test):
        # nothing to do ...
        # ... if wrong FW version => turn off device, i.e. VBAT off ???
        pass

if "__main__" == __name__:
    unicorn.main()
