#responsible: yunhui.zhang@thalesgroup.com
#location: Beijing
#TC0103989.001 - TpCrsmErrorCheck

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.configuration import functionality_modes
from dstl.security import lock_unlock_sim
from dstl.network_service import register_to_network

class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_lock_sim()
        return


    def run(test):
        test.log.info('***Test start***')
        test.log.step('1.Check test and write command in airplane mode.')
        test.expect(test.dut.dstl_set_airplane_mode())
        test.expect(test.dut.at1.send_and_verify('at+crsm=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=242', '.*\+CRSM: 144,0,"62.*OK'))
        test.expect(test.dut.dstl_set_full_functionality_mode())

        test.log.step('2.Check test and write command when removing SIM card')
        test.dut.dstl_remove_sim()
        test.sleep(2)
        test.expect(test.dut.at1.send_and_verify('at+crsm=?', 'OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=242', '.*\+CME ERROR: SIM not inserted'))
        test.dut.dstl_insert_sim()
        test.sleep(5)

        test.log.step('3.Check read and write record file command when the file type is binary')
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,12258,0,0,10', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=220,12258,0,0,10,"98681108214365872104"', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))

        test.log.step('4.Check read and write binary file command when the file type is record')
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28476,1,4,176', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=214,28476,1,4,176,"00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))

        test.log.step('5.Check read and write binary or record file command when the file type is cyclic')
        test.expect(test.dut.at1.send_and_verify('at+crsm=176,28473,0,0,3', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=178,28473,0,0,3', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=220,28473,0,0,3,"FFFFFF"', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))
        test.expect(test.dut.at1.send_and_verify('at+crsm=214,28473,0,0,3,"FFFFFF"', '.*\+CRSM: \d{1,3},\d{1,3},"".*OK'))

        test.log.step('6.Check to set the fileid is not 0 and set the pathid')
        if(test.dut.project == 'VIPER'):
            test.expect(test.dut.at1.send_and_verify('at+crsm=176,1,0,0,10,,"3F002FE2"', '.*OK*.'))  # according to IPIS100334922
        else:
            test.expect(test.dut.at1.send_and_verify('at+crsm=176,1,0,0,10,,"3F002FE2"', '.*\+CME ERROR*.'))
        test.log.info('***Test end***')

    def cleanup(test):
        test.dut.dstl_lock_sim()
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK*."))


if (__name__ == "__main__"):
    unicorn.main()
