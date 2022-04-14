# responsible feng.han@thalesgroup.com
# location Dalian
# TC0108042.001


import unicorn

from core.basetest import BaseTest
from dstl.internet_service.certificates.openssl_certificates import OpenSslCertificates
from dstl.internet_service.configuration.scfg_tcp_tls_version import dstl_set_scfg_tcp_tls_version
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.ip_server.ssl_server import SslServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.hardware.set_real_time_clock import dstl_set_real_time_clock
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """
       TC0108042.001 is intended to test the normal flow of init module according to RQ6000095.001 EBS - AlarmDevice - CheckNetwork
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        main_process(test)

    def cleanup(test):
        pass


def main_process(test):
    test.log.step("1. Application and the module power up & 2. Power on the module via the ignition line.")
    test.dut.at1.send_and_verify("AT^SMSO", ".*OK.*")
    test.dut.devboard.send_and_verify("mc:vbatt=off", ".*OK.*")
    test.sleep(2)
    test.dut.devboard.send_and_verify("mc:vbatt=on", ".*OK.*")
    test.sleep(2)
    test.dut.devboard.send_and_verify("mc:igt=1000", ".*OK.*")
    test.log.step("3. Waits for ^SYSSTART about 30s.")
    test.dut.at1.wait_for('SYSSTART', 60)
    test.log.step("4. Check the AT command communication with the module. Send AT and expect return OK.")
    test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
    test.log.step("5. Set baudrate, IPR is 230400.")
    test.dut.at1.send_and_verify("at+ipr={}".format(230400), "OK", timeout=10)
    test.dut.at1.reconfigure({"baudrate": 230400})
    test.sleep(5)
    test.log.step("6. Set echo, ATE0 and expect return OK.")
    test.expect(test.dut.at1.send_and_verify("ATE0", ".*OK.*"))
    test.log.step("7. Set error messages format with AT+CMEE=1.")
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=1", ".*OK.*"))
    test.log.step("8. Activate registration URCs with AT+CREG=2.")
    test.expect(test.dut.at1.send_and_verify("AT+CREG=2", ".*OK.*"))
    test.log.step("9. Check module model with AT+CGMM.")
    test.expect(test.dut.at1.send_and_verify("AT+CGMM", ".*OK.*"))
    test.log.step("10. Disable AutoAttach")
    test.expect(test.dut.at1.send_and_verify("AT^SCFG=GPRS/AutoAttach,disabled", ".*OK.*"))
    # test.expect(test.dut.at1.send_and_verify('AT+COPS?', ".*OK.*"))
    test.log.step("11. Set serial port hardware flow control with AT\Q3.")
    test.expect(test.dut.at1.send_and_verify("AT\Q3", ".*OK.*"))
    test.log.step("12. Activate radio state URC, AT^SIND=lsta,1,0.")
    test.expect(test.dut.at1.send_and_verify("AT^SIND=lsta,1,0", ".*OK.*"))
    test.log.step("13. Activate service state URC.")
    test.expect(test.dut.at1.send_and_verify("AT^SIND=service,1", ".*OK.*"))
    test.log.step("15. Activate SMS full storage URC")
    test.expect(test.dut.at1.send_and_verify("AT^SIND=smsfull,1", ".*OK.*"))
    test.log.step("16. Activate SIM data activity URC.")
    test.expect(test.dut.at1.send_and_verify("AT^SIND=simdata,1", ".*OK.*"))
    test.log.step("17. Activate extended incoming call indication format.")
    test.expect(test.dut.at1.send_and_verify("AT+CRC=1", ".*OK.*"))
    test.log.step("18. Activate CLIP.")
    test.expect(test.dut.at1.send_and_verify("AT+CLIP=1", ".*OK.*"))
    test.log.step("19. Set RING functionality.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RingOnData","on"', ".*OK.*"))
    test.log.step("20. Set ports (other module option).")
    test.expect(test.dut.at1.send_and_verify("AT^SSET=1", ".*OK.*"))
    test.log.step("21. Disable power save on serial.")
    test.expect(test.dut.at1.send_and_verify("AT^SPOW=1,0,0", ".*OK.*"))
    test.log.step("22. Check module connection.")
    test.expect(test.dut.at1.send_and_verify("AT", ".*OK.*"))
    test.log.step("23. Set clock initial time..")
    test.expect(test.dut.at1.send_and_verify('AT+CCLK="00/01/01,00:00:57"', ".*OK.*"))
    test.log.step("24. Check technology setting..")
    test.expect(test.dut.at1.send_and_verify("AT^SXRAT?", ".*OK.*"))
    test.log.step("25. Set technology according to application setup.")
    # test.expect(test.dut.at1.send_and_verify("AT^SXRAT=1,2", ".*OK.*"))
    test.log.step("26. Set GPIO8 to FNS to control selected SIM interface.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std"', ".*OK.*"))
    test.log.step("27. Activate second SIM interface.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode","1"', ".*OK.*"))
    test.log.step("28. Set dual SIM option.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode/Dreg","on"', ".*OK.*"))
    test.log.step("29. Check enabled SIM.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/CS"', ".*OK.*"))
    test.log.step("30. Check PIN.")
    test.log.step("31. Provide PIN.")
    test.expect(test.dut.dstl_enter_pin())
    test.log.step("32. Verify IMSI of selected SIM.")
    test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
    test.log.step("33. Check registration status.")
    test.sleep(5)
    test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
    test.log.step("34. Check IMSI of selected SIM (bugfix of Esseye SIM with IMSI switcher).")
    test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
    test.log.step("35. Check registration status.")
    test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
    test.log.step("36. Set SMS to PDU mode.")
    test.expect(test.dut.at1.send_and_verify('AT+CMGF=0', ".*OK.*"))
    test.log.step("37. Set SMS display method.")
    test.expect(test.dut.at1.send_and_verify('AT+CNMI=2,1,0,0,1', ".*OK.*"))
    test.log.step("38. Set SMS storage space.")
    test.expect(test.dut.at1.send_and_verify('AT+CPMS="SM","ME","SM"', ".*OK.*"))
    test.log.step("39. Set coding.")
    test.expect(test.dut.at1.send_and_verify('AT+CSCS="GSM"', ".*OK.*"))
    test.log.step("40. Set AT+COPS format.")
    test.expect(test.dut.at1.send_and_verify('AT+COPS=3,0', ".*OK.*"))
    test.log.step("41. Check registration - network.")
    test.expect(test.dut.at1.send_and_verify('AT+COPS?', ".*OK.*"))
    test.log.step("42. Check registration - cell.")
    test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
    test.log.step("43. Set error reporting format.")
    test.expect(test.dut.at1.send_and_verify('AT+CMEE=1', ".*OK.*"))
    test.log.step("44. Activate CLIP.")
    test.expect(test.dut.at1.send_and_verify('AT+CLIP=1', ".*OK.*"))
    test.log.step("45. Check module model.")
    test.expect(test.dut.at1.send_and_verify('AT+CGMM', ".*OK.*"))
    test.log.step("46. Check module clock/time.")
    test.expect(test.dut.at1.send_and_verify('AT+CCLK?', ".*OK.*"))
    test.log.step("47. Check attach.")
    test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
    test.log.step("48. Attach.")
    test.expect(test.dut.at1.send_and_verify('AT+CGATT=1', ".*OK.*"))
    test.sleep(5)
    test.log.step("49. Check attach.")
    test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT+COPS?', ".*OK.*"))
    test.log.step("50. Activate TCP/IP URCs.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","on"', ".*OK.*"))
    test.log.step("51. Set TCP/IP parameters.")
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","3"', ".*OK.*"))
    test.log.step("52-56. Define connection.")
    test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,IPV6', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT+CGDCONT=2,IPV6,"internetipv6"', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SGAUTH=2,1,"gemalto","gemalto"', ".*OK.*"))
    test.log.step("57-59. Define listener to get IP (this is to get IP address of the connection).")
    test.expect(test.dut.at1.send_and_verify('AT^SISS=9,srvType,"Socket"', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=9,alphabet,1', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=9,conId,2', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=9,address,"socktcp://listener:54321"', ".*OK.*"))
    test.log.step("60. Internet Connection Activate.")
    test.expect(test.dut.at1.send_and_verify('AT^SICA=1,2', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SICA?', ".*OK.*"))
    test.log.step("61. Open listener.")
    test.expect(test.dut.at1.send_and_verify('AT^SISO=9', ".*OK.*"))
    test.log.step("62. Check attach.")
    test.expect(test.dut.at1.send_and_verify('AT+CGATT?', ".*OK.*"))
    test.log.step("63. Check connection IP.")
    test.expect(test.dut.at1.send_and_verify('AT^SISO?', ".*OK.*"))
    test.log.step("64. Close listener.")
    test.expect(test.dut.at1.send_and_verify('AT^SISC=9', ".*OK.*"))
    test.log.step("65. Check SIM.")
    test.expect(test.dut.at1.send_and_verify('AT+CRSM=242', ".*OK.*"))
    test.log.step("66. Check for new messages.")
    test.expect(test.dut.at1.send_and_verify('AT+CMGL=4', ".*OK.*"))
    test.log.step("67. Check received and read messages.")
    test.expect(test.dut.at1.send_and_verify('AT+CMGL=1', ".*OK.*", wait_for=".*OK.*"))

    test.log.step("68-72. Define back end server connection.")
    connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
    test.socket = SocketProfile(test.dut, "1", connection_setup_dut.dstl_get_used_cid(), protocol="tcp", host="client",
                                localport=65100)
    test.expect(test.dut.at1.send_and_verify('AT^SISS=1,srvType,Socket', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=1,conId,2', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=1,tcpMR,10', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=1,tcpOT,6000', ".*OK.*"))
    # test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://dev10.aplnet.dynv6.net:6650"', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=1,address,"socktcp://[2001:470:18:36b::2]:50025"', ".*OK.*"))
    test.log.step("73. Open back end server connection")
    test.expect(test.dut.at1.send_and_verify('AT^SISO=1', ".*OK.*", wait_for="^SISW: 1,1"))
    test.log.step("74. Check service status.")
    test.expect(test.dut.at1.send_and_verify('AT^SISI=1', ".*OK.*"))
    test.log.step("75. Check service errors.")
    test.expect(test.dut.at1.send_and_verify('AT^SISE=1', ".*OK.*"))
    test.log.step("76. Check service status.")
    test.expect(test.dut.at1.send_and_verify('AT^SISI=1', ".*OK.*"))
    test.log.step("77. Check send data.")
    test.expect(test.dut.at1.send_and_verify('AT^SISW=1,0', ".*OK.*"))
    test.log.step("78. Send initial report.")
    test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(55))
    test.sleep(10)
    test.log.step("79. Read initial configuration from the server..")
    test.expect(test.dut.at1.send_and_verify('AT^SISR=1,511', ".*OK.*"))
    test.log.step("80. Monitor network status every 30s.")
    test.log.step("81. Monitor SIM status every 30s.")
    test.log.step("82. Check for new messages every 30s.")
    test.log.step("83. Check network signal every 30s.")
    test.log.step("84. Check if no IMEI change (Eseye cards) every 30s.")
    test.log.step("85. Check messages from server every 30s.")
    for i in range(5):
        test.expect(test.dut.at1.send_and_verify('AT+CREG?', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CRSM=242', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CMGL=4', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SMONI', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT+CIMI', ".*OK.*"))
        test.expect(test.socket.dstl_get_service().dstl_send_sisw_command_and_data(511))
        test.expect(test.dut.at1.send_and_verify('AT^SISR=1,511', ".*OK.*"))
        test.sleep(30)
    test.dut.at1.send_and_verify("at+ipr={}".format(115200), "OK", timeout=10)
    test.dut.at1.reconfigure({"baudrate": 115200})
    # start added by yinhw
    test.expect(test.dut.at1.send_and_verify('AT^SISC=1', ".*OK.*"))
    test.expect(test.dut.at1.send_and_verify("AT^SCFG=GPRS/AutoAttach,enabled", ".*OK.*"))
    # end


if __name__ == "__main__":
    unicorn.main()