# responsible: thomas.hinze@thalesgroup.com
# location: Berlin

'''Check if a kernel config fragment was applied to  the Linux kernel

    The intention of this test case is to ensure that the required
    Linux kernel fragment config files were applied to the Linux kernel 
    config during the FW build.

    If a fragment file is disabled by accident then this test shall find
    such issue. 

    This test will check if the resulting kernel config file from the build
    contains all kernel settings that shall be applied by the fragment config 
    file. The list of fragament files that have to be applied shall be 
    extended by developers when kernel settings were changed due to feature 
    implementions.

Testcase parameter:
    --kconfig-artifact
        the path to the kernel .config artifact from FW build

    --kconfig-fragment
        the name of the kernel .config fragment file
    
    --kconfig-fragment-dir
        the directory containing the fragment file
'''

import os

import unicorn
from core.basetest import BaseTest

class TestCheckLinuxKernelConfigIfFragmentWasApplied(BaseTest):

    def setup(test):
        #self.testname += f".{self.kconfig_fragment}"
        pass

    def run(test):
        test.log.info(f'kconfig_fragment={test.kconfig_fragment}')
        test.log.info(f'kconfig_artifact={test.path_to_sdk}/debug/.config')
        test.log.info(f'kconfig_fragment_dir={test.kconfig_fragment_dir}')

        kconfig_fragment_file = f'{test.kconfig_fragment_dir}/{test.kconfig_fragment}'
        
        #test.log.step("Open the artifact & fragment files and read them line wise")
        kconfig_fragment = open(kconfig_fragment_file, 'r').readlines()
        kconfig_artifact = open(f'{test.path_to_sdk}/debug/.config', 'r').readlines()

        #test.log.step("Check for config settings that are missing in the kernel config")
        missing_cfgs = set(kconfig_fragment).difference(kconfig_artifact)
        test.expect(not missing_cfgs)
        for line in missing_cfgs:
                line = line.rstrip()
                if line:
                    test.log.error(f"missing config: {line}")
                    #test.fail(f"missing: {line}")

        #test.log.step("Get config settings that are included in the kernel config")
        # ... might be skipped - only more verbose in system out
        same = set(kconfig_fragment).intersection(kconfig_artifact)
        for line in same:
                line = line.rstrip()
                if line:
                        test.log.info(f'found config: {line}')

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
