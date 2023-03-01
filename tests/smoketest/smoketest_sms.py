# author: christian.gosslar@thalesgroup.com
# responsible: christian.gosslar@thalesgroup.com
# location: Berlin
# TC0095332.001
# jira: xxx
# feature: LM0000079.001, LM0000081.001, LM0000083.001, LM0000088.001, LM0000095.001, LM0000096.001,
# LM0000099.001, LM0000101.001, LM0000107.001, LM0000109.001, LM0000110.001, LM0000788.001, LM0001223.001,
# LM0001229.001, LM0001230.001,  LM0001231.001, LM0001233.001, LM0001234.001, LM0001238.001, LM0001240.001,
# LM0001241.001, LM0001242.001, LM0001501.001, LM0001935.001, LM0002383.001, LM0002384.001, LM0003219.003,
# LM0004451.003, LM0004455.002, LM0004455.003, LM0004455.005, LM0007422.001, LM0007425.001

import unicorn
import time
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.collect_module_infos import dstl_collect_module_info
from dstl.identification.get_revision_number import dstl_get_revision_number
from dstl.identification.get_imei import dstl_get_imei
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.check_c_revision_number import dstl_check_c_revision_number
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.sms.delete_sms import dstl_delete_all_sms_messages
from dstl.sms.sms_memory_capacity import dstl_get_sms_memory_capacity
from dstl.sms.write_sms_to_memory import dstl_write_sms_to_memory
from dstl.sms.send_sms_message import dstl_send_sms_message_from_memory

import re


