#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0094198.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
import re

class Test(BaseTest):

    def setup(test):

        test.dut.detect()

    def run(test):
        dtr_current='AT^SCFG="MEopMode/ExpectDTR","current"'
        dtr_powerup='AT^SCFG="MEopMode/ExpectDTR","powerup"'

        test.log.step('1.Send AT^SCFG=? command to check for subcommand "MEopMode/ExpectDTR"'
                      'which ports are available.')
        atc = test.prepare_all_ports_atc()
        p_list = test.get_available_ports(atc)
        test.log.info(f'Available port list:{p_list}')

        test.log.step('2.Set AT^SCFG="MEopMode/ExpectDTR","current","acm1","acm2","acm3",'
                      '"acm4","rmnet0","rmnet1", and check if ports are correctly set.')
        test.expect(test.dut.at1.send_and_verify(f'{dtr_current},{atc}','OK'))
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"',f'"current",{atc}'))

        test.log.step('3.Set AT^SCFG="MEopMode/ExpectDTR","current" and check if '
                      'there is no port set.')
        test.dut.at1.send_and_verify(f'{dtr_current}','OK')
        test.expect('"current",' not in test.dut.at1.last_response)

        test.log.step('4.Set AT^SCFG="MEopMode/ExpectDTR","current" with each port separately'
                      'and check if ports are correctly set.')
        for port in p_list:
            test.expect(test.dut.at1.send_and_verify(f'{dtr_current},"{port}"', 'OK'))
            test.expect(
                test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"', f'"current","{port}"\s'))

        test.log.step('5.Set AT^SCFG="MEopMode/ExpectDTR","powerup","acm1","acm2","acm3",'
                      '"acm4","rmnet0","rmnet1",and check if ports are correctly set.')
        test.expect(test.dut.at1.send_and_verify(f'{dtr_powerup},{atc}', 'OK'))
        test.expect(
            test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"', f'"powerup",{atc}'))

        test.log.step('6.Restart Module and check if ports for "current" and "powerup" are correctly set.')
        test.dut.dstl_restart()
        test.expect(
            test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"', 'OK'))
        test.expect(f'"current",{atc}' in test.dut.at1.last_response)
        test.expect(f'"powerup",{atc}' in test.dut.at1.last_response)

        test.log.step('7.Set AT^SCFG="MEopMode/ExpectDTR","powerup" and check if there is no port set.')
        test.dut.at1.send_and_verify(f'{dtr_powerup}', 'OK')
        test.expect('"powerup",' not in test.dut.at1.last_response)
        test.log.step('8.Restart Module and check if ports for"current" and "powerup" are correctly set.')
        test.dut.dstl_restart()
        test.expect(
            test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"', 'OK'))
        test.expect('"current",' not in test.dut.at1.last_response)
        test.expect('"powerup",' not in test.dut.at1.last_response)

        test.log.step('9.Set AT^SCFG="MEopMode/ExpectDTR","powerup" with each port separately, '
                      'make restart and check if ports are correctly set.')
        for port in p_list:
            test.expect(test.dut.at1.send_and_verify(f'{dtr_powerup},"{port}"', 'OK'))
            test.dut.dstl_restart()
            test.expect(
                test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ExpectDTR"',
                                             f'"current","{port}"\s.*"powerup","{port}"\s'))

        test.log.step('10.Set AT^SCFG="MEopMode/ExpectDTR","powerup","acm1","acm2","acm3","acm4",'
                      '"rmnet0","rmnet1"  and restart module.')
        test.expect(test.dut.at1.send_and_verify(f'{dtr_powerup},{atc}', 'OK'))
        test.dut.dstl_restart()

    def cleanup(test):
        pass

    def get_available_ports(test,at_res):
        port_list=[]
        for p in at_res.split(','):
            port_list.append(p.strip('"'))
        return port_list

    def prepare_all_ports_atc(test):
        test.dut.at1.send_and_verify('at^scfg=?', 'OK')
        res = test.dut.at1.last_response
        pattern_1 = '"MEopMode/ExpectDTR",(.*),\((.*)\)'
        res_1 = re.search(pattern_1, res).group(2)
        return res_1


if "__main__" == __name__:
    unicorn.main()