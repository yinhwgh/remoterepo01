# responsible: sebastian.lupkowski@globallogic.com
# location: Wroclaw
# TC0091874.001

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.security.lock_unlock_sim import dstl_lock_sim
from dstl.packet_domain.pdp_context_operation import *

class Test(BaseTest):
    """
    TC0091874.001    TpAtCgdcontBasic

    This procedure provides the possibility of basic tests for the test, read and write command of +CGDCONT.

    Step 1: Check command without and with PIN
    Step 2: Check for valid and invalid parameters
    Step 3: Store user defined context
    Step 4: Restart module and check NV parameters of CGDCONT
    """
    contexts = []
    def setup(test):
        test.log.step('product detect,get imei and lock sim')
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_lock_sim(test.dut)
        dstl_restart(test.dut)
        test.log.step('Creating backup of the contexts')
        test.contexts = dstl_backup_pdp_context(test.dut)
        test.log.step('Clearing contexts')
        dstl_clear_contexts(test.dut)
    
    def run(test):
        test.log.step("1. Check command without and with PIN")
        test_cgdcont(test)
        check_cgdcont_cid(test, 'write')
        check_cgdcont_cid(test, 'read')

        test.expect(dstl_enter_pin(test.dut))
        test.sleep(10)  # waiting for module to get ready
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", ".*OK.*"))
        test.sleep(10)  # waiting for complete network deregistration
        
        test_cgdcont(test)
        check_cgdcont(test, 'write', 'OK', '2,"IP","{}2"'.format(test.dut.sim.apn_v4))
        if test.dut.project == "SERVAL":
            check_cgdcont(test, 'read', 'OK', f'[+]CGDCONT: 1,"IP","{test.dut.sim.apn_v4}","0.0.0.0",0,0.*'
                                              f'[+]CGDCONT: 2,"IP","{test.dut.sim.apn_v4}2","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 4,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 8,"Non-IP","TestAPNNONIP".*'
                                              '[+]CGDCONT: 12,"IPV6","TestAPNIPV6","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 16,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*')
        else:
            check_cgdcont(test, 'read', 'OK', f'[+]CGDCONT: 1,"IP","{test.dut.sim.apn_v4}","0.0.0.0",0,0.*'
                                              f'[+]CGDCONT: 2,"IP","{test.dut.sim.apn_v4}2","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 3,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 4,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 5,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 6,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 7,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 8,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 9,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 10,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 11,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 12,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 13,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 14,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 15,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 16,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*')
        test.log.info('Clearing contexts')
        dstl_clear_contexts(test.dut)
        check_cgdcont_cid(test, 'write')
        check_cgdcont_cid(test, 'read')
        
        test.log.step("2. Step 2: Check for valid and invalid parameters")
        dstl_clear_contexts(test.dut)
        check_cgdcont(test, 'write', 'OK', '1,"IP"')
        check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","","0.0.0.0",0,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IPV6"')
        check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IPV6","","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IPV4V6"')
        check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IPV4V6","","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IP","internet1"')
        check_cgdcont(test, 'write', 'OK', '2,"IPV6","internet2"')
        check_cgdcont(test, 'write', 'OK', '3,"IPV4V6","internet3"')
        check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","0.0.0.0",0,0.*'
                                          '[+]CGDCONT: 2,"IPV6","internet2","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0.*'
                                          '[+]CGDCONT: 3,"IPV4V6","internet3","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IP","internet1","192.192.192.192"')
        check_cgdcont(test, 'write', 'OK', '2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1"')
        check_cgdcont(test, 'write', 'OK', '3,"IPV4V6","internet3","193.193.193.193"')
        if test.dut.project == 'VIPER':
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","192.192.192.192",0,0.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",0,0.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","193.193.193.193",0,0')
        else:
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",0,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IP","internet1","192.192.192.192",0')
        check_cgdcont(test, 'write', 'OK', '2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",1')
        check_cgdcont(test, 'write', 'OK', '3,"IPV4V6","internet3","193.193.193.193",2')
        if test.dut.project == "VIPER":
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","192.192.192.192",0,0.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",1,0.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","193.193.193.193",2,0')
        else:
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",1,0.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",2,0')
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'OK', '1,"IP","internet1","192.192.192.192",0,4')
        check_cgdcont(test, 'write', 'OK', '2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",1,3')
        check_cgdcont(test, 'write', 'OK', '3,"IPV4V6","internet3","193.193.193.193",2,0')
        check_cgdcont(test, 'write', 'OK', '4,"IP","internet4","194.194.194.194",1,2')
        check_cgdcont(test, 'write', 'OK', '5,"IPV6","internet5","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",2,1')
        if test.dut.project == "VIPER":
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","192.192.192.192",0,4.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",1,3.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","193.193.193.193",2,0.*'
                                              '[+]CGDCONT: 4,"IP","internet4","194.194.194.194",1,2.*'
                                              '[+]CGDCONT: 5,"IPV6","internet5","38.0.3.128.128.97.0.189.0.0.0.85.158.142.35.1",2,1')
        else:
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","internet1","0.0.0.0",0,4.*'
                                              '[+]CGDCONT: 2,"IPV6","internet2","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",1,3.*'
                                              '[+]CGDCONT: 3,"IPV4V6","internet3","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",2,0.*'
                                              '[+]CGDCONT: 4,"IP","internet4","0.0.0.0",1,2.*'
                                              '[+]CGDCONT: 5,"IPV6","internet5","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0",2,1')
        dstl_clear_contexts(test.dut)
        
        for cid in range(1, 17):
            check_cgdcont(test, 'write', 'OK', '{0},"IP","internet{0}"'.format(cid))
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: {0},"IP","internet{0}","0.0.0.0",0,0'.format(cid))
        dstl_clear_contexts(test.dut)
        
        check_cgdcont(test, 'write', 'CME ERROR', '-1')
        check_cgdcont(test, 'write', 'CME ERROR', '0')
        check_cgdcont(test, 'write', 'CME ERROR', '1,"abc"')
        check_cgdcont(test, 'write', 'CME ERROR', '1,"IP","$%&"')
        check_cgdcont(test, 'write', 'CME ERROR', '1,"IP","internet","2000"')
        check_cgdcont(test, 'write', 'CME ERROR', '1,"IP","internet","0.0.0.0",100')
        check_cgdcont(test, 'write', 'CME ERROR', '1,"IP","internet","0.0.0.0",1,1000')
        check_cgdcont(test, 'write', 'CME ERROR', '99,"IP","internet","0.0.0.0",1,1')
        
        test.log.step("3. Store user defined context")
        check_cgdcont(test, 'write', 'OK', '1,"IP","{}","192.192.192.192",1,1'.format(test.dut.sim.apn_v4))
        
        test.log.step("4. Restart module and check NV parameters of CGDCONT")
        test.expect(dstl_restart(test.dut))
        if test.dut.project == 'VIPER':
            check_cgdcont(test, 'read', 'OK',
                          '[+]CGDCONT: 1,"IP","{}","192.192.192.192",1,1'.format(test.dut.sim.apn_v4))
        else:
            check_cgdcont(test, 'read', 'OK', '[+]CGDCONT: 1,"IP","{}","0.0.0.0",1,1'.format(test.dut.sim.apn_v4))
    
    def cleanup(test):
        test.log.step('Clearing contexts and restoring original contexts')
        dstl_clear_contexts(test.dut)
        for line in test.contexts:
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={}".format(line), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def check_cgdcont(test, mode, expected_response, value='0'):
    if mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={}".format(value), ".*{}.*".format(expected_response)))
    else:
        if expected_response is 'OK':
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*{}.*OK.*".format(value)))
        else:
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT?", ".*{}.*".format(expected_response)))


