#responsible: baris.kildi@thalesgroup.com
#location: Berlin

import unicorn
import os
import subprocess
from dstl.auxiliary import tracing
from dstl.auxiliary import init
from core.basetest import BaseTest

class Test(BaseTest):
    """ To enable the plugin open enabled.cfg file and write into all needed plugin names
    like webimacs, junit, ...
    """

    def setup(test):
        test.dut.tracing_init()
        pass

    def run(test):
        test.dut.tracing_start()

        test.expect(test.dut.at1.send_and_verify('at', '.*\sOK\s.*', timeout=10))
        vari = test.local_config_path
        test.log.info(vari)

        test.dut.tracing_stop()
    def cleanup(test):
         pass


if "__main__" == __name__:
    unicorn.main()
