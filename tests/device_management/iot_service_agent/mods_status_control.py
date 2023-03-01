#responsible: xueping.zhang@thalesgroup.com
#location: Beijing
#TC

import unicorn

from core.basetest import BaseTest

from dstl.internet_service import start_stop_mods_client
from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network


class Lwm2mStatusControl(BaseTest):
    def setup(test):
        pass

    def run(test):
        test.log.info("1. Check the status of IoT Service Agent service by AT^SRVCTL=\"MODS\",status on module startup.")
        # Need to check the status of Service on module startup.
        test.dut.dstl_restart()
        test.expect(not test.dut.dstl_check_mods_service_status())

        test.expect(test.dut.dstl_register_to_network())

        test.sleep(30)

        test.log.info("2. Start IoT Service Agent service by AT^SRVCTL=\"MODS\",start.")
        test.expect(test.dut.dstl_start_mods_service())

        test.log.info("3. Check the status of IoT Service Agent service by AT^SRVCTL=\"MODS\",status.")
        test.expect(test.dut.dstl_check_mods_service_status())

        test.sleep(300)

        test.log.info("4. Restart module with IOT service agent running")
        test.expect(test.dut.dstl_restart())

        test.expect(test.dut.dstl_register_to_network())

        test.sleep(30)

        test.log.info("5. Check the status of IoT Service Agent service by AT^SRVCTL=\"MODS\",status.")
        test.expect(not test.dut.dstl_check_mods_service_status())

        # test.log.info("6. Stop IoT service agent by AT^SRVCTL=\"MODS\",stop")
        # test.expect(test.dut.dstl_stop_mods_service())

        # test.log.info("6. Check the status of IoT Service Agent service by AT^SRVCTL=\"MODS\",status.")
        # test.expect(not test.dut.dstl_check_mods_service_status())

        test.log.info("6. Loop 5 times: "
                      "start  IoT Service Agent service; "
                      "let it run for 3 minutes; "
                      "stop IoT Service Agent service.")

        for i in range(3):
            test.log.info("Loop {} starts...".format(i+1))
            test.log.info("6.{} start mods service...".format(i + 1))
            test.expect(test.dut.dstl_start_mods_service())

            test.sleep(300)

            test.log.info("6.{} Check mods service status...".format(i + 1))
            test.expect(test.dut.dstl_check_mods_service_status())

            test.log.info("6.{} Stop mods service...".format(i + 1))
            test.dut.dstl_stop_mods_service()
            test.log.info("6.{} Check mods service status...".format(i + 1))
            test.expect(not test.dut.dstl_check_mods_service_status())
            test.log.info("Loop {} ends...".format(i + 1))

            test.sleep(300)

    def cleanup(test):
        if test.dut.dstl_check_mods_service_status():
            test.dut.dstl_stop_mods_service()


if __name__ == "__main__":
    unicorn.main()
