#responsible: jingxin.shen@thalesgroup.com
#location: Beijing
#TC0093091.001

import unicorn

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service.register_to_network import  dstl_enter_pin

'''
Case name:
'''


class at_scfg_cregroam_basic(BaseTest):
    def setup(test):
        #        test.dut.dstl_restart()
        #        test.sleep(5)
        pass

    def run(test):
        test.log.info('---------Test Begin -------------------------------------------------------------')

        test.expect(test.dut.dstl_restart())
        '''
        iLoop=1:test in airplane mode
        iLoop=2:test in normal mode without pin
        iLoop=3:test in normal mode with pin
        '''
        for iLoop in range(1, 4):
            '''check response of at^scfg=?'''
            if iLoop == 1:
                test.expect(test.dut.at1.send_and_verify('at+cfun=4', 'OK',wait_for='^SYSSTART AIRPLANE MODE'))
            if iLoop == 2:
                test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: SIM PIN'))
            if iLoop == 3:
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: READY'))
            test.expect(test.dut.at1.send_and_verify('at^scfg=?', '^SCFG: "MEopMode/CregRoam",("0","1")'))

            '''set to 0'''
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam","0"', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","0"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","0"'))
            test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","0"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","0"'))
            test.expect(test.dut.dstl_restart())
            if iLoop == 1:
                test.expect(test.dut.at1.send_and_verify('at+cfun=4', 'OK',wait_for='^SYSSTART AIRPLANE MODE'))
            if iLoop == 2:
                test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: SIM PIN'))
            if iLoop == 3:
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: READY'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","0"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","0"'))

            '''set to 1'''
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam","1"', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","1"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","1"'))
            test.expect(test.dut.at1.send_and_verify('AT&F', 'OK'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","1"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","1"'))
            test.expect(test.dut.dstl_restart())
            if iLoop == 1:
                test.expect(test.dut.at1.send_and_verify('at+cfun=4', 'OK',wait_for='^SYSSTART AIRPLANE MODE'))
            if iLoop == 2:
                test.expect(test.dut.at1.send_and_verify('at+cfun=1', 'OK'))
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: SIM PIN'))
            if iLoop == 3:
                test.expect(test.dut.dstl_enter_pin())
                test.expect(test.dut.at1.send_and_verify('at+cpin?', '+CPIN: READY'))
            test.expect(test.dut.at1.send_and_verify('at^scfg?', '^SCFG: "MEopMode/CregRoam","1"'))
            test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam"', '^SCFG: "MEopMode/CregRoam","1"'))

            '''illegal parameters test'''
            illegal = ['"a"', '"-1"', '"2"', '"*"', '"+"', '"^"']
            for param in illegal:
                test.expect(
                    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CregRoam",' + param, '+CME ERROR: invalid index'))

        test.log.info('---------Test End -------------------------------------------------------------')
    def cleanup(test):
        pass


if (__name__ == "__main__"):
    unicorn.main()
