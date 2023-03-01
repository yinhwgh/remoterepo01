# responsible: thomas.hinze@thalesgroup.com
# location: Berlin

'''Check if specific settings were applied to  the Linux kernel

    The intention of this test case is to ensure that the settings
    requested by the customer were applied.

Testcase parameter:
    --kconfig-artifact
        the path to the kernel .config artifact from FW build

    --kconfig-settings
        the name of the kernel .config settings file to be checked
    
    --kconfig-settings-dir
        the directory containing the settings file
'''

import os

import unicorn
from core.basetest import BaseTest

class TestCheckLinuxKernelConfigForSpecificSettings(BaseTest):

    def setup(test):
        #self.testname += f".{self.kconfig_fragment}"
        pass

    def run(test):
        test.log.info(f'kconfig_settings={test.kconfig_settings}')
        test.log.info(f'kconfig_artifact={test.path_to_sdk}/debug/.config')

        # the test files should be place in the same directory as the test case
        #testfile_dir = os.path.dirname(__file__)
        #kconfig_settings_file = f'{test.kconfig_settings}'
        
        #test.log.step("Open the artifact & settings files and read them line wise")
        kconfig_settings = open(test.kconfig_settings, 'r').readlines()
        kconfig_artifact = open(f'{test.path_to_sdk}/debug/.config', 'r').readlines()

        #test.log.step("Check for config settings that are missing in the kernel config")
        missing_cfgs = set(kconfig_settings).difference(kconfig_artifact)
        test.expect(not missing_cfgs)
        for line in missing_cfgs:
                line = line.rstrip()
                if line:
                    test.log.error(f"missing config: {line}")
                    #test.fail(f"missing: {line}")

        #test.log.step("Get config settings that are included in the kernel config")
        # ... might be skipped - only more verbose in system out
        same = set(kconfig_settings).intersection(kconfig_artifact)
        for line in same:
                line = line.rstrip()
                if line:
                        test.log.info(f'found config: {line}')

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()