def test_cgdcont(test):
    if test.dut.project == "SERVAL":
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?',
                                                 '.*[+]CGDCONT: \\(1-16\\),"IP",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"IPV6",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"IPV4V6",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"Non-IP",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*OK.*'))
    else:
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=?',
                                                 '.*[+]CGDCONT: \\(1-16\\),"IP",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"PPP",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"IPV6",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*[+]CGDCONT: \\(1-16\\),"IPV4V6",,,\\(0-2\\),\\(0-4\\)'
                                                 '.*OK.*'))
def check_cgdcont_cid(test, mode):
    if mode is 'write':
        if test.dut.project == "SERVAL":
            check_cgdcont(test, 'write', 'OK', '16,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'CME ERROR', '15,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '12,"IPV6","TestAPNIPV6","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'CME ERROR', '11,"IPV6","TestAPNIPV6","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '8,"Non-IP","TestAPNNONIP"')
            check_cgdcont(test, 'write', 'CME ERROR', '7,"Non-IP","TestAPNNONIP"')
            check_cgdcont(test, 'write', 'OK', '4,"IP","TestAPNIP"')
            check_cgdcont(test, 'write', 'CME ERROR', '3,"IP","TestAPNIP"')
            check_cgdcont(test, 'write', 'OK', '1,"IP","{}"'.format(test.dut.sim.apn_v4))
        else:
            check_cgdcont(test, 'write', 'OK', '16,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '15,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '14,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '13,"IPV4V6","TestAPN","0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '12,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '11,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '10,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '9,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0"')
            check_cgdcont(test, 'write', 'OK', '8,"PPP","TestAPNPPP"')
            check_cgdcont(test, 'write', 'OK', '7,"PPP","TestAPNPPP"')
            check_cgdcont(test, 'write', 'OK', '6,"PPP","TestAPNPPP"')
            check_cgdcont(test, 'write', 'OK', '5,"PPP","TestAPNPPP"')
            check_cgdcont(test, 'write', 'OK', '4,"IP","TestAPNIP"')
            check_cgdcont(test, 'write', 'OK', '3,"IP","TestAPNIP"')
            check_cgdcont(test, 'write', 'OK', '2,"IP","TestAPNIP"')
            check_cgdcont(test, 'write', 'OK', '1,"IP","{}"'.format(test.dut.sim.apn_v4))
    else:
        if test.dut.project == "SERVAL":
            check_cgdcont(test, 'read', 'OK', f'[+]CGDCONT: 1,"IP","{test.dut.sim.apn_v4}","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 4,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 8,"Non-IP","TestAPNNONIP".*'
                                              '[+]CGDCONT: 12,"IPV6","TestAPNIPV6","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 16,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*')

        else:
            check_cgdcont(test, 'read', 'OK', f'[+]CGDCONT: 1,"IP","{test.dut.sim.apn_v4}","0.0.0.0",0,0.*'
                                              '[+]CGDCONT: 2,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 3,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 4,"IP","TestAPNIP".*'
                                              '[+]CGDCONT: 5,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 6,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 7,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 8,"PPP","TestAPNPPP".*'
                                              '[+]CGDCONT: 9,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 10,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 11,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 12,"IPV6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 13,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 14,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 15,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*'
                                              '[+]CGDCONT: 16,"IPV4V6","TestAPN","0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0".*')














if "__main__" == __name__:
    unicorn.main()
