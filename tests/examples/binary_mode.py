# responsible: tomasz.witka@globallogic.com
# location: Wroclaw
# TC0000001.001 binary_mode

#!/usr/bin/env unicorn
"""Unicorn tests.template.py module

This file represents Unicorn test template, that should be the base for every new test. Test can be executed with
unicorn.py and test file as parameter, but also can be run as executable script as well. Code defines only what is
necessary while creating new test. Examples of usage can be found in comments. For more details please refer to
basetest.py documentation.

"""

import unicorn
import re
import os
from core.basetest import BaseTest

import dstl.auxiliary.restart_module

from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):

    def setup(test):
        test.script__file_handle = -1
        test.script__tmp_folder = "/tmp/"
        test.script__test_file_name = "test.txt"
        test.script__host_file = "./test.txt"

        test.expect(test.dut.dstl_restart())

        test.expect(test.dut.at1.enable_tracing("traces.log"))

        # Create temporary directory
        test.expect(test.dut.at1.send_and_verify("at^sfsa=\"mkdir\",{}".format(test.script__tmp_folder), "OK"),
                    critical=False)
        test.dut.detect()

        pass

    def run(test):

        # Open and create file if not exist
        test.expect(
            test.dut.at1.send_and_verify(
                "at^sfsa=\"open\",{}{},9".format(test.script__tmp_folder, test.script__test_file_name), "OK")
            , critical=True
        )

        # Parse URC
        match = re.search(r"\^SFSA: (\d+), (\d+)", test.dut.at1.last_response)
        if match:
            test.script__file_handle = match.group(1)
            status = match.group(2)

            # Write file if status OK
            if status == "0":
                test.expect(
                    test.dut.at1.send_and_verify(
                        "at^sfsa=\"write\",{},{}".format(
                            test.script__file_handle, os.path.getsize(test.script__host_file))
                        , wait_for="CONNECT"))
            test.expect(test.dut.at1.send_file(test.script__host_file))
            test.expect(test.dut.at1.wait_for("OK"))


        # Reading binary data
        data = test.dut.at1.send_and_read_binary("at")
        test.log.info("DATA: {}".format(data))

        # Waiting for bytes sequence
        test.dut.at1.buffer.flush()
        test.dut.at1.send("at")
        test.expect(test.dut.at1.wait_for_bytes(b"OK"))

    def cleanup(test):

        test.expect(test.dut.at1.send_and_verify(
            "at^sfsa=\"close\",{}".format(test.script__file_handle), "OK"))

        test.expect(test.dut.at1.send_and_verify(
            "at^sfsa=\"stat\",{}{}".format(test.script__tmp_folder, test.script__test_file_name)))

        test.expect(test.dut.at1.send_and_verify(
                "at^sfsa=\"remove\",{}{}".format(test.script__tmp_folder, test.script__test_file_name), "OK"))

        test.expect(test.dut.at1.send_and_verify("at^sfsa=\"rmdir\",{}".format(test.script__tmp_folder), "OK"))

        test.expect(test.dut.at1.disable_tracing())


if "__main__" == __name__:
    unicorn.main()
