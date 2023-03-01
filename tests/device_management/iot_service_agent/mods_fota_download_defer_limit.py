#responsible: wenyan.wu@thalesgroup.com
#location: Beijing
#TC
import unicorn

from core.basetest import BaseTest
from dstl.internet_service import start_stop_mods_service
from dstl.internet_service import set_get_mods_client_service_tag
from dstl.internet_service import trigger_mods_fota_action


class ModsFotaConditional(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.info('1. Set conditional pull download...')
        test.expect(test.dstl_set_fwdownload_deferlimit("5"))

        test.log.info("2. Start IoT Service Agent service...")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(test.dut.dstl_start_mods_service())

        test.log.info("3. Trigger FOTA from MODS server...")
        # Trigger FOTA from MODS server

        test.dut.at1.wait_for('.*^SRVACT: "MODS","ready","to download"\\s+')

        test.log.info("4. Initiate the firmware download...")
        test.expect(test.dut.dstl_trigger_mods_fota_download())
        test.dut.at1.wait_for('.*^SRVACT: "MODS","fwdownload","init".*')

        test.log.info("5. Wait for progress URC...")
        i = 5
        while i < 100:
            test.dut.at1.wait_for('.*^SRVACT: "MODS","fwdownload","progress",{}.*'.format(i), 5*60)
            i += 5

        test.log.info("6. Check whether the counter for fwdownload/deferLimit is reset to 5")
        test.expect(test.dut.dstl_get_fwdownload_deferlimit() == "5")


        test.dut.at1.wait_for('.*^SRVACT: "MODS","fwdownload","status","download success".*')
        test.dut.at1.wait_for(".*SYSSTART.*", 5*60)
        test.dut.at1.send_and_verify("AT^CICRET=SWN")

    def cleanup(test):
        pass


if __name__ == "__main__":
    unicorn.main()
