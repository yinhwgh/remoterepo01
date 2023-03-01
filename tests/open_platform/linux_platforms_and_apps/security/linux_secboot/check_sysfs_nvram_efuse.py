# responsible: thomas.hinze@thalesgroup.com
# location: Berlin

import os

from core.basetest import BaseTest

class Test(BaseTest):

    def setup(test):
        test.dut.adb.send_and_receive("uptime")
        test.dut.adb.send_and_receive("uci -c /vendor show")
        pass

    def run(test):
        sysfs_efuse_nvmem_file = "/sys/devices/platform/11ec0000.efuse/mtk-devinfo0/nvmem"
        local_efuse_nvmem_file = "sysfs_efuse_nvmem.dat"

        test.log.info("Check for e-fuese nvmem data file in the system")
        test.dut.adb.send_and_receive(f"ls {sysfs_efuse_nvmem_file}")
        test.expect(test.dut.adb.last_retcode == 0)

        test.log.info("Get e-fuse nvmem data from the system")
        test.dut.adb.pull(sysfs_efuse_nvmem_file, local_efuse_nvmem_file)
        test.expect(test.dut.adb.last_retcode == 0)

        # orignal size with RC1 delivery was 800 byte
        # size increased by 344 byte to 1144 byte after aplying patch from AUTO00128437
        #   -> 86 new values were added each with a size of 4 byte => +344 byte
        #   -> patch will be integrated in RC2 delivery
        #   -> GA delivery added another 4 bytes, new size 1148
        expected_size = 1148
        test.log.info("Get size of e-fuse nvmem data")
        data_size = os.path.getsize(local_efuse_nvmem_file)
        test.log.info( f"Check size of e-fuse nvmem data: size={data_size} expected={expected_size}" )
        test.expect(data_size == expected_size)

        # TODO: read the file and check some specific values
        #with open(local_efuse_nvmem_file, 'rb') as data_file:
            #data = data_file.read()
            #data_file.close()

    def cleanup(test):
        pass
