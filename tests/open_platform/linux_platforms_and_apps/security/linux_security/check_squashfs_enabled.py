# responsible: marek.mlodzianowski@globallogic.com
# location: Wroclaw
# TC0000001.001

import unicorn
from core.basetest import BaseTest


class Test(BaseTest):
    def setup(test):
        pass


    def run(test):
        #list of squashfs partitions needs to be determined
        squashfs_partitions = ["/dev/dm-0 on /"]
        mount = test.dut.adb.send_and_receive("mount").splitlines()
        if check_squashfs_partitions(mount, squashfs_partitions) == len(squashfs_partitions):
            test.expect(True)
        pass


    def cleanup(test):
        pass


def check_squashfs_partitions(response, list_of_partitions):
    result = 0
    for line in response:
        for partition in list_of_partitions:
            if partition in line and "squashfs" in line:
                result = result + 1
    return result

