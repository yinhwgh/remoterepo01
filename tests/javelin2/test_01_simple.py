import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary import download_software_by_swup
from dstl.internet_service.lwm2m.lwm2m_server import Lwm2mServer

class Test(BaseTest):

    def setup(test):
        """Setup method.
        Steps to be executed before test is run.
        """
        # test.log.debug("This is a debug!")
        # test.log.info("This is an info!")
        # test.log.warning("This is a warning!")
        # test.log.error("This is an error!")
        # test.log.critical("This is a critical!")
        test.lwm2m = Lwm2mServer(stack_id_str="mods", secure=False)
        test.log.info("Setting up the test")
        # test.os.execute("ping www.baidu.com")
        #dstl_detect(test.dut)

    def run(test):
        """Run method.

        Actual test steps.
        """

        test.kpi.timer_start("ping_duration", device=test.dut)

        test.log.info("Test is running")
        #test.dut.dstl_restart()
        #test.dut.dstl_detect()

        dstl_detect(test.dut)
        print(test.dut)

        test.dut.at1.send_and_verify("ati", "OK")

        print(test.dut.at1.last_response)
        # test.dut.at1.send('ati')
        # test.sleep(10)
        # print(test.dut.at1.last_response)
        # test.sleep(10)
        # test.expect(test.dut.at1.send_and_verify("at+cgdcont?"), weight=4)
        # print(test.dut.at1.last_response)
        # test.dut.at1.send('at+cops?')
        # test.dut.at1.wait_for_strict('CHINA')
        # print(test.dut.at1.last_response)
        # test.dut.at1.wait_for_strict('ok', timeout=10)
        # print(test.dut.at1.last_response)
        # print(test.workspace)
        test.log.step("1. lwm2m.client.dstl_init_client()")
        test.expect(test.dut.at1.send_and_verify("at+cops=3,0"))
        test.lwm2m.client.dstl_init_client()
        test.log.step("2. lwm2m.dstl_add_client_to_dm_server()")
        test.expect(test.lwm2m.dstl_add_client_to_dm_server())
        test.log.step("3. lwm2m.dstl_start_client(timeout=120)")
        test.expect(test.lwm2m.dstl_start_client(timeout=120))
        test.sleep(20)
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","fwdownload/deferLimit","0"'))
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","fwupdate/deferLimit","0"'))
        test.log.step("4. lwm2m.fota.dstl_start_server_download()")
        test.lwm2m.fota.dstl_start_server_download()
        # test.expect(test.dut.dstl_check_urc('\\^SNLWM2M: "procedure","mods",,"fwdownload",'
        #                                     '"progress","100%"', timeout=300))
        test.expect(test.dut.dstl_check_urc('\\^SRVACT: "MODS","fwdownload","progress","100%"', timeout=300))
        # test.expect(test.dut.dstl_check_urc('\\^SNLWM2M: "procedure","mods",,"fwdownload",'
        #                                     '"finished","download success"', timeout=60))
        test.expect(test.dut.dstl_check_urc('\\^SNLWM2M: "procedure","mods",,"fwdownload",'
                                            '"finished","download \\^SRVACT: "MODS","fwdownload","finished","download success"', timeout=60))
        # test.expect(test.dut.dstl_check_urc('\\^SNLWM2M: "procedure","mods",,"fwupdate",'
        #                                     '"progress","starting update"', timeout=120))
        test.expect(test.dut.dstl_check_urc('\\^SNLWM2M: "procedure","mods",,"fwupdate",'
                                            '"progress","starting up\\^SRVACT: "MODS","fwupdate","progress","starting update"', timeout=120))
        test.expect(test.dut.dstl_check_urc("\\^SYSSTART AIRPLANE MODE", timeout=60))
        test.expect(test.dut.dstl_check_urc("\\^SYSSTART", timeout=600))
        test.kpi.timer_stop("ping_duration")
        test.sleep(30)
    def cleanup(test):
        """Cleanup method.
        Steps to be executed after test run steps.
        """
        test.log.info("Cleaning up the test")
        test.log.step("1. lwm2m.fota.dstl_cancel_server_update()")
        test.lwm2m.fota.dstl_cancel_server_update()
        test.log.step("2. dut.dstl_download_software_by_swup()")
        test.expect(test.dut.dstl_download_software_by_swup())

if "__main__" == __name__:
    unicorn.main()