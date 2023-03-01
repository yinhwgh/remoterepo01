# author: jingxin.shen@thalesgroup.com
# location: Beijing
# TC0088319.002

import unicorn
import re

from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.packet_domain.pdp_context_operation import *
from dstl.security.lock_unlock_sim import dstl_lock_sim

new_cgdcont_1 = '1,"IP","internet","10.185.80.69",1,1,0,1,1,1'
new_cgdcont_2 = '1,"IP","internet","0.0.0.0",2,4,0,1,2,0'
new_cgdscont_1 = '4,1,1,1'
new_cgdscont_2 = '4,1,2,4'
new_cgeqos_1 = '1,1,1,1,1,1'
new_cgeqos_2 = '1,0,2,2,2,2'

new_cgtft_1 = '1,1,1,"255.255.255.255.255.192.0.0"'
new_cgtft_2 = '1,1,10,"8.8.8.8.255.255.255.255"'


class Test(BaseTest):
    """
    Intention:
    Checks persistance of Contexts.
    """
    contexts = []

    def setup(test):
        dstl_detect(test.dut)
        dstl_lock_sim(test.dut)
        test.contexts = dstl_backup_pdp_context(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2", "OK", timeout=60))
        dstl_clear_contexts(test.dut)
        pass

    def run(test):
        test.log.step('1.1 Define parameters of +CGDCONT')
        test.log.step('1.2 Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)')
        test.set_pdp_context_and_check('CGDCONT', new_cgdcont_1)
        test.set_pdp_context_and_check('CGDCONT', new_cgdcont_2)
        test.log.step('2.1 Define parameters of +CGDSCONT')
        test.log.step('2.2 Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)')
        test.set_pdp_context_and_check('CGDSCONT', new_cgdscont_1)
        test.set_pdp_context_and_check('CGDSCONT', new_cgdscont_2)
        test.log.step('3.1 Define parameters of +CGEQOS')
        test.log.step('3.2 Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)')
        test.set_pdp_context_and_check('CGEQOS', new_cgeqos_1)
        test.set_pdp_context_and_check('CGEQOS', new_cgeqos_2)

        test.log.step('4.1 Define parameters of +CGTFT')
        test.log.step('4.2 Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)')
        test.set_pdp_context_and_check('CGTFT', new_cgtft_1)
        test.set_pdp_context_and_check('CGTFT', new_cgtft_2)
        test.log.step('5.1 Define parameters of +CGAUTH')
        test.log.step('5.2 Check if parameters are persistent (non-volatile and independent from AT&F, AT&W, ATZ)')
        if test.dut.project == 'VIPER':
            test.log.warning('Viper does not support CGAUTH')
        else:
            test.log.error('Should implement CGAUTH part for this project')
        pass

    def cleanup(test):
        dstl_clear_contexts(test.dut)
        for line in test.contexts:
            test.expect(test.dut.at1.send_and_verify("AT+CGDCONT={}".format(line), ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))
        pass

    def set_pdp_context_and_check(test, command, new_value):
        test.expect(test.dut.at1.send_and_verify('AT+{}={}'.format(command, new_value), expect='OK'))
        if test.dut.platform == "QCT" and command == 'CGTFT':
            t = re.search(r'(\d+,\d+,\d+,"\d+.\d+.\d+.\d+).\d+.\d+.\d+.\d+"', new_value)
            new_value = t.group(1) + '.\d+.\d+.\d+.\d+"'
        test.expect(
            test.dut.at1.send_and_verify('AT+{}?'.format(command), expect='\+{}:\s+{}.*OK'.format(command, new_value)))
        dstl_restart(test.dut)
        if test.dut.project is 'VIPER':
            test.sleep(9)  # waiting for SIM and prov configuration

        test.expect(
            test.dut.at1.send_and_verify('AT+{}?'.format(command), expect='\+{}:\s+{}.*OK'.format(command, new_value)))
        test.expect(dstl_enter_pin(test.dut))
        test.attempt(test.dut.at1.send_and_verify, 'ATZ', expect='OK', retry=6,
                     sleep=1)  # for Viper only SIM BUSY instead!
        test.expect(
            test.dut.at1.send_and_verify('AT+{}?'.format(command), expect='\+{}:\s+{}.*OK'.format(command, new_value)))
        test.expect(test.dut.at1.send_and_verify('AT&W', expect='OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT+{}?'.format(command), expect='\+{}:\s+{}.*OK'.format(command, new_value)))
        test.expect(test.dut.at1.send_and_verify('AT&F', expect='OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT+{}?'.format(command), expect='\+{}:\s+{}.*OK'.format(command, new_value)))
        return True


if '__main__' == __name__:
    unicorn.main()
