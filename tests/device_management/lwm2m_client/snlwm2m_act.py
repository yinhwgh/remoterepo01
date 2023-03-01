import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.devboard import devboard

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
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

    def snlwm2m_act_cmd(test, client_id, start_stop, exp_resp):
        test.log.info(start_stop+" LWM2M client: "+client_id)
        test.expect(test.dut.at1.send_and_verify("at^snlwm2m=\"act\",\""+client_id+"\",\""+start_stop+"\"", exp_resp, timeout=5))
        test.sleep(5)
        Lwm2mATcommandTest.handle_response(test, exp_resp)

    def snlwm2m_srvstatus_req(test, client_id, reg_num):
        #test.dut.at1.send_and_verify("at^snlwm2m=\"status/srv\"","^SNLWM2M: \"status/srv\",\""+client_id+"\","+reg_num+",registered")
        test.dut.at1.send_and_verify("at^snlwm2m=status/srv","^SNLWM2M: \"status/srv\",\""+client_id+"\","+reg_num+",registered")
        test.sleep(1)
        Lwm2mATcommandTest.handle_response(test, "^SNLWM2M: \"status/srv\",\""+client_id+"\","+reg_num+",registered")

    def snlwm2m_regupd_cmd(test, client_id, reg_num, exp_resp):
        test.log.info("reg update for client "+client_id+" with number "+reg_num+", expect "+exp_resp)
        test.expect(test.dut.at1.send_and_verify("at^snlwm2m=\"act\",\""+client_id+"\",\"regUpdate\","+reg_num, exp_resp, timeout=5))
        #Lwm2mATcommandTest.handle_response(test, exp_resp)
        test.sleep(1)
        Lwm2mATcommandTest.handle_response(test, "^SNLWM2M: \"status/srv\",\""+client_id+"\","+reg_num+",connecting")
        test.sleep(10)
        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test, client_id, reg_num)

    def run(test):
        test.log.info("Activate context")
        test.dut.at1.send_and_verify('AT^SICA=1,1')
        
        test.log.info("===== act-test begin =====")

        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"attus","start","OK")

        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"attus","100")

        Lwm2mATcommandTest.snlwm2m_regupd_cmd(test,"attus","100","OK")

        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"attus","100")
        
        Lwm2mATcommandTest.snlwm2m_regupd_cmd(test,"attus","99","+CME ERROR: not found")

        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"attus","99")

        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"attus","start","+CME ERROR: operation temporary not allowed")
        
        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"attus","stop","OK")

        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"attus","100")
        
        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"attus","stop","+CME ERROR: operation temporary not allowed")
        
        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"verizonus","start","OK")
        
        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"verizonus","100")
        
        Lwm2mATcommandTest.snlwm2m_regupd_cmd(test,"verizonus","100","OK")
        
        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"verizonus","100")
        
        Lwm2mATcommandTest.snlwm2m_regupd_cmd(test,"verizonus","99","+CME ERROR: not found")
        
        Lwm2mATcommandTest.snlwm2m_srvstatus_req(test,"verizonus","99")

        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"verizonus","stop","OK")

        Lwm2mATcommandTest.snlwm2m_act_cmd(test,"verizonusx","start","+CME ERROR: not found")

        test.log.info("===== act-test end =====")
        
        ################# TODO add more AT commands ####################

    def cleanup(test):
        # nothing to do ...
        # ... if wrong FW version => turn off device, i.e. VBAT off ???
        pass

if "__main__" == __name__:
    unicorn.main()
