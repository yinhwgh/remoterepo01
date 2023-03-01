# responsible: kamil.kedron@globallogic.com
# location: Wroclaw
# TC0105181.001 - IncrementalSwupContinuousPowerLossInterruption1
# TC0105182.001 - IncrementalSwupDurationPowerLossInterruption1

import unicorn
from pywinauto import application
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
import sys


class Test(BaseTest):

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=10))
        dstl_restart(test.dut)

        test.log.info("\n0. Read parameters.")

        try:
            import pywinauto
        except ImportError as ex:
            test.log.critical("pywinauto module must be installed to run the test!")
            test.log.exception(ex)
            test.fail()

        try:
            test.gwinswup_path = "C:\Projects\Cougar\Cougar_400_030\swup\gwinswup.exe"
        except IndexError as ex:
            test.log.critical("Missing gwinswup path!")
            test.log.exception(ex)
            test.fail()

        try:
            test.image_path = "C:\Projects\Cougar\Cougar_400_030\cougar_400_030A\ems31-j_sbm-r04.014_a01.000.04_dcm-r04.014_a01.000.04_cougar_400_030__ems31-j_sbm-r04.014T_a01.000.04_dcm-r04.014T_a01.000.04_cougar_400_030A.usf"
        except IndexError as ex:
            test.log.critical("Missing incremental image path!")
            test.log.exception(ex)
            test.fail()

        try:
            test.lower_image_path = "C:\Projects\Cougar\Cougar_400_030\swup\ems31-j_sbm-r04.014_a01.000.04_dcm-r04.014_a01.000.04_cougar_400_030.usf"
        except IndexError as ex:
            test.log.critical("Missing image lower version software path!")
            test.log.exception(ex)
            test.fail()

        try:
            test.interval = "0.2"
        except IndexError:
            test.log.info("Parameter interval not defined! Default value is 0.01")
            test.interval = 0.1

        test.validate_software()
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/FwUpdateMode\",\"normal\"", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify("AT+IPR=921600", ".*OK.*", timeout=10)
        test.dut.at1.reconfigure({
            "baudrate": 921600
        })

        test.log.info("Path to gwinswup = " + test.gwinswup_path)
        test.log.info("Path to incremental image = " + test.image_path)
        test.log.info("Path to lower software image = " + test.lower_image_path)
        test.log.info("Interval = " + test.interval)

    def run(test):
        """
        TC0105181.001 IncrementalSwupContinuousPowerLossInterruption
        To check if SWUP update is possible in case of continuous connection/power lose for Incremental FW update. Module disconnection interval is 10ms.
        author mateusz.strzelczyk@globallogic.com
        Location: Wroclaw
        """
        """
        3 ports are needed to map for this test:
        ASC0, ASC2, Ctrl (dsb2016)

        Test needs 4 parameters:
        - gwinswup_path - full path to execution file gwinswup
        - image_path - full path to .usf incremental image file of current TR
        - lower_image_path - full path to lower software image .usf file of current TR
        - interval - how often power cuts have to be
        """
        test.log.info("\n1. Set up gwinswup.")
        time = 22.55
        test.log.info("Gwinswup path = " + test.gwinswup_path)
        test.log.info("Image path = " + test.image_path)

        app = application.Application().start(test.gwinswup_path)
        test.dlg = app.top_window()
        test.dlg.FilenameEdit.set_edit_text(test.image_path)
        test.dlg.PortEdit.set_edit_text(test.dut.at1.port)
        test.dlg.BaudrateComboBox.select("921600")
        test.dut.at2.open()

        test.log.info("\n2. Start incremental updating with power cutting.")
        test.press_start_button()

        test.log.info(f"Sleep time is: {time}s")
        test.sleep(time)

        if test.dut.at2.wait_for(".*UPDATER.*", timeout=10):
            while True:
                result = test.reset_module()
                if result == False:
                    break
                else:
                    while not test.dlg.STARTButton.is_enabled():
                        test.log.info(test.dlg.StatusEdit.get_line(0))
                        test.sleep(2)

                    test.press_start_button()
                    time += 0.01

                while "Firmware update in progress" not in test.dlg.StatusEdit.get_line(0):
                    test.log.info(test.dlg.StatusEdit.get_line(0))
                    test.sleep(0.1)
                test.sleep(2)
                if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                    test.log.info("Check current software")
                    dstl_detect(test.dut)
                    break
                #     test.force_swup()
                #     test.press_start_button()
                #     while "Firmware update in progress" not in test.dlg.StatusEdit.get_line(0):
                #         test.log.info(test.dlg.StatusEdit.get_line(0))
                #         test.sleep(0.1)
                #
                test.log.info(f"Sleep time is: {time}s")
                test.sleep(time)
                test.log.info(test.dlg.UpdateStatusEdit.get_line(0))
                # if "Update failed" in test.dlg.UpdateStatusEdit.get_line(0):
                #     test.downgrade_soft()

        # while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
        #     test.sleep(10)
        test.dlg.close()
        """
        It is possible that module does not responding, but through yatt communication is well. To investigation.
        """
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
        test.log.info("Check current software")
        dstl_detect(test.dut)

        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)

    def reset_module(test):
        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 0", "OK", timeout=10)

        test.log.info(test.dlg.StatusEdit.get_line(0))
        while "ERROR: Update failed" not in test.dlg.StatusEdit.get_line(0):
            test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 0", "OK", timeout=10)
            test.log.info(test.dlg.StatusEdit.get_line(0))
            test.sleep(5)
            if "ERROR: Cannot access module after upgrade" in test.dlg.StatusEdit.get_line(0):
                break
            if "Transfer succeeded" in test.dlg.StatusEdit.get_line(0):
                return False
            if "Update succeeded" in test.dlg.StatusEdit.get_line(0):
                return False

        test.log.info(test.dlg.StatusEdit.get_line(0))
        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", "OK", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", "OK", timeout=10)
        test.dut.at1.read()

        if "Transfer succeeded" in test.dlg.StatusEdit.get_line(0):
            return False

        test.sleep(5)

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=20):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })

        test.log.info("Module does not responding, trying to reconnect.")
        test.dut.devboard.send("OUTP:EMRG on")
        test.sleep(5)
        test.dut.devboard.send("OUTP:EMRG off")

        if "Transfer succeeded" in test.dlg.StatusEdit.get_line(0):
            return False

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=20):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })

        if "SYSSTART" in test.dut.at1.last_response:
            return
        test.dut.devboard.send("MC:IGT=555")
        test.dut.at1.read()

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=20):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })

        if "SYSSTART" in test.dut.at1.last_response:
            return
        else:
            test.log.info("Module does not wake up after power loss!")
        test.dut.at1.read()

        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=10):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })
            test.downgrade_soft()

            if "SYSSTART" in test.dut.at1.last_response:
                return
            else:
                test.log.info("Module does not wake up after power loss!")
                test.fail()

    def inter_check(test):
        try:
            if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=20):
                return
        except:
            test.dut.at1.reconfigure({
                "baudrate": 921600
            })


    def force_swup(test):
        """
        Getting crushdump from module.
        """
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
        test.downgrade_soft()
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/FwUpdateMode\", \"normal\"", ".*OK.*", timeout=10)

    def downgrade_soft(test):
        """
        Downgrade soft to starting version. Useful when module is in downgrade mode or soft version changed before
        successfull incremental upgrade.
        """
        test.dlg.FilenameEdit.set_edit_text(test.lower_image_path)
        test.press_start_button()
        while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.sleep(30)
            test.log.info(test.dlg.StatusEdit.get_line(0))
            if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                test.log.info(test.dlg.StatusEdit.get_line(0))
                test.log.info("Unknown error during downgrade!")
                test.fail()
            if "ERROR: Module do not respond to at commands on any known baudrate." in test.dlg.StatusEdit.get_line(0):
                test.log.info(test.dlg.StatusEdit.get_line(0))
                test.press_start_button()
        test.dlg.FilenameEdit.set_edit_text(test.image_path)

    def validate_software(test):
        if not (
                test.dut.variant == "X" and "cougar_30" in test.image_path or test.dut.variant == "J" and "cougar_40" in test.image_path):
            test.log.critical("Invalid software!")
            test.log.critical(
                f"This module is {test.dut.product}-{test.dut.variant}, but linked software is {test.image_path}!")
            test.log.critical("Please add path to correct software!")
            test.fail()

    def press_start_button(test):
        test.dut.at1.close()
        test.log.info("Pressing START button")
        test.dlg.STARTButton.click()


if "__main__" == __name__:
    unicorn.main()
