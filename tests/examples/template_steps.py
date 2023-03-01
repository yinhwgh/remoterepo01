# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 template_steps

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):
        pass

    def run(test):

        """Send the command and then start waiting for specific URC
        """
        from dstl.auxiliary.init import dstl_detect
        from dstl.template import dstl_restart_template

        test.log.step("Detecting dut and remote versions")
        dstl_detect(test.r1)
        dstl_restart_template(test.r1)

        test.log.step("Running thread which pings google.com server")
        t = test.thread(test.os.execute, "ping google.com")
        t.join()

        test.log.info(test.dut)

        test.log.step("Rebooting module and checking read buffer")
        dstl_restart_template(test.r1)
        test.expect(test.dut.at1.send_and_verify("at+cfun?", ".*CFUN: 1.*OK.*"))
        test.log.info("Last response: \n\n{}\n\n".format(test.dut.at1.last_response))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

