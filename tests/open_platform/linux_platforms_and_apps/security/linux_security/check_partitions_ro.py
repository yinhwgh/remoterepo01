# responsible: marek.mlodzianowski@globallogic.com
# location: Wroclaw
# TC0000001.001

import unicorn
from core.basetest import BaseTest


class Test(BaseTest):
    def setup(test):
        pass


    def run(test):
        #list of read only partitions needs to be determined
        ro_partitions = ["/dev/dm-0 on /", "tmpfs on /sys/fs/cgroup", "tmpfs on /etc/machine-id"]
        mount = test.dut.adb.send_and_receive("mount").splitlines()
        if check_ro_partitions(mount, ro_partitions) == len(ro_partitions):
            test.expect(True)
        pass


    def cleanup(test):
        pass


def check_ro_partitions(response, list_of_partitions):
    result = 0
    for line in response:
        for partition in list_of_partitions:
            if partition in line and "(ro," in line:
                result = result + 1
    return result

