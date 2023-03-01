#responsible: xiaoyu.chen@thalesgroup.com
#location: Dalian
#TC0091924.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init

class ReadBootloaderVersion (BaseTest):
    '''
      TC0091924.001 - ReadBootloaderVersion
    '''
    def setup(test):

        test.dut.dstl_detect()

    def run(test):
        test.expect(test.compare_result())

    def cleanup(test):
        pass
    def compare_result(test):
        test.dut.at1.send_and_verify("ATI51", ".*OK.*")
        res_1=test.dut.at1.last_response.split('\n')[1:]
        if test.dut.at1.send_and_verify('AT^SOS="bootloader/info"', ".*OK.*"):
            res_2 = test.dut.at1.last_response.split('\n')[1:]
            for i in range(2):
                if res_1[i].strip().lower()==res_2[i].strip().lower():
                    test.log.info('compare passed in line {}'.format(i))
                else:
                    test.log.error('compare failed in line {}'.format(i))
                    return False
        else:
            test.log.warning('Product not support at^sos="bootloader/info",skip compare')
            return True
        return True

if "__main__" == __name__:
    unicorn.main()