class SmoketestSms(BaseTest):

    def setup(test):
        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')
        test.log.com('***** Collect some Module Infos *****')
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_get_bootloader()
        test.dut.dstl_check_c_revision_number()
        pass

    def run(test):
        """
        Intention:
        Simple check of the ati command with all parameters
        """

        str_sms_class1 = "00F10B"
        str_sms_109 = "6CC474795E9E83D2733A889C2E83A6CD29A89DA683C86537081A9687DB657A59EE068DDDED740FC692B1602C192B160259D36536680A0FCFE7207139DD0651CB737AD9ED0255DD64103A5D9683D6EF76BBEC06ADCB697719546DB3C3757AD905"
        withsmgo = False
        withoutsmgo = True
        smsmem3x = '\"ME\",\"ME\",\"ME\"'

        if (not test.dut.sim.pdu) or (not test.dut.sim.nat_voice_nr) or (not test.dut.sim.sca_int):
            test.log.error("some SIM-values are empty - ABORT!")
            test.log.error("Please check <sim.pdu> value: >" + str(test.dut.sim.pdu) + "<")
            test.log.error("Please check <sim.nat_voice_nr> value: >" + str(test.dut.sim.nat_voice_nr) + "<")
            test.log.error("Please check <sim.sca_int> value: >" + str(test.dut.sim.sca_int) + "<")
            test.expect(False, critical=True)

        # ==============================================================
        test.log.step('Step 0.1: Set Project Parameter, enter PIN')
        test.expect(test.dut.dstl_enter_pin())
        test.sleep(2)
        # ==============================================================
        if re.search(test.dut.platform, 'QCT'):
            withsmgo = False
            if re.search(test.dut.product, 'PLS-X|PLS-V'):
                test.dut.at1.send_and_verify('at^scfg=\"SMS/Format\",\"3GPP\",\"3GPP\"')
            # withoutsmgo = False
        if re.search(test.dut.project, 'ODESSA'):
            withsmgo = False
            smsmem3x = '\"ME\",\"ME\",\"ME\"'
        if re.search(test.dut.project, 'DAHLIA'):
            withsmgo = False
            smsmem3x = '\"ME\",\"ME\",\"ME\"'
            if re.search(test.dut.product, 'ELS31-V|ELS51-V'):
                test.dut.at1.send_and_verify("at+csmp=,,,9", ".*OK.*",15)
                test.dut.at1.send_and_verify("AT^SCFG=\"Sms/Format\",\"3GPP\",\"3GPP2\"", ".*OK.*", 15)
        if re.search(test.dut.project, 'COUGAR'):
            withsmgo = False
            smsmem3x = '\"ME\",\"ME\",\"ME\"'
        if re.search(test.dut.project, 'JAKARTA'):
            smsmem3x = '\"ME\",\"ME\",\"ME\"'
            withsmgo = False
        #   withoutsmgo = !withsmgo;

        # ==============================================================
        test.log.step('Step 0.2: configure Tln1 and Tln2 for SMS-actions')
        test.expect(test.dut.at1.send_and_verify("at+CGSMS?", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("at+CGSMS=1", ".*OK.*"))
        if re.search(test.dut.project, 'IRIS|QUINN|RHEA|URANUS|FLORENCE|WIRTANEN|HALIFAX|JAKARTA|BOXWOOD|GINGER|MIAMI|ODESSA|ZURICH|FOXTAIL|DAHLIA|COUGAR|BOBCAT|VIPER|SERVAL'):
            test.expect(test.dut.at1.send_and_verify("at+cnmi?", "OK"))
            ret = test.expect(test.dut.at1.send_and_verify("at+cnmi=2,1", "OK"))
            if not ret:
                test.log.error("if previous step failed, please check setting on all other interfaces. CNMI can not be actived if it is already done on other IF")

            test.expect(test.dut.at1.send_and_verify("at+cnmi?", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+csms?", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+csms=0", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+csms?", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+csca=\"" + test.dut.sim.sca_int + "\"", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+cpms=" + smsmem3x, "OK"))
        else:
            test.expect(test.dut.at1.send_and_verify("at+cnmi=3,1", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+csca=\"" + test.dut.sim.sca_int + "\"", "OK"))
            test.expect(test.dut.at1.send_and_verify("at+cpms=\"MT\",\"MT\",\"MT\"", "OK"))
            if withsmgo:
                test.expect(test.dut.at1.send_and_verify("at^SMGO?", ".*0,0.*OK.*"))
                test.expect(test.dut.at1.send_and_verify("at^SMGO=1", ".*OK.*"))
                test.expect(test.dut.at1.send_and_verify("at^SMGO?", ".*1,0.*OK.*"))

        numbersOfSmsInt = int(test.dut.dstl_get_sms_memory_capacity(1))

        if withoutsmgo:
            test.log.info("use only 5 SMS to check send+receive function and do not fill up")
            test.log.info("all possible SMS-memory entries - this may take a lot of time")
            if (numbersOfSmsInt >4):
                numbersOfSmsInt = 5

        test.expect(test.dut.at1.send_and_verify("AT+CSCA=\"{}\"".format(test.dut.sim.sca_int), "OK"))
        test.dut.at1.send_and_verify("at+CPMS?", "OK")

        test.log.step("Step 1.0: ***************_ SMS send Text Mode Start _*************** ")
        # ==============================================================
        test.log.step('Step 1.1: remove all SMS')
        if re.search(test.dut.project, 'TIGER'):
            test.expect(test.dut.at1.send_and_verify("at+cmgd=1,3", ".*OK.*"))
        else:
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('Step 1.2: fill up SMS memory to ' + str(numbersOfSmsInt) + ' Number of SMS')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cmgf=1", "OK"))
        n = 1
        # sms_post_text = ' - now lot much more text to reach 160 characters in summary to see if all characters are echooooooooed correct'
        sms_post_text = ' - nowend'
        while n < numbersOfSmsInt+1:
            test.expect(test.dut.at1.send_and_verify("at+cmgw=\"" + str(test.dut.sim.nat_voice_nr) + "\"", ">"))

            ret = test.expect(test.dut.at1.send_and_verify("Hello Module this Test SMS " + str(n) + " from " + str(numbersOfSmsInt)
                                                    + sms_post_text
                                                    , ".*Hello Module this Test SMS \d from \d" + sms_post_text
                                                    + ".*\+CMGW: \d.*OK.*"
                                                    , end="\x1a", append=True))
            # check if ECHO of SMS msg was correct - issue found in Serval03/04: SRV03-1947
            test.sleep(1)

            lresp = test.dut.at1.last_response
            if not ret:
                if '+CMGW: ' in lresp:
                    if sms_post_text not in lresp:
                        test.log.error("ECHO of SMS cmd is not correct, maybe issue SRV03-1947 found!")
                        test.log.error("ECHO was:\n" + lresp)

            n += 1
        test.expect(test.dut.at1.send_and_verify("at+cmgl=\"all\"", "OK"))

        test.log.step('Step 1.3: Send ' + str(numbersOfSmsInt) + ' stored Text-SMS and receive it')
        # ==============================================================
        n = 0
        while n < numbersOfSmsInt:
            test.log.step('Step 1.3x: Send ' + str(n) + ' Text SMS and receive it')
            if re.search(test.dut.project, 'TIGER'):
                index_start = 1 + n
                test.expect(test.dut.at1.send_and_verify("at+cmgl=\"all\"", "OK"))
            else:
                index_start = 0 + n

            ret = test.expect(test.dut.at1.send_and_verify("at+cmss=" + str(index_start), "OK"))
            if "+CMS ERROR: unknown error" in test.dut.at1.last_response:
                # seems we found SRV03-1966. Let's try if it works a second later again.
                ret = test.expect(test.dut.at1.send_and_verify("at+cmss=" + str(index_start), "OK"))
                if ret:
                    test.log.error("above, SRV03-1966 was found: repeating same cmd again was successful now!")

            if "+CMSS: " in test.dut.at1.last_response:
                test.log.info('SMS was send')
            else:
                test.log.info('SMS send URC was NOT received')
                test.expect(False)

            if re.search(test.dut.project, 'TIGER'):
                # no URC wait one minute and read all SMS
                test.sleep(30)
                test.expect(test.dut.at1.send_and_verify("at+cmgl=\"all\"", "OK"))
                res = test.dut.at1.last_response
                if "REC UNREAD" in res:
                    test.log.info('TIGER: SMS was received')
                else:
                    test.log.com('TIGER: SMS was NOT received')
                    test.expect(False)
            else:
                test.expect(test.dut.at1.verify_or_wait_for("CMTI: ", timeout=30))
            n += 1

        test.log.step('Step 1.4: Send additional Text SMS ' + str(n) + ' with +CMGS and receive it')
        # ==============================================================

        test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.nat_voice_nr), ".*>.*", wait_for=".*>.*"))
        test.expect(test.dut.at1.send_and_verify("Hello Module this is additional CMGS Test SMS "
                                                    + str(n+1) + sms_post_text, end="\u001A"))
        ret = test.dut.at1.verify_or_wait_for(".*Hello Module this is additional CMGS Test SMS "
                                                    + str(n+1) + sms_post_text + ".*\+CMGS:.*")
        time.sleep(2)
        if not ret:
            lresp = test.dut.at1.last_response
            lresp2 = test.dut.at1.read()

            if "+CMS ERROR: unknown error" in lresp or "+CMS ERROR: unknown error" in lresp2:
                # seems we found SRV03-1966. Let's try if it works a second later again.

                test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.nat_voice_nr), ".*>.*",
                                                         wait_for=".*>.*"))
                test.expect(test.dut.at1.send_and_verify("Hello Module this is additional CMGS Test SMS "
                                                         + str(n + 1) + sms_post_text, end="\u001A"))
                ret = test.dut.at1.verify_or_wait_for(".*Hello Module this is additional CMGS Test SMS "
                                                      + str(n + 1) + sms_post_text + ".*\+CMGS:.*")
                if ret:
                    test.log.error("above, SRV03-1966 was found: repeating same cmd again was successful now!")
                    lresp = test.dut.at1.last_response

        # check if ECHO of SMS msg was correct - issue found in Serval03/04: SRV03-1947
        if not ret:
            if '+CMGS: ' in lresp:
                if sms_post_text not in lresp:
                    test.log.error("ECHO of SMS cmd is not correct, maybe issue SRV03-1947 found!")
                    test.log.error("ECHO was:\n" + lresp)

        time.sleep(5)

        test.log.step('Step 1.5: List all SMS and check the Number of SMS')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify('at+cmgl="all"', 'OK'))
        if test.dut.at1.last_response.count("CMGL: ") == (numbersOfSmsInt*2 + 1):
            test.expect(True)
            test.log.info("Number of SMS is correct: " + str(numbersOfSmsInt*2 + 1))
        else:
            test.expect(False)
            test.log.info("Number of SMS entries wrong: " + str(test.dut.at1.last_response.count("CMGL: "))
                          + " requested count is: " + str(numbersOfSmsInt*2 + 1))

        test.log.step('Step 1.6: remove all SMS')
        # ==============================================================
        if re.search(test.dut.project, 'TIGER'):
            test.expect(test.dut.at1.send_and_verify("at+cmgd=1,3", ".*OK.*"))
        else:
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('Step 2.0: Send ' + str(numbersOfSmsInt) + ' PDU-SMS and receive it')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cmgf=0", "OK"))
        n = 1
        while n < numbersOfSmsInt+1:
            test.log.step('Step 2.1x: Send ' + str(n) + ' PDU SMS and receive it')
            SCA_PDU = test.dut.sim.sca_pdu
            pduString = SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
            test.expect(test.dut.at1.send_and_verify("at+cmgs=109", ">"))
            ret = test.expect(test.dut.at1.send_and_verify(pduString
                                                 # check also full ECHO:
                                                 , SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
                                                 + ".*OK.*", end="\x1a"))

            lresp = test.dut.at1.last_response
            lresp2 = test.dut.at1.read()

            if "+CMS ERROR: unknown error" in lresp or "+CMS ERROR: unknown error" in lresp2:
                # seems we found SRV03-1966. Let's try if it works a second later again.
                test.log.error("above, SRV03-1966 was found: try to repeat same cmd again:")
                test.expect(test.dut.at1.send_and_verify("at+cmgs=109", ">"))
                ret = test.expect(test.dut.at1.send_and_verify(pduString
                                                   # check also full ECHO:
                                                   , SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
                                                   + ".*OK.*", end="\x1a"))
                lresp = test.dut.at1.last_response


            # check if ECHO of SMS msg was correct - issue found in Serval03/04: SRV03-1947
            if not ret:
                if '+CMGS: ' in lresp:
                    if sms_post_text not in lresp:
                        test.log.error("ECHO of SMS cmd is not correct, maybe issue SRV03-1947 found!")
                        test.log.error("ECHO was:\n" + lresp)
                    else:
                        test.log.info('PDU SMS send URC was NOT received')
                        test.expect(False)
            else:
                test.log.info('PDU SMS was sent')

            if re.search(test.dut.project, 'TIGER'):
                # no URC wait one minute and read all SMS
                test.sleep(30)
                test.expect(test.dut.at1.send_and_verify("at+cmgl=0", "OK"))
                res = test.dut.at1.last_response
                if "+CMGL: " in res:
                    # SIM lock was disabled, activate SIM PIN
                    test.log.info('TIGER: SMS was received')
                else:
                    test.log.com('TIGER: SMS was NOT received')
                    test.expect(False)
            else:
                test.expect(test.dut.at1.verify_or_wait_for("CMTI: ", timeout=30))
            n += 1
        # ==============================================================

        test.log.step('Step 2.2: Store PDU SMS ' + str(n) + ' with +CMGW')
        # ==============================================================
        SCA_PDU = test.dut.sim.sca_pdu
        pduString = SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
        test.expect(test.dut.at1.send_and_verify("at+cmgw=109", ">"))
        ret = test.expect(test.dut.at1.send_and_verify(pduString
                                             # check also full ECHO:
                                             , SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
                                             + ".*OK.*", end="\x1a"))
        # test.expect(test.dut.at1.send_and_verify("\x1a", end=""))

        if not ret:
            lresp = test.dut.at1.last_response
            lresp2 = test.dut.at1.read()

            if "+CMS ERROR: unknown error" in lresp or "+CMS ERROR: unknown error" in lresp2:
                # seems we found SRV03-1966. Let's try if it works a second later again.
                test.expect(test.dut.at1.send_and_verify("at+cmgw=109", ">"))
                ret = test.expect(test.dut.at1.send_and_verify(pduString
                                               # check also full ECHO:
                                               , SCA_PDU + "1100" + test.dut.sim.pdu + str_sms_class1 + str_sms_109
                                               + ".*OK.*", end="\x1a"))
                lresp = test.dut.at1.last_response

        # check if ECHO of SMS msg was correct - issue found in Serval03/04: SRV03-1947
        if not ret:
            if '+CMGW: ' in lresp:
                if sms_post_text not in lresp:
                    test.log.error("ECHO of SMS cmd is not correct, maybe issue SRV03-1947 found!")
                    test.log.error("ECHO was:\n" + lresp)
            else:
                test.log.info('PDU SMS was NOT stored')
                test.expect(False)

        test.log.step('Step 2.3: List all PDU SMS')
        # ==============================================================
        test.expect(test.dut.at1.send_and_verify("at+cmgl=4", "OK"))
        if test.dut.at1.last_response.count("CMGL: ") == numbersOfSmsInt + 1:
            test.expect(True)
            test.log.info("Number of SMS is correct: " + str(numbersOfSmsInt))
        else:
            test.expect(False)
            test.log.info("Number of SMS entries wrong: " + str(test.dut.at1.last_response.count("CMGL: ")) +
                          " requested count is: " + str(numbersOfSmsInt))

        test.log.step('Step 2.4: remove all SMS')
        # ==============================================================
        if re.search(test.dut.project, 'TIGER'):
            test.expect(test.dut.at1.send_and_verify("at+cmgd=1,3", ".*OK.*"))
        else:
            test.expect(dstl_delete_all_sms_messages(test.dut))

        test.log.step('Step end')

    def cleanup(test):
        """Cleanup method.
        """

        test.log.com(' ')
        test.log.com('****  log dir: ' + test.workspace + ' ****')

        test.log.step('cleanup: remove all SMS')
        if re.search(test.dut.project, 'TIGER'):
            test.dut.at1.send_and_verify("at+cmgd=1,3", ".*OK.*")
        else:
            dstl_delete_all_sms_messages(test.dut)

        test.log.com(' ')
        test.log.com('**** Testcase: ' + test.test_file + ' - END ****')
        pass


if "__main__" == __name__:
    unicorn.main()
