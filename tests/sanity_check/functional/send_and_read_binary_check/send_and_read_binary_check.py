#responsible: johann.suhr@thalesgroup.com
#location: Berlin

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary import init
from dstl.security import lock_unlock_sim

import os


class Test(BaseTest):
    """ Test send_and_read_binary() method. See IPIS100311133."""

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        bytes_read = 0
        packet_size = 9
        size = 500

        bytes_to_be_read = size
        remaining_size = bytes_to_be_read

        bin_file = os.path.join(os.path.dirname(__file__), "file.bin")
        with open(bin_file, "wb") as file:
            while remaining_size > 0:
                read_size = min(packet_size, remaining_size)

                data = test.dut.at1.send_and_read_binary('at', size=read_size)

                bytes_read += read_size
                remaining_size = bytes_to_be_read - bytes_read
                file.write(data)

        file_size = os.path.getsize(bin_file)
        test.expect(file_size == size)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
