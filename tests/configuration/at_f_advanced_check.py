#responsible: yi.guo@thalesgroup.com
#location: Beijing
#TC0091775.001 - TpAtAndFAdvanced

import unicorn
import random

from core.basetest import BaseTest

from dstl.auxiliary import restart_module
from dstl.network_service import register_to_network
from dstl.auxiliary import init

class TpAtAndFAdvanced(BaseTest):

    def setup(test):
        test.dut.dstl_detect()
        test.log.info("1. Restore to default configurations ")
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*"))
        test.log.info("*******************************************************************\n\r")

        test.log.info("2. Enable SIM PIN lock before testing  ")

        test.expect(test.dut.at1.send_and_verify(r'AT+CLCK="SC",1,"{}"'.format(test.dut.sim.pin1), ".*(OK|ERROR).*"))
        test.dut.dstl_restart()
        # test.device.dstl_restart()

        test.sleep(2)
        test.log.info("*******************************************************************\n\r")
        pass

    def run(test):
        if ("ALAS5" in test.dut.product or  test.dut.project == 'VIPER'):
            test.expect(test.dut.dstl_enter_pin())
            test.log.step("1. Display current configuration AT&V ")
            test.expect(test.dut.at1.send_and_verify("AT&V", "OK", timeout=10))
            test.log.info("*******************************************************************\n\r")

            test.log.step("2. Set non-default values ")
            test.expect(test.dut.at1.send_and_verify("AT&C0", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT&D0", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT&S1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CEREG=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=1,1,1,1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGREG=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CLIR=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CMGF=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+COPS=0,1", ".*OK.*", timeout=10))
            if (test.dut.project == 'VIPER'):
                test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"EN\"", ".*OK.*", timeout=10))
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CPBS=\"ME\"", ".*OK.*", timeout=10))
                test.expect(test.dut.at1.send_and_verify("AT+CR=1", ".*OK.*", timeout=10)) #
            test.expect(test.dut.at1.send_and_verify("AT+CRC=1", ".*OK.*", timeout=10)) #
            test.expect(test.dut.at1.send_and_verify("AT+CREG=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB=1,\"\",\"1\"", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCS=\"UCS2\"", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSDH=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=17,166,1,1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP=255", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSMS=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CNMI=1,1,2,1,1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSSN=1,1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZR=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZU=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CUSD=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+ICF=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+VTD=2", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("ATS0=005", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("ATX1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SCKS=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SCTM=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SLCC=1", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA=0", ".*OK.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SSET=1", ".*OK.*", timeout=10))
            test.dut.at1.send("ATV0", timeout=2)
            test.sleep(2)
            test.dut.at1.send("ATQ1", timeout=2)
            test.sleep(2)
            test.dut.at1.send("ATE0", timeout=2)
            test.sleep(2)
            test.log.info("*******************************************************************\n\r")

            test.log.step("3. Display and check current configuration AT&V")
            if (test.dut.project == 'VIPER'):
                test.expect(
                    test.dut.at1.send_and_verify("AT&V", ".*E0 Q1 V0 X1 &C0 &D0 &S1 .*Q3.*S0:005.*[+]CRC: 1.*"
                                                         "[+]CMGF: 1.*[+]CSDH: 1.*[+]CNMI: 1,1,2,1,1.*[+]CMEE: 1.*"
                                                         "[+]CSMS: 1.*SLCC: 1.*SCKS: 1.*SSET: 1.*[+]CREG: 1.*"
                                                         "[+]CLIP: 1.*[+]COPS: 0,1.*", timeout=10))
            else:
                test.expect(test.dut.at1.send_and_verify("AT&V", ".*E0 Q1 V0 X1 &C0 &D0 &S1.*S0:005.*[+]CR: 1.*[+]CRC: 1.*"
                                                             "[+]CMGF: 1.*[+]CSDH: 1.*[+]CNMI: 1,1,2,1,1.*[+]CMEE: 1.*"
                                                             "[+]CSMS: 1.*SLCC: 1.*SCKS: 1.*SSET: 1.*[+]CREG: 1.*"
                                                             "[+]CLIP: 1.*[+]COPS: 0,1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*[+]CEREG: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF?", ".*[+]CGPIAF: 1,1,1,1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", ".*[+]CGREG: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CLIR?", ".*[+]CLIR: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB?", ".*[+]CSCB: 1,.*,\"1\".*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCS?", ".*[+]CSCS: \"UCS2\".*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*[+]CSMP: 255,166,1,1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSSN?", ".*[+]CSSN: 1,1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZR?", ".*[+]CTZR: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZU?", ".*[+]CTZU: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CUSD?", ".*[+]CUSD: 1.*", timeout=10))
            if (test.dut.project == 'VIPER'):
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", ".*[+]CPBS: \"EN\".*", timeout=10))
                test.expect(test.dut.at1.send_and_verify("AT+ICF?", ".*[+]ICF: 3.*", timeout=10))
            else:
                test.expect(test.dut.at1.send_and_verify("AT+CPBS?", ".*[+]CPBS: \"ME\".*", timeout=10))
                test.expect(test.dut.at1.send_and_verify("AT+ICF?", ".*[+]ICF: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+VTD?", ".*[+]VTD: 2.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SCTM?", ".*SCTM: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA?", ".*SSDA: 0.*", timeout=10))
            test.log.info("*******************************************************************\n\r")

            test.log.step("4. Reset to default values with AT&F ")
            test.expect(test.dut.at1.send_and_verify("AT&F", "OK", timeout=10))
            test.log.info("*******************************************************************\n\r")

            test.log.step(
                "5. Display current configuration AT&V and check if commands have been reset to default values")
            if (test.dut.project == 'VIPER'):
                test.expect(test.dut.at1.send_and_verify("AT&V", ".*E1 Q0 V1 X0 &C1 &D2 &S0 .*Q3.*S0:000.*[+]CRC: 0.*"
                                                             "[+]CMGF: 0.*[+]CSDH: 0.*[+]CNMI: 0,0,0,0,1.*[+]CMEE: 2.*"
                                                             "[+]CSMS: 0.*SLCC: 0.*SCKS: 0.*SSET: 0.*[+]CREG: 0.*"
                                                             "[+]CLIP: 0.*[+]COPS: 0,0.*", timeout=10))
            else:
                test.expect(test.dut.at1.send_and_verify("AT&V", ".*E1 Q0 V1 X0 &C1 &D2 &S0.*S0:000.*[+]CR: 0.*[+]CRC: 0.*"
                                                             "[+]CMGF: 0.*[+]CSDH: 0.*[+]CNMI: 0,0,0,0,1.*[+]CMEE: 2.*"
                                                             "[+]CSMS: 0.*SLCC: 0.*SCKS: 0.*SSET: 0.*[+]CREG: 0.*"
                                                             "[+]CLIP: 0.*[+]COPS: 0,0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CEREG?", ".*[+]CEREG: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGPIAF?", ".*[+]CGPIAF: 0,0,0,0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CGREG?", ".*[+]CGREG: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CLIR?", ".*[+]CLIR: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CPBS?", ".*[+]CPBS: \"SM\".*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCB?", ".*[+]CSCB: 0,.*,\"\".*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSCS?", ".*[+]CSCS: \"GSM\".*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSMP?", ".*[+]CSMP: 17,167,0,0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CSSN?", ".*[+]CSSN: 0,0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZR?", ".*[+]CTZR: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CTZU?", ".*[+]CTZU: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+CUSD?", ".*[+]CUSD: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+ICF?", ".*[+]ICF: 3.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT+VTD?", ".*[+]VTD: 1.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SCTM?", ".*SCTM: 0.*", timeout=10))
            test.expect(test.dut.at1.send_and_verify("AT^SSDA?", ".*SSDA: 1.*", timeout=10))
            test.log.info("*******************************************************************\n\r")
        else:

            test.expect(test.dut.dstl_enter_pin())
            test.log.info("1. Change some settings to non-default value")
            test.expect(test.dut.at1.send_and_verify(r'AT&C0', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify('AT&D0', r'.*OK.*'))
            test.sleep(2)
            test.expect(test.dut.at1.send_and_verify(r'AT&S1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CGREG=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMEE=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CMGF=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+COPS=2', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CREG=2', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSCS="UCS2"', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSDH=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSMP=21,169,1,1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSMS=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CTZU=1', r'.*OK.*'))

            test.expect(test.dut.at1.send_and_verify(r'ATX1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCKS=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCTM=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SSET=1', r'.*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SLED=1', r'.*OK.*'))

            if (test.dut.project == 'VIPER'):
                test.expect(test.dut.at1.send_and_verify(r'AT^SLCC ', r'.*OK.*')) # ; releated to call, Serval doesn't support it
                test.expect(test.dut.at1.send_and_verify(r'AT\\Q', r'.*OK.*')) #;Serval fix this value to 3
                test.expect(test.dut.at1.send_and_verify(r'AT+CUSD  ', r'.*OK.*'))# ; releated to call, Serval doesn't support it
                test.expect(test.dut.at1.send_and_verify(r'ATS10', r'.*OK.*')) #;Serval doesn't support
                test.expect(test.dut.at1.send_and_verify(r'ATS3', r'.*OK.*'))
                test.expect(test.dut.at1.send_and_verify(r'ATS4', r'.*OK.*'))
                test.expect(test.dut.at1.send_and_verify(r'ATS5', r'.*OK.*'))
                test.expect(test.dut.at1.send_and_verify(r'ATS6', r'.*OK.*')) #;Serval doesn't support
                test.expect(test.dut.at1.send_and_verify(r'ATS8', r'.*OK.*')) #;Serval doesn't support
                test.expect(test.dut.at1.send_and_verify(r'AT+CGSMS=3', r'.*OK.*'))# Restore to NV, and not be restore by AT&F
                test.expect(test.dut.at1.send_and_verify(r'AT+CSSN', r'.*OK.*')) #; releated to call, Serval doesn't support it
                test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) #;Not support yet
                test.expect(test.dut.at1.send_and_verify(r'AT+CPBS', r'.*OK.*')) #; releated to PB, Serval doesn't support it
                test.expect(test.dut.at1.send_and_verify(r'AT+CNMI', r'.*OK.*')) #;Not support yet
                test.expect(test.dut.at1.send_and_verify(r'AT+CLIP', r'.*OK.*')) #; releated to call, Serval doesn't support it
                test.expect(test.dut.at1.send_and_verify('ATS0=100', r'.*OK.*'))

            test.expect(
                test.dut.at1.send_and_verify(r'AT&V',
                                             '.*X1[\s\S]*\&C0[\s\S]*\&D0[\s\S]*\&S1[\s\S]*CMGF: 1[\s\S]*CSDH: 1[\s\S]*CMEE: 1[\s\S]*CSMS: 1[\s\S]*SSET: 1[\s\S]*CREG: 2[\s\S]*SLED: 1[\s\S]*OK.*'))

            test.log.info(test.dut.at1.last_response)

            test.expect(test.dut.at1.send_and_verify(r'AT+CGREG?', r'.*\+CGREG: 1[\S\s]*OK.*'))
            #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI?', r'.*OK.*'));Not support yet
            #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
            test.expect(test.dut.at1.send_and_verify(r'AT+CSCS?', r'.*\+CSCS: "UCS2"[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CTZU?', r'.*\+CTZU: 1[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCKS?', r'.*\^SCKS: 1[\s\S]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCTM?', '.*\^SCTM: 1[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSMP?', '.*\+CSMP: 21,169,1,1[\S\s]*OK.*'))

            test.log.info("2. test: Check AT&F Execute Command ")
            # test.expect(test.dut.at1.send_and_verify(r'AT^SCFG=?', '.*SCFG: \"MEopMode/PwrSave\".*'))
            test.expect(test.dut.at1.send_and_verify(r'AT&F', '.*OK.*'))
            test.log.info("*******************************************************************\n\r")

            test.log.info("3. test: Check if settings are restored to default value")
            test.expect(
                test.dut.at1.send_and_verify(r'AT&V',
                                             '.*X0[\s\S]*\&C1[\s\S]*\&D2[\s\S]*\&S0[\s\S]*CMGF: 0[\s\S]*CSDH: 0[\s\S]*CMEE: 2[\s\S]*CSMS: 0[\s\S]*SSET: 0[\s\S]*CREG: 0[\s\S]*SLED: 0[\s\S]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CGREG?', r'.*\+CGREG: 0[\S\s]*OK.*'))
            #test.expect(test.dut.at1.send_and_verify(r'AT+CNMI?', r'.*OK.*'));Not support yet
            #test.expect(test.dut.at1.send_and_verify(r'AT+CSCB', r'.*OK.*')) ;Not support yet
            test.expect(test.dut.at1.send_and_verify(r'AT+CSCS?', r'.*\+CSCS: "GSM"[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CTZU?', r'.*\+CTZU: 0[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCKS?', r'.*\^SCKS: 0[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT^SCTM?', '.*\^SCTM: 0[\S\s]*OK.*'))
            test.expect(test.dut.at1.send_and_verify(r'AT+CSMP?', '.*\+CSMP: 17,167,0,0[\S\s]*OK.*'))


            test.log.info("4. Change some special settings to none default value")
            test.expect(test.dut.at1.send_and_verify(r'ATE0','.*OK.*'))
            test.sleep(2)
            test.dut.at1.send(r'ATQ1')
            test.sleep(2)
            test.dut.at1.send(r'ATV0')
            test.sleep(2)
            test.dut.at1.send(r'AT+ICF=5,1')
            test.sleep(2)

            test.log.info("5. test: Check AT&F Execute Command without PIN ")
            test.dut.at1.send(r'AT&F')
            test.log.info("*******************************************************************\n\r")
            test.sleep(3)

            test.log.info("6. test: Check if settings are restored to default value")
            test.expect(
                test.dut.at1.send_and_verify(r'AT&V',
                                             '.*E1[\s\S]*Q0[\s\S]*V1[\s\S]*OK.*'))
            test.expect(
                test.dut.at1.send_and_verify(r'AT+ICF?',
                                             '.*ICF: 3[\s\S]*OK.*'))

    def cleanup(test):
        # set echo on and Result Code Presentation Mode, if something was brocke before
        test.dut.at1.send_and_verify("ate1")
        test.dut.at1.send_and_verify("atq0")
        pass


if (__name__ == "__main__"):
    unicorn.main()
