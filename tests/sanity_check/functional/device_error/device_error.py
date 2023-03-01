import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network



class Test(BaseTest):
    """IPIS100332041
    """

    def setup(test):
        test.dut.dstl_detect()
        #test.dut.dstl_restart()

    def run(test):
        test.dut.dstl_restart()
        test.expect(test.dut.at1.send_and_verify("at", "OK", timeout=30))
        test.expect(test.dut.at2.send_and_verify("ati", "OK", timeout=30))

        test.dut.dstl_restart()
        test.sleep(10)
        test.expect(test.dut.at1.send_and_verify("at+creg?", "OK", timeout=30))
        test.expect(test.dut.at2.send_and_verify("at^smoni", "OK", timeout=30))

        #testfilePath = test.test_files_path
        #print("tfPath:", testfilePath)


    def cleanup(test):
        pass



if "__main__" == __name__:
    unicorn.main()

