#responsible: christian.gosslar@thalesgroup.com
#location: Berlin
#LM0004975.003, LM0004975.004, LM0004985.003, LM0006213.001, LM0006590.001 - TC0093811.001
testcase_id = "LM0004975.003, LM0004975.004, LM0004985.003, LM0006213.001, LM0006590.001 - TC0093811.001"

import unicorn
from dstl.auxiliary import init
from core.basetest import BaseTest
from dstl.security.lock_unlock_sim import *
from dstl.auxiliary.restart_module import dstl_restart


from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.identification.get_part_number import dstl_check_or_read_part_number

default_provider_name =""

class provider_specific_images(BaseTest):

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com("***** " + testcase_id + " *****")
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        test.dut.dstl_collect_module_info()
        test.dut.dstl_check_or_read_part_number(onlyread=True)
        test.dut.devboard.send_and_verify("mc:asc0cfg=off",".*O.*")
        pass

    def run(test):

        vzw_provider_name = ""
        vzw_image_name = ""
        global default_provider_name

        if (test.dut.project == 'VIPER'):
            vzw_provider_name = "hVoLTE-Verizon"
            default_provider_name = "ROW_Generic_3GPP"
            vzw_image_name = "MIMG VZW"

        res_provider_name = ".*" + vzw_provider_name + ".*OK.*"
        res_image_name = ".*" + vzw_image_name + ".*OK.*"

        test.dut.at1.send_and_verify("at+CPIN?",".*O.*")
        if not ("SIM PIN" in test.dut.at1.last_response):
            test.expect(test.dut.dstl_lock_sim())

        test.log.step('Step 1.1: check if vzw provider config is listed via ati61')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("ati61",res_provider_name ))

        test.log.step('Step 1.2: check if default provider config is listed via ati61')
        # ==============================================================
        res_provider_name = ".*" + default_provider_name + ".*OK.*"
        test.expect(test.dut.at1.send_and_verify("ati61",res_provider_name ))

        test.log.step('Step 2.1: disable provider autoselect and select default provider')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg," + default_provider_name , ".*OK.*"))

        test.log.step('Step 2.2: restart module')
        # ==============================================================
        test.expect(test.dut.dstl_restart())

        test.log.step('Step 2.3: check if Default Image is running')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("ati61", ".*MIMG DEFAULT.*OK.*"))
        test.log.info("register to network only for restart check")
        test.expect(test.dut.dstl_register_to_network())

        test.log.step('Step 3.0: select VzW Image')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg," + vzw_provider_name , ".*OK.*"))

        test.log.step('Step 3.1: module must restart automaticly wait 60 sec')
        # ==============================================================
        test.sleep (60)
        test.dut.at1.send_and_verify("at+CPIN?",".*O.*")
        if ("READY" in test.dut.at1.last_response):
            test.expect(False)
            test.log.info ("Module is still registered, no restart seen")
            test.log.info ("restart the module manually")
            test.expect(test.dut.dstl_restart())
        else:
            test.expect(True)
            test.log.info("Restart was done")

        test.log.step('Step 4.0: Check if MIMG VZW is listed via ati61')
        # ==============================================================
        # Todo correct name must be define

        test.expect(test.dut.at1.send_and_verify("ati61", res_image_name))

        pass

    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        # ==============================================================
        test.log.com('**** log  dir: ' + test.workspace + ' ****')
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/AutoSelect,\"off\"", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at^scfg=MEopMode/Prov/Cfg," + default_provider_name , ".*OK.*"))
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass

if (__name__ == "__main__"):
    unicorn.main()
