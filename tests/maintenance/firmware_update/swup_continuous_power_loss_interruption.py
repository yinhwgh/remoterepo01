# responsible: kamil.kedron@globallogic.com
# location: Wroclaw
# TC0105185.001 - SwupContinuousPowerLossInterruption1
# TC0105186.001 - SwupDurationPowerLossInterruption


import unicorn
from pywinauto import application
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
import sys


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT&W", "OK", timeout=10))
        dstl_restart(test.dut)

        try:
            import pywinauto
        except ImportError as ex:
            test.log.critical("pywinauto module must be installed to run the test!")
            test.log
            test.fail()

        try:
            # test.gwinswup_path = sys.argv[1]
            test.gwinswup_path = "C:\Projects\Cougar\cougar_400_054A\swup"
        except IndexError as ex:
            test.log.critical("Missing gwinswup path!")
            test.log.exception(ex)
            test.fail()

        try:
            #test.image_path = sys.argv[2]
            test.image_path = "C:\Projects\Cougar\cougar_400_054A\swup\ems31-j_sbm-r04.014_a01.000.16T_dcm-r04.014_a01.000.16T_cougar_400_054A.usf"
        except IndexError as ex:
            test.log.critical("Missing image path!")
            test.log.exception(ex)
            test.fail()

        try:
            # test.interval = sys.argv[3]
            test.interval = 0.01
        except IndexError:
            test.log.info("Parameter interval not defined! Default value is 0.1")
            test.interval = 0.01

        test.validate_software()
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/FwUpdateMode\",\"normal\"", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify("AT+IPR=921600", ".*OK.*", timeout=10)
        test.dut.at1.reconfigure({
            "baudrate": 921600
        })

    def run(test):
        """
        author mateusz.strzelczyk@globallogic.com
        Location: Wroclaw
        """
        # time = 106.9300000000178  # <- for IPIS retest
        time = 5
        test.log.info("Gwinswup path = " + test.gwinswup_path)
        test.log.info("Image path = " + test.image_path)

        app = application.Application().start(test.gwinswup_path + "\gwinswup.exe")
        test.dlg = app.top_window()
        test.dlg.FilenameEdit.set_edit_text(test.image_path)
        test.dlg.PortEdit.set_edit_text(test.dut.at1.port)
        test.dlg.BaudrateComboBox.select("921600")
        test.dut.at2.open()
        test.press_start_button()

        test.log.info(f"Sleep time is: {time}s")
        test.sleep(time)

        while "Transfer succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.reset_module()
            while not test.dlg.STARTButton.is_enabled():
                test.sleep(1.01)

            test.press_start_button()
            time += test.interval
            while "Firmware update in progress" not in test.dlg.StatusEdit.get_line(0):
                test.log.info(test.dlg.StatusEdit.get_line(0))
                test.sleep(0.1) #usunąć?
                if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                    test.press_start_button()

            test.sleep(2)
            if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                test.force_swup()
                test.press_start_button()
                while "Firmware update in progress" not in test.dlg.StatusEdit.get_line(0):
                    test.log.info(test.dlg.StatusEdit.get_line(0))
                    test.sleep(0.1)

            test.log.info(f"Sleep time is: {time}s")
            test.sleep(time)
            test.log.info(test.dlg.UpdateStatusEdit.get_line(0))

        while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.sleep(10)
        test.dlg.close()
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", "OK", timeout=10)
        try:
            test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=10)
        except:
            pass
        try:
            test.dut.at1.send_and_verify("AT+IPR=115200", ".*OK.*", timeout=10)
        except:
            pass

    def cleanup(test):
        test.dut.at1.reconfigure({
            "baudrate": 115200
        })
        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)

    def reset_module(test):
        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 0", "OK", timeout=10)
        test.sleep(5)
        test.log.info(test.dlg.StatusEdit.get_line(0))
        while "ERROR" not in test.dlg.StatusEdit.get_line(0):
            test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", "OK", timeout=10)
            test.log.info(test.dlg.StatusEdit.get_line(0))
            test.sleep(1.2)
            if "ERROR: Cannot access module after upgrade" in test.dlg.StatusEdit.get_line(0):
                break
            if "Transfer succeeded" in test.dlg.StatusEdit.get_line(0):
                return
            if "Update succeeded" in test.dlg.StatusEdit.get_line(0):
                return


        test.log.info(test.dlg.StatusEdit.get_line(0))
        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", "OK", timeout=10)

        test.sleep(5)

        test.log.info("Module does not responding, trying to reconnect.")
        test.dut.devboard.send("OUTP:EMRG on")
        test.sleep(5)
        test.dut.devboard.send("OUTP:EMRG off")

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=20):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 115200
            })

            test.sleep(5)

        if test.dut.at1.wait_for(".*\^SYSSTART.*", timeout=120):
            return
        test.dut.devboard.send("MC:IGT=555")

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=10):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })

        if test.dut.at1.wait_for(".*\^SYSSTART.*", timeout=120):
            return
        else:
            test.log.info("Module does not wake up after power loss!")

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=10):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })
            test.fast_swup()

            """test.dut.devboard.send("OUTP:EMRG on")
            test.dut.devboard.send("OUTP:EMRG off")
            test.dut.devboard.send("MC:IGT=555")
            test.dut.at1.send_and_verify("AT+SMCLEANBOOT", "OK", timeout=10)"""

    def fast_swup(test):
        test.press_start_button()
        end_time = 0
        while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.sleep(11)
            end_time += 11
            test.log.info(test.dlg.StatusEdit.get_line(0))
            if end_time > 300:
                test.log.info("Module does not respond")
                test.fail()
            if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                test.log.info(test.dlg.StatusEdit.get_line(0))
                test.force_swup()
            if "ERROR: Module do not respond to at commands on any known baudrate." in test.dlg.StatusEdit.get_line(0):
                test.log.info(test.dlg.StatusEdit.get_line(0))
                test.press_start_button()

    def force_swup(test):
        test.dut.at1.send_and_verify("AT!=cat /userfs/ems/ota/conf_file_fails.cfg", ".*(ERROR|OK).*", timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/ems/ota/over_file_fails.cfg", ".*(ERROR|OK).*", timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/user/logs/user_conf_op_file_fails.cfg", ".*(ERROR|OK).*",
                                     timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/user/logs/user_conf_file_fails.cfg", ".*(ERROR|OK).*", timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/ems/ota/conf_file_fails_opsw.cfg", ".*(ERROR|OK).*", timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/ems/ota/over_file_fails_opsw.cfg", ".*(ERROR|OK).*", timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/user/logs/user_conf_op_file_fails_opsw.cfg", ".*(ERROR|OK).*",
                                     timeout=10)
        test.dut.at1.send_and_verify("AT!=cat /userfs/user/logs/user_conf_file_fails_opsw.cfg", ".*(ERROR|OK).*",
                                     timeout=10)

        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/FwUpdateMode\", \"forced\"", ".*OK.*", timeout=10)
        test.dut.at1.close()
        test.press_start_button()
        while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.sleep(20)
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/FwUpdateMode\", \"normal\"", ".*OK.*", timeout=10)

    def validate_software(test):
        if not (test.dut.variant == "X" and "cougar_30" in test.image_path or test.dut.variant == "J" and "cougar_40" in test.image_path):
            test.log.critical("Invalid software!")
            test.log.critical(f"This module is {test.dut.product}-{test.dut.variant}, but linked software is {test.image_path}!")
            test.log.critical("Please add path to correct software!")
            test.fail()

    def press_start_button(test):
        test.dut.at1.close()
        test.log.info("Press START button")
        test.dlg.STARTButton.click()


if "__main__" == __name__:
    unicorn.main()