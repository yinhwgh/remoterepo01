#responsible: jun.chen@thalesgroup.com
#location: Beijing
#SRV03-4328

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.write_json_result_file import *

class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        test.log.step("1. Send AT")
        test.expect(test.dut.at1.send_and_verify("AT", "OK"))

    def cleanup(test):
        test.dut.write_json_result_file(test.get('test_execution_key', default='no_test_execution_key'),
                                        test.get('test_key', default='no_test_key'), str(test.test_result), test.campaign_file,
                                        test.timer_start, test.test_file)
        test.log.com('***** Testcase: ' + test.test_file + ' (' + test.get('test_key',default='no_test_key') + ') - End *****')

if "__main__" == __name__:
    unicorn.main()
