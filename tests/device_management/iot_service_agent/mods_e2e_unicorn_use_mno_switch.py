# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com
# location: Berlin

import unicorn
import re
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_rest_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc

import json
import datetime


class Test(BaseTest):
    """
    UseCase_1
    """

    def setup(test):
        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.info(f'{40 * "*"} Check if device exists if yes delete Device {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        if not device_id:
            test.log.info("Device with your imei will be created")
        else:
            request = delete_device(device_id)
            response = request.json()
            log_body(response)

        test.log.info(f'{40 * "*"} Get all Rules {40 * "*"}')
        rules = get_rules()
        log_body(rules.json())
        test.expect(rules.status_code == 200)

        test.log.info(f'{40 * "*"} Get all APN Profiles {40 * "*"}')
        response = get_apn_profiles()
        apn_profiles = response.json()
        log_body(apn_profiles)
        test.expect(response.status_code == 200)

        test.log.info(f'{40 * "*"} Get all Subscriptions {40 * "*"}')
        subscriptions = get_subscriptions()
        log_body(subscriptions.json())
        test.expect(subscriptions.status_code == 200)

        test.dut.at1.send_and_verify('at^sbnr=preconfig_cert', expect='.*OK.*')
        test.dut.dstl_set_real_time_clock()
        test.dut.dstl_detect()
        test.dut.dstl_restart()

    def run(test):
        # Get the current time - 1 hour to find the job
        time_before_test = test.dut.dstl_get_mods_time(format=True)

        test.dut.at1.send_and_verify('AT^SNLWM2M=act,MODS')
        if "Service already started" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify('AT^SNLWM2M=act,MODS,start', expect='.*OK.*'))

        test.log.step("1. Register to network and display the address of the active PDP context")
        test.dut.dstl_get_imsi()

        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201", expect="OK", retry=10,
                                                       retry_expect="no network service"))
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",7'))

        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))

        test.dut.at1.send_and_verify('at^susma="LPA/Engine",1', wait_for='.*2')

        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                              test.dut.at1.last_response))

        test.dut.dstl_get_imsi()
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if "JTM2M" in last_response:
            test.log.info("APN which you are looking occurs in response")
        else:
            test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))

        # test.dut.at1.send_and_verify('AT^SNLWM2M=act,MODS,stop', expect='.*OK.*')
        # test.sleep(5)
        # These at commands helped us to continue testing with an old software version
        # test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS,/,MAX_BOOTSTRAP_WAIT_TIME,1', expect='.*OK.*')
        # test.dut.at1.send_and_verify('at^snlwm2m=cfg/ext,MODS,/,PER_REGSTATUS_FEAT,0', expect='.*OK.*')
        # test.dut.at1.send_and_verify('at^snlwm2m=cfg/ext,MODS,/,PER_BOOTSTRAP_FEAT,0', expect='.*OK.*')

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        if '"APN_NAME","JTM2M"' in last_response and '"APN","JTM2M"' in last_response:
            test.log.info("APN which you are looking occurs in response")
        else:
            test.log.info("Required APN not found, test will be terminated")
            test.expect(False, critical=True)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.step("2. Create device on MODS")
        label = 'Unicorn E2E Tests'

        test.log.info(f'{40 * "*"} Create Device {40 * "*"}')
        response = create_device(imei, label)
        body = response.json()
        log_body(body)
        test.expect(response.status_code == 200)
        test.expect(body != [])
        device_id = body["id"]

        # test.dut.at1.send_and_verify('AT^SNLWM2M=act,MODS,start', expect='.*OK.*')
        # test.sleep(5)

        test.log.step("3. Set Download Mode to 1")
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('at^snlwm2m=cfg,MODS,/33096/0/6,1', expect='.*OK.*'))

        test.log.step("4. Set Provisioning Rule ID")
        test.expect(test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('at^snlwm2m=cfg,MODS,/33096/0/8,UNICORN-POC', expect='.*OK.*'))

        test.sleep(15)

        test.log.step("5. Check if Bootstrap state is active")
        test.expect(test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*'))

        #test.log.step("6. Restart module and start Engine")
        #test.dut.dstl_restart()
        #test.dut.at1.send_and_verify('at^susma="LPA/Engine",1', expect='.*OK.*')

        test.log.step("6. Enable URC's")
        test.expect(test.dut.at1.send_and_verify('at^sind=simstatus,1', ".*SIND: simstatus,1,5", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at^sind=simdata,1', ".*SIND: simdata,1", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at^sind=iccid,1', ".*SIND: iccid,1,.*", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at^sind=euiccid,1', ".*SIND: euiccid,1,""", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SIND=imsi,1', ".*SIND: imsi,1,.*", wait_for="OK"))
        test.expect(test.dut.at1.send_and_verify('at+cgerep=2,0', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/Ext/URC",1', ".*OK.*"))

        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))

        test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201", expect="OK", retry=10,
                                                       retry_expect="no network service"))
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",7'))
        #test.dut.at1.send_and_verify('AT^SNLWM2M=act,MODS,start', expect='.*OK.*')
        test.sleep(5)

        test.log.step(
            "7. Wait until device is registered - key word 'registered' should occur at the end of the response")
        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        while "deregistered" in test.dut.at1.last_response:
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(45)

        test.log.step("8. Find the job and wait until it is finished")
        jobs = get_jobs_since_time(imei, job_type='connectivityProvision', time=time_before_test).json()
        log_body(jobs)

        test.expect(test.dut.at1.wait_for("^SYSSTART AIRPLANE MODE", timeout=180))
        test.sleep(12)
        test.expect(test.dut.at1.wait_for("^SYSSTART", timeout=180))
        test.sleep(10)
        # Sometimes module does not register after SYSSTART
        test.expect(test.dut.at1.send_and_verify('at^sxrat=7,7', wait_for="OK", timeout=10))
        test.expect(test.dut.at1.send_and_verify('at^sxrat?', wait_for="OK", timeout=10))
        test.dut.at1.send_and_verify_retry("at+cops=1,2,26201", expect="OK", retry=10,
                                                       retry_expect="no network service")

        while test.expect(jobs['numberOfElements'] == 0):
            jobs = get_jobs_since_time(imei, job_type='connectivityProvision', time=time_before_test).json()
            log_body(jobs)
            test.sleep(10)

        test.log.info("A job was found. Checking its status ...")
        latest_job = jobs['content'][-1]
        job_status = latest_job["status"]
        # Sometimes the status is suspended and gets succeeded after a while.
        while test.expect(job_status != 'succeeded'):
            test.expect(test.dut.at1.send_and_verify('at^smoni', wait_for='OK'))
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            jobs = get_jobs_since_time(imei, job_type='connectivityProvision', time=time_before_test).json()
            latest_job = jobs['content'][-1]
            job_status = latest_job["status"]
            log_body(jobs)
            test.sleep(30)

        test.log.info("The job succeeded.")

        test.log.step("9. Check if Bootstrap state is deactive and subscription is active")
        test.expect(test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if '"LPA/Profiles/Info",1,1' in last_response and '"LPA/Profiles/Info",0,0' in last_response:
            test.log.info("Your subscription is active")
        else:
            test.log.info("Subscription is still not active, test will be terminated")
            test.expect(False, critical=True)

        test.log.step(
            "10. Check if APN of subscription is occurs in response of 'at+cgdcont?' and 'AT^SNLWM2M=cfg/ext,MODS'")
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        last_response = test.dut.at1.last_response
        if "internet" in last_response:
            test.log.info("Your current APN is internet")
        else:
            test.log.info("APN of your subscription does not occur, anything went wrong and test will be terminated")
            test.expect(False, critical=True)

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        if '"APN_NAME","internet"' in last_response and '"APN","internet"' in last_response:
            test.log.info("Required APN occurs in response")
        else:
            test.log.info("Required APN not found, test will be terminated")
            test.expect(False, critical=True)

        test.log.step("11. Check if assigned IP address shown in at+cgpddr and at^snlwm2m=status/srv,<list> is equal")
        test.expect(test.dut.at1.send_and_verify('AT+CGPADDR={}'.format(1), '.*OK.*'))
        test.expect(re.search(r"(\+CGPADDR: " + str(1) + r",\"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\")",
                              test.dut.at1.last_response))

        test.log.step("12. Call ping if internet connection is established via operational profile")
        test.expect(test.dut.at1.send_and_verify('AT^SICA=1,1', ".*OK.*"))
        test.sleep(20)
        test.expect(test.dut.at1.send_and_verify('AT^SISX=Ping,1,"www.google.com",5', expect='.*OK.*'))

        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))

        test.log.info(f'{40 * "*"} Get all attributes of your Device {40 * "*"}')
        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        test.log.info(device_id)
        device_obj = get_device_long(device_id).json()
        log_body(device_obj)
        test.expect(imei == device_obj['imei'])


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
