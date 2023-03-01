# responsible: hongwei.yin@thalesgroup.com
# location: Dalian


import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei

imei = ''


class Test(BaseTest):
    """
       check nv values if remain after reboot .
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.devboard.send_and_verify("mc:urc=off", ".*OK.*", wait_for=".*OK.*")
        test.dut.devboard.send_and_verify("mc:urc=pwrind", ".*OK.*", wait_for=".*OK.*")
        test.dut.at1.send_and_verify('AT+CMEE=2')
        test.dut.at1.send_and_verify('AT^SSET=1')
        test.dut.at1.send_and_verify('AT&W')
        test.dut.at1.send_and_verify('AT+CPIN=1234')
        test.dut.at1.send_and_verify('AT+CLCK="SC",0,1234')
        global imei
        imei = test.dut.dstl_get_imei()
        test.log.info(f"This module's imei is {imei}.")
        test.sleep(2)

    def run(test):
        change_nv(test)
        test.dut.at1.send_and_verify('AT+CFUN=1,1')
        test.dut.at1.wait_for('.*SYSSTART.*')
        check_nv(test)
        reset_nv(test)

    def cleanup(test):
        test.dut.devboard.send_and_verify("mc:urc=common", ".*OK.*", wait_for=".*OK.*")


def change_nv(test):
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","off"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","asc0"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","0"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","1"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","+CMT"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","RING"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","60"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","off"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","disabled"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","0"')

    # init
    test.dut.at1.send_and_verify('AT', 'OK')
    test.dut.at1.send_and_verify('ATE0', 'OK')
    test.dut.at1.send_and_verify('AT+CGMI', 'OK')
    test.dut.at1.send_and_verify('AT+GMM', 'OK')
    test.dut.at1.send_and_verify('ATI1', 'OK')
    test.dut.at1.send_and_verify('AT\Q3', 'OK')
    test.dut.at1.send_and_verify('AT+CMEE=1', 'OK')
    test.dut.at1.send_and_verify('ATS0=0', 'OK')
    test.dut.at1.send_and_verify('AT+CGSN', 'OK')
    test.dut.at1.send_and_verify('AT+CFUN=1', 'OK')
    test.dut.at1.send_and_verify('AT+CCID', 'OK')
    test.dut.at1.send_and_verify('AT+CSCB=1,"",""', 'OK')
    test.dut.at1.send_and_verify('AT+CGMM', 'OK')
    test.dut.at1.send_and_verify('AT+CPIN?', 'OK')
    test.dut.at1.send_and_verify('AT+CIMI', 'OK')
    test.dut.at1.send_and_verify('AT+CREG=2', 'OK')
    test.dut.at1.send_and_verify('AT+CGEREP=2', 'OK')
    test.dut.at1.send_and_verify('AT+CGDCONT=1,"IP","","",0,0', 'OK')
    test.dut.at1.send_and_verify('AT+CMGF=1', 'OK')
    test.dut.at1.send_and_verify('AT+CNMI=2,1', 'OK')
    test.dut.at1.send_and_verify('AT+CSDH=1', 'OK')
    test.dut.at1.send_and_verify('AT+CMGL="ALL"', 'OK')
    test.dut.at1.send_and_verify('AT+CCLK?', 'OK')
    test.dut.at1.send_and_verify('AT^SIND="is_cert",1', 'OK')
    test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,1', 'OK')
    test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,2', 'OK')
    test.dut.at1.send_and_verify('AT^SSECUA="CertStore/TLS/PreconfigureCert",,3', 'OK')

    # 140
    test.dut.at1.send_and_verify('AT^SCFG="SAT/GTP","FFFFFFFF7F0F009F7F00001FE200000003"')
    test.dut.at1.send_and_verify('AT^SCFG="SAT/UTP","F71FF8CE1F9C00879600001FE200000043C0000000004000500000000008"')
    test.dut.at1.send_and_verify('AT^SCFG="Security/A5","0"')
    test.dut.at1.send_and_verify('AT^SCFG="Security/GEA","0"')
    test.dut.at1.send_and_verify('AT^SCFG="Call/ECC","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Call/Speech/Codec","2"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/AntTun","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Mode","1"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Size","1280"')
    test.dut.at1.send_and_verify('AT^SCFG="Ident/Manufacturer","gemalto"')
    test.dut.at1.send_and_verify('AT^SCFG="Ident/Product","ELS62-test"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","1"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/AdRelCal14","1"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RingOnData","on"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RPM","0"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/SRPOM","1"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","off"')
    test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup","on"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/2G","1"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/4G","1","20"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/OutputPowerReduction","0"')
    test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode","2"')
    test.dut.at1.send_and_verify('AT^SCFG="SIM/CS","SIM3"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/TLS/Version","1.1","1.3"')
    test.dut.at1.send_and_verify(
        'AT^SCFG="Serial/USB/DDD","1","0","0409","2E3D","1111","test modules","elstest","20221201"')
    test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug","UNLOCK","01618364124173264411"')
    test.dut.at1.send_and_verify('AT+CVMOD=2')
    test.dut.at1.send_and_verify('AT+CTZU=1')
    test.dut.at1.send_and_verify('AT^SNSRAT=0,7')
    test.dut.at1.send_and_verify('AT^SXRAT=3')
    test.dut.at1.send_and_verify('at^snfota="url","http://114.55.6.216:10080/els62-w_rev00.802"')
    test.dut.at1.send_and_verify('at^snfota="CRC","4ee9a59764736e05efa14ef24eec8573a3e126a6a46e4fac41bc83cb617ac0d4"')
    test.dut.at1.send_and_verify('at^snfota="conid",1')
    test.dut.at1.send_and_verify('at^snfota="urc",0')
    test.dut.at1.send_and_verify('AT+CSCA="13010940500"')
    test.dut.at1.send_and_verify('AT+CPMS="SM","SM","SM"')
    test.dut.at1.send_and_verify('AT+CSMP=17,167,255,247')
    test.dut.at1.send_and_verify('AT^SICS=2,dns1,"1.1.1.1"')
    test.dut.at1.send_and_verify('AT+CGDCONT=3,ipv4v6,test')
    test.dut.at1.send_and_verify('AT+CGQMIN=3,0,0,0,0,0')
    test.dut.at1.send_and_verify('AT+CGSMS=1')
    test.dut.at1.send_and_verify('at^sgauth=3,1,"testpwd2","testuser2"')
    test.dut.at1.send_and_verify('AT+CCLK="22/11/30,12:10:00+08"')
    test.dut.at1.send_and_verify('AT^SCFG= "Radio/Mtpl/2G",3,1,1,,30,26')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Mtpl/4G","3",1,1,0,18')
    test.dut.at1.send_and_verify('AT^SSTA=1,1')
    test.dut.at1.send_and_verify('AT^SAIC=3,1,1,2,0,1,1,1,0')
    test.dut.at1.send_and_verify('AT+CGDSCONT=4,3,0,0')
    test.dut.at1.send_and_verify('AT+COPS=2')
    test.dut.at1.send_and_verify('AT^SGCONF=0,0,8,8,0')
    test.dut.at1.send_and_verify('AT^SPOW=2,1000,3')


def check_nv(test):
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC"', expect="gpio"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline"', expect="asc0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime"', expect="1"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc"', expect="RING"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp"', expect="1"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT"', expect="60"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR"', expect="1"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT"', expect="1"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs"', expect="off"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach"', expect='disabled'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS"', expect='0'))

    # init
    test.expect(test.dut.at1.send_and_verify('AT+CMEE?', expect='2'))
    test.expect(test.dut.at1.send_and_verify('ATS0?', expect='000'))
    test.expect(test.dut.at1.send_and_verify('AT+CFUN?', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT+CSCB?', expect='+CSCB:0'))
    test.expect(test.dut.at1.send_and_verify('AT+CREG?', expect='+CREG: 0'))
    test.expect(test.dut.at1.send_and_verify('AT+CGEREP?', expect='+CGEREP: 0'))
    test.expect(test.dut.at1.send_and_verify('AT+CMGF?', expect='+CMGF: 0'))
    test.expect(test.dut.at1.send_and_verify('AT+CNMI?', expect='+CNMI: 1'))
    test.expect(test.dut.at1.send_and_verify('AT+CSDH?', expect='+CSDH: 0'))

    # 140
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SAT/GTP"', expect='FFFFFFFF7F0F009F7F00001FE200000003'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SAT/UTP"',
                                             expect='F71FF8CE1F9C00879600001FE200000043C0000000004000500000000008'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/A5"', expect='0'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Security/GEA"', expect='0'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Call/ECC"', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Call/Speech/Codec"', expect='2'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/AntTun"', expect='std'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Mode"', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Size"', expect='1280'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Ident/Manufacturer"', expect='gemalto'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Ident/Product"', expect='ELS62-test'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp"', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/AdRelCal14"', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RingOnData"', expect='on'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RPM"', expect='0'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/SRPOM"', expect='1'))  # may be alway=0
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp"', expect='off'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Power/Srv/RF"', expect='0'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup"', expect='on'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/2G"', expect='00000001'))
    test.expect(
        test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/4G"', expect='^SCFG: "Radio/Band/4G","00000001","00000020"'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/OutputPowerReduction"', expect='0'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/CS"', expect='SIM3'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode"', expect='2'))
    test.expect(
        test.dut.at1.send_and_verify('AT^SCFG="Tcp/TLS/Version"', expect='^SCFG: "Tcp/TLS/Version","1.1","1.3"'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Serial/USB/DDD"',
                                             expect='^SCFG: "Serial/USB/DDD","1","0","0409","2E3D","1111","test modules","elstest","20221201"'))
    test.expect(test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug"', expect='UNLOCK'))
    test.expect(test.dut.at1.send_and_verify('AT+CVMOD?', expect='2'))
    test.expect(test.dut.at1.send_and_verify('AT+CTZU?', expect='1'))
    test.expect(test.dut.at1.send_and_verify('AT^SNSRAT?', expect='0, 7'))
    test.expect(test.dut.at1.send_and_verify('AT^SXRAT?', expect='3,3'))
    test.expect(test.dut.at1.send_and_verify('AT^SNFOTA?', expect='"urc","0"'))
    test.expect(test.dut.at1.send_and_verify('AT+CSCA?', expect='+CSCA: "13010940500",129'))
    test.expect(test.dut.at1.send_and_verify('AT+CPMS?', expect='+CPMS: "SM"'))
    test.expect(test.dut.at1.send_and_verify('AT+CSMP?', expect='+CSMP: 17,167,255,247'))
    test.expect(test.dut.at1.send_and_verify('AT^SICS?', expect='^SICS: 2,"dns1","1.1.1.1"'))
    test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', expect='+CGDCONT: 3,"IPV4V6","test"'))
    test.expect(test.dut.at1.send_and_verify('AT+CGQMIN?', expect='CGQMIN: 3,0,0,0,0,0'))
    test.expect(test.dut.at1.send_and_verify('AT+CGSMS?', expect='+CGSMS: 1'))
    test.expect(test.dut.at1.send_and_verify('at^sgauth?', expect='^SGAUTH: 3,1,"testpwd2"'))
    test.expect(test.dut.at1.send_and_verify('AT+CCLK?', expect='22/11/30'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Mtpl/2G","2","1"', expect='"00000001",,"30","26"'))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="Radio/Mtpl/4G","2","1"', expect='"00000001","00000000","18"'))
    test.expect(test.dut.at1.send_and_verify('AT^SSTA?', expect='1,1'))
    test.expect(test.dut.at1.send_and_verify('AT^SAIC?', expect='^SAIC: 3,1,1,2,0,1,1,1,0'))
    test.expect(test.dut.at1.send_and_verify('AT+CGDSCONT?', expect='+CGDSCONT: 4,3,0,0'))
    test.expect(test.dut.at1.send_and_verify('AT^SGCONF?', expect='^SGCONF: 0,0,8,8,0'))
    test.expect(test.dut.at1.send_and_verify('AT^SPOW?', expect='^SPOW: 2,1000,3'))


def reset_nv(test):
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/ASC1","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/FNS","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DCD0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DSR0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/DTR0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/RING0","std"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/mode/SYNC","std"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline","local"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/ActiveTime","2"')
    test.dut.at1.send_and_verify('AT^SCFG="URC/Ringline/SelWUrc","all"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","0"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/IRT","3"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/MR","10"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/OT","6000"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/WithURCs","on"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/AutoAttach","enabled"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/IMS","1"')

    # 140
    test.dut.at1.send_and_verify('AT^SCFG="SAT/GTP","FFFFFFFF7F0F009F7F00001FE200000003"')
    test.dut.at1.send_and_verify('AT^SCFG="SAT/UTP","F71FF8CE1F9C00879600001FE200000043C0000000004000500000000008"')
    test.dut.at1.send_and_verify('AT^SCFG="Security/A5","5"')
    test.dut.at1.send_and_verify('AT^SCFG="Security/GEA","6"')
    test.dut.at1.send_and_verify('AT^SCFG="Call/ECC","0"')
    test.dut.at1.send_and_verify('AT^SCFG="Call/Speech/Codec","0"')
    test.dut.at1.send_and_verify('AT^SCFG="GPIO/Mode/AntTun","gpio"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Mode","0"')
    test.dut.at1.send_and_verify('AT^SCFG="GPRS/MTU/Size","1430"')
    test.dut.at1.send_and_verify('AT^SCFG="Ident/Manufacturer","Cinterion"')
    test.dut.at1.send_and_verify('AT^SCFG="Ident/Product","ELS62-C"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PingRsp","0"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/AdRelCal14","0"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RingOnData","off"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/RPM","2"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/SRPOM","0"')
    test.dut.at1.send_and_verify('AT^SCFG="MEopMode/ShutdownOnCritTemp","on"')
    test.dut.at1.send_and_verify('AT^SCFG="MEShutdown/sVsup","off"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/2G","3"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Band/4G","00000095","000001e2"')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/OutputPowerReduction","4"')
    test.dut.at1.send_and_verify('AT^SCFG="SIM/DualMode","2"')
    test.dut.at1.send_and_verify('AT^SCFG="SIM/CS","SIM3"')
    test.dut.at1.send_and_verify('AT^SCFG="Tcp/TLS/Version","MIN","MAX"')  # maybe 1.2,max
    test.dut.at1.send_and_verify('AT^SCFG="Serial/USB/DDD",0')
    test.dut.at1.send_and_verify('AT^SSECUG="Factory/Debug","LOCK"')
    test.dut.at1.send_and_verify('AT+CVMOD=3')
    test.dut.at1.send_and_verify('AT+CTZU=0')
    test.dut.at1.send_and_verify('AT^SNSRAT=7,0')
    test.dut.at1.send_and_verify('AT^SXRAT=5,3')
    test.dut.at1.send_and_verify('at^snfota="urc",1')
    test.dut.at1.send_and_verify('AT+CSCA="+8613010940500",145')
    test.dut.at1.send_and_verify('AT+CPMS="ME","ME","ME"')
    test.dut.at1.send_and_verify('AT+CSMP=17,167,0,0')
    test.dut.at1.send_and_verify('AT^SICS=2')
    test.dut.at1.send_and_verify('at^sgauth=3')
    test.dut.at1.send_and_verify('AT+CGSMS=3')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Mtpl/2G",3,1,1,,33,27')
    test.dut.at1.send_and_verify('AT^SCFG="Radio/Mtpl/4G","3",1,1,0,23')
    test.dut.at1.send_and_verify('AT^SSTA=0,0')
    test.dut.at1.send_and_verify('AT^SAIC=1,1,1,3,0,0,1,0,0')
    test.dut.at1.send_and_verify('AT+CGDSCONT=4')
    test.dut.at1.send_and_verify('AT+CGDCONT=3')
    test.dut.at1.send_and_verify('AT+COPS=2')
    test.dut.at1.send_and_verify('AT^SGCONF=0,0,12,12,0')
    test.dut.at1.send_and_verify('AT+COPS=0')
    test.dut.at1.send_and_verify('AT^SPOW=1,0,0')


if "__main__" == __name__:
    unicorn.main()
