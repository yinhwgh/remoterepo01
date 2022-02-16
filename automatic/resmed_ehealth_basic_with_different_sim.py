# responsible hongwei.yin@thalesgroup.com
# location Dalian
# TC0107811.001

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.generate_data import dstl_generate_data
import resmed_ehealth_initmodule_normal_flow
import resmed_ehealth_sendhealthdata_normal_flow


class Test(BaseTest):
    """
       TC0107811.001 - Resmed_eHealth_basic_with_different_SIM
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()
        test.dut.dstl_enter_pin()
        test.dut.devboard.send_and_verify('mc:urc=off', "OK")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_tls_version(test.dut, "MIN", "MAX"))
        test.expect(resmed_ehealth_initmodule_normal_flow.uc_init_module(test, 1))

    def run(test):
        test.expect(resmed_ehealth_sendhealthdata_normal_flow.NF_pre_config(test))

        test.log.step("1. Power on the module by MC test board.")
        test.dut.devboard.send('MC:VBATT=OFF')
        test.sleep(1)
        test.dut.devboard.send('MC:VBATT=ON')
        test.expect(test.dut.devboard.send_and_verify("MC:IGT=1000"))

        test.log.step("2. Wait the '^SYSSTART' URC.")
        test.expect(test.dut.at1.wait_for('.*SYSSTART.*'))

        test.log.step("3. Keep checking the connection state via MC test port "
                      "and check the AT command communication with the module.")
        test.expect(test.dut.devboard.send_and_verify("MC: ASC0"))
        test.expect(test.dut.at1.send_and_verify("AT"))

        test.log.step("4. Request module version.")
        test.expect(test.dut.at1.send_and_verify("ATE0"))
        test.expect(test.dut.at1.send_and_verify("AT+CGMI"))
        test.expect(test.dut.at1.send_and_verify("AT+GMM"))
        test.expect(test.dut.at1.send_and_verify("ATI1"))

        test.log.step("5. Enable HW flow control.")
        test.expect(test.dut.at1.send_and_verify("AT\Q3"))

        test.log.step("6. Enable error result code.")
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=1"))

        test.log.step("7. Automatic response to Network requests.")
        test.expect(test.dut.at1.send_and_verify("ATS0=0"))

        test.log.step("8. Request IMEI.")
        test.expect(test.dut.at1.send_and_verify("AT+CGSN"))

        test.log.step("9. Enable full function level.")
        test.expect(test.dut.at1.send_and_verify("AT+CFUN=1"))

        test.log.step("10. Request USIM ID.")
        test.expect(test.dut.at1.send_and_verify("AT+CCID"))

        test.log.step("11. Forbid cell broadcast messages.")
        test.expect(test.dut.at1.send_and_verify('AT+CSCB=1,"",""'))

        test.log.step("12. Request model identification.")
        test.expect(test.dut.at1.send_and_verify("AT+CGMM"))

        test.log.step("13. Enabled Fota feature.")
        pass # no at command

        test.log.step("14. Request SIM PIN status.")
        test.expect(test.dut.at1.send_and_verify("AT+CPIN?"))

        test.log.step("15. Request International Mobile Subscriber Identity.")
        test.expect(test.dut.at1.send_and_verify("AT+CIMI"))

        test.log.step("16. Enable extended registration URC.")
        test.expect(test.dut.at1.send_and_verify("AT+CREG=2"))

        test.log.step("17. Enable packet domain event reporting.")
        test.expect(test.dut.at1.send_and_verify("AT+CGEREP=2"))

        test.log.step("18. Enable auto attach.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"'))

        test.log.step("19. Fast Shutdown can also be triggered by GPIO4.")
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FSR","std"'))

        test.log.step("20. Indicate Fast Shutdown mode.")
        pass # AT^SCFG="MEShutdown/Fso","1" is not supported

        test.log.step("21. Select Radio Access Technologies.")
        test.expect(test.dut.at1.send_and_verify("AT^SXRAT=5,3"))  # "AT^SXRAT=4,3" is not supported

        test.log.step("22. Select APN.")
        test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","cmnet"'))
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', 'OK\r\n', handle_errors=True), critical=True)

        test.log.step("23. Set operator format.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=3,2"))

        test.log.step("24. Configure SMS format.")
        test.expect(test.dut.at1.send_and_verify("AT+CMGF=1"))

        test.log.step("25. Enable SMS URC.")
        test.expect(test.dut.at1.send_and_verify("AT+CNMI=2,1"))

        test.log.step("26. Configure detailed header information.")
        test.expect(test.dut.at1.send_and_verify("AT+CSDH=1"))

        test.log.step("27. List SMS messages from preferred store.")
        test.expect(test.dut.at1.send_and_verify('AT+CMGL="ALL"'))

        test.log.step("28. Read Operator Name.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS?"))

        test.log.step("29. Configures the IP service connection profile 0.")
        pass # AT^SICS=0,"conType","GPRS0" is not supported

        test.log.step("30. A private APN.")
        pass # AT^SICS=0,"apn","internet4g.gdsp" is not supported

        test.log.step("31. An inactive timeout set to 90 seconds.")
        pass  # AT^SICS=0,"inactTO","90" is not supported

        test.log.step("32. configures server type.")
        test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"srvType","socket"'))

        test.log.step("33. configures conId.")
        test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"conId","1"'))

        test.log.step("34. secure TCP socket in non-transparent mode.")
        test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"address","socktcps://114.55.6.216:50433"'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"secopt","1"'))
        test.expect(test.dut.at1.send_and_verify('AT^SISS=0,"tcpOT","90"'))

        test.log.step("35. opens the internet service, waits for SISW URC.")
        test.expect(test.dut.at1.send_and_verify("AT^SISO=0", 'SISW', wait_for='SISW', handle_errors=True), critical=True)
        test.expect(test.dut.at1.send_and_verify("AT^SISO=0,1"))

        test.log.step("36. Check signal quality.")
        test.expect(test.dut.at1.send_and_verify("AT+CSQ"))

        test.log.step("37. Monitoring Serving Cell.")
        test.expect(test.dut.at1.send_and_verify("AT^SMONI"))

        test.log.step("38. sends health data (~100k-1MByte) to the receiving server in 1500Bytes chunks.")
        test.expect(test.dut.at1.send_and_verify("AT^SISW=0,1500", "^SISW: 0,1500,0", wait_for="SISW", handle_errors=True))

        test.log.step("39. sends Hash file to the module from server and wait for SISR URC.")
        partial_send_data = dstl_generate_data(1500)
        test.expect(test.dut.at1.send_and_verify(partial_send_data, 'OK\r\n', handle_errors=True))

        test.log.step("40. checks the connection status.")
        test.expect(test.dut.at1.send_and_verify("AT^SISI=0"))

        test.log.step("41. Reads the file which is about the size of 100k-2Mbyte in 1500 Byte chunks.")
        test.expect(test.dut.at1.send_and_verify("AT^SISR=0,1500", wait_after_send=2))

        test.log.step("42. checks the connection status.")
        test.expect(test.dut.at1.send_and_verify("AT^SISI=0"))

        test.log.step("43. closes the internet service profile (ID 0).")
        test.expect(test.dut.at1.send_and_verify("AT^SISC=0"))

        test.log.step("44. Configure SNFOTA feature (URL, CID, hash).")     # 依据实际情况修改
        # test.expect(test.dut.at1.send_and_verify('at^snfota="url","http://114.55.6.216:10080/pls83-w-rev01.004_arn01.000.02_viper_100_112_to_rev01.005_arn01.000.01_viper_100_118-sign01dev.usf"'))
        # test.expect(test.dut.at1.send_and_verify('at^snfota="conid",1'))
        # test.expect(test.dut.at1.send_and_verify('at^snfota="CRC","5f63ad89a0ae757d541b9a09ba606d769ddef11b63300d190262e906cfff4828"'))

        test.log.step("45. Trigger the download.")
        # test.expect(test.dut.at1.send_and_verify('at^snfota="act",2'))

        test.log.step("46. Monitor progress report.")
        # test.expect(test.dut.at1.wait_for("^SNFOTA:act,2,0,100", timeout=100))

        test.log.step("47. Trigger the firmware swap process.")
        # test.expect(test.dut.at1.send_and_verify("AT^SFDL=2"))

        test.log.step("48. Wait for PBREADY.")

        test.log.step("49. Check the module's SW version.")
        test.expect(test.dut.at1.send_and_verify("AT^CICRET=SWN"))

        try:
            if not test.ssl_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        test.log.step("Remove certificates from module.")
        try:
            test.certificates.dstl_delete_openssl_certificates()
            if not test.expect(test.certificates.dstl_count_uploaded_certificates() == 0,
                               msg="Problem with deleting certificates from module"):
                test.certificates.dstl_delete_all_uploaded_certificates()
        except AttributeError:
            test.log.error("Certificate object was not created.")

    def cleanup(test):
        pass



if __name__ == "__main__":
    unicorn.main()
