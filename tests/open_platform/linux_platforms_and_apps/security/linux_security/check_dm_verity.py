# responsible: marek.mlodzianowski@globallogic.com
# location: Wroclaw
# TC0000001.001

import unicorn
from core.basetest import BaseTest


class Test(BaseTest):
    def setup(test):
        pass


    def run(test):
        #list of devices needs to be determined
        verity = test.dut.adb.send_and_receive("veritysetup status /dev/mapper/nvme0n1p3_crypt")
        test.expect(check_dm_verity_f(verity))
        pass


    def cleanup(test):
        pass


def check_dm_verity_f(response):
    if "status:      verified" in response:
        return True
    else:
        return False

