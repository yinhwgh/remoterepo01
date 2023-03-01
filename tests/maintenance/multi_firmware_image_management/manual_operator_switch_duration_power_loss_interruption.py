# responsible: kamil.kedron@globallogic.com
# location: Wroclaw
# TC0105201.001 ManualOperatorSwitchDurationPowerLossInterruption



import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
import sys
from pywinauto import application


class Test(BaseTest):
    """Example test: Send AT command
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*", timeout=10))
        dstl_restart(test.dut)

        test.log.info("\n0. Read parameters.")
        try:
            test.gwinswup_path = "C:\Projects\Cougar\cougar_400_044\swup"
        except IndexError as ex:
            test.log.critical("Missing gwinswup path!")
            test.log.exception(ex)
            test.fail()

        try:
            test.image_path = "C:\Projects\Cougar\cougar_400_040\swup\ems31-j_sbm-r04.014_a01.000.11_dcm-r04.014_a01.000.11_cougar_400_044.usf"
        except IndexError as ex:
            test.log.critical("Missing image path!")
            test.log.exception(ex)
            test.fail()

        try:
            test.interval = 0.01
        except IndexError:
            test.log.warning("Parameter interval not defined! Default value is 0.01")
            test.interval = 0.01

        test.log.info("Path to gwinswup = " + test.gwinswup_path)
        test.log.info("Path to image = " + test.image_path)
        test.log.info("Interval = " + str(test.interval))

    def run(test):
        """
        TC0105201.001 ManualOperatorSwitchDurationPowerLossInterruption
        To check if Operator Switch update is possible in case of continuous connection/power lose during FW update.
        Module disconnection interval is 1ms.

        author mateusz.strzelczyk@globallogic.com
        Location: Wroclaw
        """

        """
        Test needs 3 parameters:
        - interval - how often power cuts have to be
        - gwinswup_path - full path to execution file gwinswup
        - image_path - full path to .usf image file of current TR
        """

        test.operators = test.give_operators()
        test.dut.at1.send_and_verify("AT^SCFG=\"MEopMode/Prov/AutoSelect\", \"off\"")

        for i in range(2):
            time = test.interval
            test.change_operator()
            test.log.info(f"Sleep time is: {time}s")
            test.sleep(time)

            while "SYSSTART" not in test.dut.at1.last_response:
                test.reset_module()
                time += test.interval
                test.log.info(f"Sleep time is: {time}s")
                test.sleep(time)
                test.dut.at1.read()

    def cleanup(test):
        test.dut.at1.send_and_verify("AT&F", ".*OK.*", timeout=10)

    def reset_module(test):
        """
        Power cutting. If module does not responding of any reason (different baudrate, download mode etc.)
        :return:
        """

        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", ".*OK.*", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 0", ".*OK.*", timeout=10)
        test.sleep(5)
        test.dut.devboard.send_and_verify("CONF:GPIO:PG0 OUTPP", ".*OK.*", timeout=10)
        test.dut.devboard.send_and_verify("OUTP:GPIO:PG0 1", ".*OK.*", timeout=10)

        if test.dut.at2.wait_for(".*\S.*", timeout=60):
            return
        test.log.info("Module does not responding, trying to reconnect.")
        test.dut.devboard.send("OUTP:EMRG on")
        test.sleep(5)
        test.dut.devboard.send("OUTP:EMRG off")

        if test.dut.at2.wait_for(".*\S.*", timeout=60):
            return

        test.dut.devboard.send("MC:IGT=555")
        if test.dut.at2.wait_for(".*\S.*", timeout=60):
            return
        test.dut.at1.send_and_verify("AT+SMCLEANBOOT", ".*OK.*", timeout=10)
        if test.dut.at1.wait_for(".*\S.*", timeout=10):
            return

        test.do_swup()
        if test.dut.at1.send_and_verify("AT", ".*OK.*", timeout=10):
            test.change_operator()
            return
        else:
            test.log.critical("Module does not turn on!")
            test.fail()

    def toggle_operator(test, response, operator):
        """
        Return operator which is not active in this moment
        """
        if operator[0] in response:
            return operator[1]
        elif operator[1] in response:
            return operator[0]

    def give_operators(test):
        """
        Depending of step of Cougar return valid operators
        """
        operators = {
            "X": ["attus", "verizonus"],
            "J": ["sbmjp", "docomojp"]
        }
        return operators[test.dut.variant]

    def do_swup(test):
        """
        try to upload soft
        """
        app = application.Application().start(test.gwinswup_path)
        dlg = app.top_window()
        dlg.FilenameEdit.set_edit_text(test.image_path)
        dlg.PortEdit.set_edit_text(test.dut.at1.port)
        dlg.BaudrateComboBox.select("921600")
        test.dut.at1.close()
        test.log.info("Pressing START button")
        dlg.STARTButton.click()

        end_time = 0
        while "Update succeeded" not in test.dlg.StatusEdit.get_line(0):
            test.sleep(11)
            end_time += 11
            test.log.info(dlg.StatusEdit.get_line(0))
            if "ERROR: Update failed" in test.dlg.StatusEdit.get_line(0):
                test.log.info(dlg.StatusEdit.get_line(0))
                test.fail()
            if "ERROR: Module do not respond to at commands on any known baudrate." in dlg.StatusEdit.get_line(0):
                test.log.info(dlg.StatusEdit.get_line(0))
                dlg.STARTButton.click()

            if end_time > 240:
                test.log.info("Module does not respond, unable to reupload software!")
                test.fail()

    def change_operator(test):
        test.dut.at1.send_and_verify("AT^SINFO=\"Fw/DeltaPkg/current\"", ".*OK.*", timeout=10)
        test.dut.at1.send_and_verify(
            f"AT^SCFG= \"MEopMode/Prov/Cfg\",{test.toggle_operator(test.dut.at1.last_response, test.operators)}",
            ".*OK.*", timeout=10)


if "__main__" == __name__:
    unicorn.main()