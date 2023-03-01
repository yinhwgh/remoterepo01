# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0094409.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.devboard import devboard
from dstl.auxiliary.restart_module import dstl_restart
from dstl.miscellaneous import read_write_nv_block


class Test(BaseTest):
    """
    TC0094409.001 - TpSbnwSbnrNvBasic
    """

    def setup(test):
        test.dut.dstl_detect()
        # test.block_number = test.dut.dstl_get_nv_test_block_number()

    def run(test):
        test.log.h1("****** check SBNR and SBNW for writing and reading of the factory test block. ******")
        data_length = 100
        data_0x01 = '0x01 ' * data_length
        data_0x00 = '0x00 ' * data_length
        # if product's NV supports BLOCK_INDEX, BLOCK_VERSION, the parameters need be set to value
        block_index = 0
        block_version = 1

        # read_dict = test.dut.dstl_read_data_from_nv_block(read_length=data_length)
        test.log.step("1. Write a special pattern into this block (named as block_0x01)")

        write_dict = test.dut.dstl_write_data_to_nv_block(block_index=block_index,
                                                          block_size=data_length,
                                                          block_version=block_version,
                                                          data_bytes=data_0x01)
        test.expect(write_dict, msg="Failed to write data to NV.")

        test.log.step("2. Read this block (verify data) - 0x01.")
        read_dict = test.dut.dstl_read_data_from_nv_block(read_length=data_length)
        test.check_block_data(write_dict, read_dict)

        test.log.step("3. Restart module and read this block (verify data).")
        test.dut.dstl_restart()
        read_dict = test.dut.dstl_read_data_from_nv_block(read_length=data_length)
        test.check_block_data(write_dict, read_dict)

        test.log.step("4. Write again this block with cleared data (all zero - names as block_0x00)")
        write_dict = test.dut.dstl_write_data_to_nv_block(block_index=block_index,
                                                          block_size=data_length,
                                                          block_version=block_version,
                                                          data_bytes=data_0x00)
        test.expect(write_dict, msg="Failed to write data to NV.")

        test.log.step("5. Read this block (verify data) - 0x00.")
        read_dict = test.dut.dstl_read_data_from_nv_block(read_length=data_length)
        test.check_block_data(write_dict, read_dict)

        test.log.step("6. Restart module and read this block (verify data - 0x00).")
        test.dut.dstl_restart()
        read_dict = test.dut.dstl_read_data_from_nv_block(read_length=data_length)
        test.check_block_data(write_dict, read_dict)

    def cleanup(test):
        test.log.info("Checking whether module is in ATC mode.")
        if not test.dut.at1.send_and_verify("AT", handle_errors=True, timeout=5):
            test.log.info("Module may not in ATC mode, reset with MC test board.")
            test.dut.dstl_reset_with_vbatt_via_dev_board()

    def check_block_data(test, write_dict, read_dict):
        # These keys may not be supported by all modules
        optional_keys = ['block_version', 'block_index']
        for k, write_data in write_dict.items():
            test.log.info(f"Checking data of {k}.")
            if k not in optional_keys or (k in optional_keys and read_dict[k] is not None):
                test.log.info(f"Write data: {write_data}")
                test.log.info(f"Read data: {read_dict[k]}")
                if not test.expect(read_dict[k] == write_data):
                    test.log.error(f"Read {k} from NV does not equal to written one.")
            else:
                test.log.info(f"Skip checking {k} for {test.dut.product}.")


if "__main__" == __name__:
    unicorn.main()
