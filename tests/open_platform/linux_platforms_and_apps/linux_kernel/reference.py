# responsible: thomas.hinze@thalesgroup.com
# location: Berlin

'''Compare the Linux kernel .config file with a reference file.

    The intention of this test case is to find changes in the Linux
    kernel configuration introduced by the supplier on new SW deliveries.

    If the supplier changes the kernel config with a SW delivery then these
    differences shall be found by this test.

    This test will compare the resulting kernel config file from the build
    with reference kernel config file. The reference file shall be verified 
    and updated  by developers on kernel config changes introduced due to 
    feature implementions.

Testcase parameter:
    --kconfig-artifact
        the path to the kernel .config artifact from FW build

    --kconfig-reference
        the path to the kernel .config reference file
'''

import os

import unicorn
from core.basetest import BaseTest

class TestCompareLinuxKernelConfigWithReferenceFile(BaseTest):

    def setup(test):
        pass

    def run(test):
        test.log.info(f'kconfig_reference={test.kconfig_reference}')
        test.log.info(f'kconfig_artifact={test.path_to_sdk}/debug/.config')
        
        #test.log.step("Open the artifact & reference files and read them line wise")
        kconfig_reference = open(test.kconfig_reference, 'r').readlines()
        kconfig_artifact = open(f'{test.path_to_sdk}/debug/.config', 'r').readlines()

        #test.log.step("Check for config settings that are missing in the kernel config")
        missing_cfgs = set(kconfig_reference).difference(kconfig_artifact)
        test.expect(not missing_cfgs)
        for line in missing_cfgs:
            line = line.rstrip() # remove any EOL and trailing white space characters
            test.log.error(f"missing config: {line}")

        #test.log.step("Check for config settings that are unexpected in the kernel config")
        unexpected_cfgs = set(kconfig_artifact).difference(kconfig_reference)
        test.expect(not unexpected_cfgs)
        for line in unexpected_cfgs:
            line = line.rstrip() # remove any EOL and trailing white space characters
            test.log.error(f"unexpected config: {line}")

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
