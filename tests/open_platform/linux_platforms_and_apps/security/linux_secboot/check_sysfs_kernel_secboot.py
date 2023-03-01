# responsible: thomas.hinze@thalesgroup.com
# location: Berlin

import os

from core.basetest import BaseTest

class Test(BaseTest):

    def setup(test):
        test.dut.adb.send_and_receive("uptime")
        test.dut.adb.send_and_receive("uci -c /vendor show")

        test.expected_files = ['auth_en', 'debug_en', 'debug_id', 'pk_hash0']

    def check_fs_uid(test, filename, uid):
        test.dut.adb.send_and_receive(f"stat -c '%u' {filename}")
        if not test.dut.adb.last_retcode == 0:
            test.log.error(f"cannot get user for: {filename}")
            return

        uid_dut = int(test.dut.adb.last_response.split()[0])
        if not test.expect(test.check(uid_dut == uid)):
            test.log.error(f"Wrong uid for: {filename} - uid_dut={uid_dut} uid_exp={uid}")

    def check_fs_gid(test, filename, gid):
        test.dut.adb.send_and_receive(f"stat -c '%g' {filename}")
        if not test.dut.adb.last_retcode == 0:
            test.log.error(f"cannot get group for: {filename}")
            return

        gid_dut = int(test.dut.adb.last_response.split()[0])
        if not test.expect(gid_dut == gid):
            test.log.error(f"Wrong uid for: {filename} - gid_dut={gid_dut} gid_exp={gid}")

    def check_fs_perm(test, filename, perm):
        test.dut.adb.send_and_receive(f"stat -c '%a' {filename}")
        if not test.dut.adb.last_retcode == 0:
            test.log.error(f"cannot get permissions for: {filename}")
            return
        
        perm_dut = test.dut.adb.last_response.split()[0]
        if not test.expect(perm_dut == perm):
            test.log.error(f"Wrong permissions for: {filename} - perm_dut={perm_dut} perm_exp={perm}")

    def run(test):
        sysfs_secboot_dir = "/sys/kernel/secboot"

        test.log.info("Check for secboot sysfs dir in the system")
        test.dut.adb.send_and_receive(f"test -d {sysfs_secboot_dir}")
        if not test.expect(test.dut.adb.last_retcode == 0):
            test.abort("missing secboot sysfs dir")
            return
        
        test.log.info(f"Check owner and group: {sysfs_secboot_dir}")
        test.check_fs_uid(sysfs_secboot_dir, uid=0)
        test.check_fs_gid(sysfs_secboot_dir, gid=0)

        test.log.info(f"Check permissions: {sysfs_secboot_dir}")
        test.check_fs_perm(sysfs_secboot_dir, perm="555")
    
        test.log.info("Get content of secboot sysfs dir")
        test.dut.adb.send_and_receive(f"ls {sysfs_secboot_dir}")
        if not test.expect(test.dut.adb.last_retcode == 0):
            test.abort("cannot read secboot sysfs dir")
            return

        dut_files = test.dut.adb.last_response.split()
        test.log.info(f"dut_files={dut_files}")

        for expected_file in test.expected_files:
            file_path = sysfs_secboot_dir + "/" + expected_file

            test.log.info(f"Check for file: {expected_file}")
            test.expect(test.check(expected_file in dut_files))

            test.log.info(f"Check owner and group: {expected_file}")
            test.check_fs_uid(file_path, uid=0)
            test.check_fs_gid(file_path, gid=0)
            
            test.log.info(f"Check permissions: {expected_file}")
            test.check_fs_perm(file_path, perm="444")

            test.log.info(f"Check read on file: {expected_file}")
            test.dut.adb.send_and_receive(f"cat {file_path} && echo")
            test.expect(test.dut.adb.last_retcode == 0)

        test.log.info("Check for unexpected files in secboot sysfs dir")
        for dut_file in dut_files:
            if not test.expect(test.check(dut_file in test.expected_files)):
                test.log.error(f"Found for unexpected file: {dut_file}")

    def check(test, condition):
        return condition

    def cleanup(test):
        pass
