# responsible: yafan.liu@thalesgroup.com
# location: Beijing
# TC0105957.001

import unicorn
import getpass
import time
from datetime import datetime
from datetime import timedelta
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.internet_service.mods_server import ModsServer
from dstl.serial_interface.config_baudrate import dstl_set_baudrate
from tests.rq6 import smart_meter_init_module_normal_flow as init
from tests.rq6 import smart_meter_read_status_normal_flow
from tests.rq6 import smart_meter_provide_data_connection_normal_flow


class Test(BaseTest):
    def setup(test):
        test.dut.dstl_detect_comprehensive()
        pass

    def run(test):
        init.set_run_all(False)
        init.uc_init_module(test, 1)
        test.log.info("*****Smart meter update module normal flow start.*****")
        uc_update_module(test)

    def cleanup(test):
        pass


def uc_update_module(test):
    test.log.info("1.1  Fota configuration in UC InitModule")
    fota_settings(test)
    test.log.info("1.2 Create a Fota job on Mods server and schedule it.")
    mods_server_obj = ModsServer()
    # mods_server_obj = ModsServer("https://partners-mods.gemalto.io/", "root.Thales", "yafan.liu@thalesgroup.com",
    #                              "Edcol.1234")
    # mods_server_obj = ModsServer("10.151.127.73", "8443", "10.151.127.74", "19280", "19170", "root.SERVAL",
    #                              "serval@gemalto.com", "mods,123")

    ############################################
    # Input parameters:
    # test.current_firmware = "SERVAL_300-ATT_014H"
    # test.target_firmware = "SERVAL_300-ATT_014G"
    # test.firware_package = "serval_300_014E_014G"
    ############################################

    imei = test.dut.dstl_get_imei()
    fota_job_name = "{}_{}_FOTA".format(getpass.getuser(),
                                        time.strftime("%Y-%m-%d_%H:%M:%S"))
    start_time = (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    job_id = mods_server_obj.dstl_trigger_fota_from_mods_server(fota_job_name,
                                                                test.upgrade_fota_package_name,
                                                                imei,
                                                                start_time,
                                                                end_time)
    mods_server_obj.dstl_check_job_status(job_id)
    test.log.info("2. Check the progress status of the firmware download.")
    if test.dut.at1.wait_for(r'^SRVACT: "MODS","fwdownload","progress"', timeout=60 * 5):
        test.log.info("Firmware downloading...")
        test.expect(True)
        if test.dut.at1.wait_for(".*SYSSTART.*", timeout=60 * 60 * 2):
            test.log.info("SYSTART received")
            test.expect(True)
            test.dut.dstl_detect_comprehensive()
            current_firmware = test.dut.software
            test.log.info("3. Check firmware version.")
            if (current_firmware in test.target_firmware) and (len(current_firmware) == len(test.target_firmware)):
                test.log.info("Software version after FOTA: {}{}".format(test.dut.project, test.dut.software))
                test.expect(True)
            else:
                test.log.info("Software version mismatch.")
                test.expect(False)
        else:
            test.log.info("Fail to update module.")
            test.expect(False)
    else:
        test.log.info("Fail to download firmware.")
        test.expect(False)


def fota_settings(test):
    test.log.info("Configured to conditional pull download and unconditional update.")
    test.dut.at1.send_and_verify('AT^SRVCFG="MODS","fwdownload/deferLimit","1"', 'OK')
    test.dut.at1.send_and_verify('AT^SRVCFG="MODS","fwupdate/deferLimit","0"', 'OK')
    test.log.info("Switch on the URCs.")
    test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', 'OK')
    test.dut.at1.send_and_verify('ATV1')
    test.dut.at1.send_and_verify('ATE1')
    test.log.info("Restart module.")
    test.dut.dstl_restart()
    test.dut.devboard.close()
    return True


if __name__ == "__main__":
    unicorn.main()
