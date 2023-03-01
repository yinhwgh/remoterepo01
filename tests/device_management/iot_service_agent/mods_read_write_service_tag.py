#responsible: xueping.zhang@thalesgroup.com
#location: Beijing
#TC

import random

import unicorn
from core.basetest import BaseTest
from dstl.internet_service import set_get_mods_client_service_tag


class Lwm2mStatusControl(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.info("1. Set and read the min value for service tags... ")
        print(test.dut.dstl_set_fwdownload_deferlimit("0"))
        test.expect(test.dut.dstl_set_fwdownload_deferlimit("0"))
        test.expect(test.dut.dstl_get_fwdownload_deferlimit() == "0")
        test.expect(test.dut.dstl_set_fwupdate_deferlimit("0"))
        test.expect(test.dut.dstl_get_fwupdate_deferlimit() == "0")

        test.log.info("2. Set and read the max value for service tags... ")
        test.expect(test.dut.dstl_set_fwdownload_deferlimit("255"))
        test.expect(test.dut.dstl_get_fwdownload_deferlimit() == "255")
        test.expect(test.dut.dstl_set_fwupdate_deferlimit("255"))
        test.expect(test.dut.dstl_get_fwupdate_deferlimit() == "255")

        test.log.info("3. Set and read random values for service tags.")

        for i in range(10):
            value = random.randint(0, 255)
            test.expect(test.dut.dstl_set_fwdownload_deferlimit(str(value)))
            test.expect(test.dut.dstl_get_fwdownload_deferlimit() == str(value))
            test.expect(test.dut.dstl_set_fwupdate_deferlimit(str(value)))
            test.expect(test.dut.dstl_get_fwupdate_deferlimit() == str(value))

    def cleanup(test):
        test.log.info("4. Restore default value for service tags... ")
        test.expect(test.dut.dstl_set_fwdownload_deferlimit("0"))
        test.expect(test.dut.dstl_get_fwdownload_deferlimit() == "0")
        test.expect(test.dut.dstl_set_fwupdate_deferlimit("0"))
        test.expect(test.dut.dstl_get_fwupdate_deferlimit() == "0")


if __name__ == "__main__":
    unicorn.main()
