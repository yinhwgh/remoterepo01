# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_os

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
        """Run simple system command
        """
        test.os.execute("ping google.com")

        """Run three system commands simultaneously
        """
        t1 = test.thread(test.os.execute, "ping google.com")
        t2 = test.thread(test.os.execute, "ping youtube.com")
        t3 = test.thread(test.os.execute, "ping wikipedia.org")
        t1.join()
        t2.join()
        t3.join()

    def cleanup(test):
        pass
