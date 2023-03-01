#responsible: shuang.liang@thalesgroup.com
#location: Beijing

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_gsm
from dstl.network_service.register_to_network import dstl_register_to_umts
from dstl.network_service.register_to_network import dstl_register_to_lte
from dstl.auxiliary import init
from dstl.auxiliary import restart_module


class Test(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_restart()
        pass

    def run(test):
        imsi = test.dut.sim.imsi
        mcc_mnc: object = imsi[0:5]
        test.log.com('mcc_mnc:' + mcc_mnc)

        test.log.step("1. Power on module and enter the PIN code.")
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(5)
        # enable creg indication with at + creg=2
        test.dut.at1.send_and_verify("at+creg=2", "OK")

        # enable text error message format
        test.dut.at1.send_and_verify("at+cmee=2", "OK")

        test.log.step("2. Check AT+COPS write command explicitly set the <AcT>:")
        test.log.step("2.1. Register to GSM: AT+COPS= <mode>,<format>,<opName>,0")
        test.expect(dstl_register_to_gsm(test.dut))

        test.log.step("2.2. Read the current selected radio access technology: AT+COPS?")
        test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,0.*OK")

        test.log.step("2.3. Deregister from network.")
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*OK.*"))

        test.log.step("2.4. Register to UTRAN: AT+COPS= <mode>,<format>,<opName>,2")
        test.expect(dstl_register_to_umts(test.dut))

        test.log.step("2.5. Read the current selected radio access technology: AT+COPS?")
        test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,2.*OK")

        test.log.step("2.6. Deregister from network.")
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*OK.*"))

        test.log.step("2.7. Register to UTRAN: AT+COPS= <mode>,<format>,<opName>,7")
        test.expect(dstl_register_to_lte(test.dut))

        test.log.step("2.8. Read the current selected radio access technology: AT+COPS?")
        test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,7.*OK")

        test.log.step("2.9. Deregister from network.")
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*OK.*"))

        test.log.step("2.10. Check invalid parameters: eg. <AcT>=-1,1,3,8")
        for invalid_act in ["-1", "1", "3", "8"]:
            test.expect(test.dut.at1.send_and_verify("at+cops=,,,{}".format(invalid_act), ".*ERROR.*"))

        test.log.step("3. Check AT+COPS write command without set the <AcT>:")
        test.log.step("3.1 Register to network without set <AcT>: AT+COPS= <mode>,<format>,<opName>")
        test.expect(test.dut.at1.send_and_verify("at+cops=1,2,{}".format(mcc_mnc), ".*OK.*"))

        test.log.step("3.2. Read the current selected radio access technology: AT+COPS?")
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,[027].*OK"))

        test.log.step("3.3. Deregister from network.")
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*OK.*"))

        test.log.step("3.4 Register to network without set <AcT>: AT+COPS=0")
        test.expect(test.dut.at1.send_and_verify("at+cops=0", ".*OK.*"))

        test.log.step("3.5. Read the current selected radio access technology: AT+COPS?")
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,[027].*OK"))

        test.log.step("3.6. Deregister from network.")
        test.expect(test.dut.at1.send_and_verify("at+cops=2", ".*OK.*"))

        test.log.step("4. Check AT+COPS test command:")
        test.log.step("4.1 Register to GSM (Repeat step 2.1) and then check AT+COPS test command;")
        test.expect(dstl_register_to_gsm(test.dut))
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,[03].*OK"))

        test.log.step("4.2. Register to UTRAN (Repeat step 2.4) and then check AT+COPS test command;")
        test.expect(dstl_register_to_umts(test.dut))
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,[26].*OK"))

        test.log.step("4.3. Register to LTE(Repeat step 2.7) and then check AT+COPS test command.")
        test.expect(dstl_register_to_lte(test.dut))
        test.expect(test.dut.at1.send_and_verify("at+cops?", ".*\+COPS:.*,.*,.*,7.*OK"))

        test.log.step("5. Check the impact on AT^SXRAT:")
        test.log.step("5.1 Register to UTRAN: AT+COPS= <mode>,<format>,<opName>,2")
        test.expect(dstl_register_to_umts(test.dut))

        test.log.step("5.2 Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("5.3 Check the value of <Act> parameter: AT^SXRAT?")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 2, 2"))

        test.log.step("5.4 Register to UTRAN: AT+COPS= <mode>,<format>,<opName>,7")
        test.expect(dstl_register_to_lte(test.dut))

        test.log.step("5.5 Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("5.6 Check the value of <Act> parameter: AT^SXRAT?")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 3, 3"))

        test.log.step("5.7 Register to UTRAN: AT+COPS= <mode>,<format>,<opName>,0")
        test.expect(dstl_register_to_gsm(test.dut))

        test.log.step("5.8 Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("5.9 Check the value of <Act> parameter: AT^SXRAT?")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 0, 0"))

        test.log.step("5.10 Register to network without set <AcT>: AT+COPS= <mode>,<format>,<opName>")
        test.expect(test.dut.at1.send_and_verify("at+cops=1,2,{}".format(mcc_mnc), ".*OK.*"))

        test.log.step("5.11 Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("5.12 Check the value of <Act> parameter: AT^SXRAT?")
        if test.dut.project.upper() == "VIPER":
            test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 0, 0.*"))
        else:
            test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 6,.*[023],.*[023].*"))

        test.log.step("5.13 Execute AT^SXRAT write command: eg. AT^SXRAT=3")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=3", ".*OK"))

        test.log.step("5.11 Restart module")
        test.expect(test.dut.dstl_restart())

        test.log.step("5.12 Check the value of <Act> parameter: AT^SXRAT?")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*\^SXRAT: 3, 3"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
