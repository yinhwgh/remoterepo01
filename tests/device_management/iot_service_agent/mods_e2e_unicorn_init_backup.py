# responsible: baris.kildi@thalesgroup.com, johann.suhr@thalesgroup.com, katrin.kubald@thalesgroup.com
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
#from dstl.miscellaneous.mods_e2e_unicorn_support import *

import json
import datetime


class Test(BaseTest):
    """
    Init
    """
    systart_timeout = 240

    def get_all_iccid(test, imei):
        test.log.info(f'{20 * "*"} Get all subscriptions ICCIDs which belong to your IMEI {20 * "*"}')
        subscriptions = get_subscriptions().json()
        iccids = get_all_iccid_by_imei(subscriptions, imei)
        test.log.info(iccids)
        return iccids


    def get_all_subscription_ids(test, imei):
        test.log.step("Delete all your subscriptions belong to your imei")
        subscriptions = get_subscriptions().json()
        subsription_ids = get_all_subscription_ids_by_imei(subscriptions, imei)
        test.log.info(subsription_ids)
        return subsription_ids


    def delete_subscription(test, subscription_id):
        request = delete_subscription(subscription_id)
        test.log.info(request)
        response = request.json()
        test.log.info(request)
        log_body(response)
        job_id = response['jobId']
        test.log.info("This is your jobID: " + job_id)

        test.dut.at1.wait_for("^SYSSTART AIRPLANE MODE", timeout=test.systart_timeout)
        test.sleep(5)
        test.dut.at1.wait_for("^SYSSTART", timeout=test.systart_timeout)

        test.dut.at1.send_and_verify('at^srvctl="MODS","stop"')
        test.sleep(15)

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",not_created_rule', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')

        test.sleep(15)

        test.dut.at1.send_and_verify('at^srvctl="MODS","status"')
        if "service is running" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0', retry=15,
                                                           retry_expect="service start failed"))

        test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3,
                                                       retry_expect="no network service"))

        test.sleep(10)

        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        while ",registered" not in test.dut.at1.last_response and wait_count < 30:
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(45)
            wait_count = wait_count + 1

        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='.*OK.*')








        test.log.step("Enable URC's")

        test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('at^susmc="LPA/Ext/URC",1', ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Engine/URC",1', expect='^SUSMC: "LPA/Engine/URC",1'))
        test.expect(test.dut.at1.send_and_verify('AT^SUSMC="LPA/Profiles/Download/URC",1',
                                                 expect='^SUSMC: "LPA/Profiles/Download/URC",1'))


        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        while ",registered" not in test.dut.at1.last_response and wait_count < 30:
            # wait_count: 20 * 45 => 900 seconds => 15 minutes
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(45)
            wait_count = wait_count + 1


        job = get_job(job_id).json()
        log_body(job)

        test.log.info("A job was found. Wait until its status is equal succeeded ...")
        wait_count = 0
        max_count = 180
        while job["status"] != 'ended' and wait_count < max_count:
            # wait_count: 5 * 180 => 900 seconds => 15 minutes
            job = get_job(job_id).json()
            log_body(job)
            test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15,
                                                           wait_after_send=3, retry_expect="no network service"))
            test.sleep(5)
            wait_count = wait_count + 1

        if wait_count == max_count:
            dstl.log.error("The job did not succeeded!!! ")
        else:
            dstl.log.info("The job succeeded.")


    def activate_oper_prof_manually(test):
        test.sleep(60)
        test.dut.at1.send_and_verify('at^SUSMA="LPA/Profiles/Info"', expect='.*OK.*')
        if '"LPA/Profiles/Info",1' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('at^srvctl="MODS","stop"')
            test.sleep(15)
            test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/0/0/10","APN_NAME","internet"', expect='.*OK.*')

            test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/","APN","internet"', expect='.*OK.*')

            test.dut.at1.send_and_verify('at+cgdcont=1,"IP","internet"', expect='.*OK.*')

            test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Engine",1', expect='^SUSMA: "LPA/Engine",2', retry=10,
                                                           retry_expect='^SUSMA: "LPA/Engine",1')


            test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Profiles/Enable",1', expect='.*OK.*', retry=15,
                                               retry_expect="operation temporary not allowed")

            test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",1', expect='.*OK.*')
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0', retry=15,
                                                           retry_expect="service start failed"))

            test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3,
                                                           retry_expect="no network service")

            test.sleep(10)

            test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*')
            wait_count = 0
            while ",registered" not in test.dut.at1.last_response and wait_count < 30:
                # wait_count: 20 * 45 => 900 seconds => 15 minutes
                test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
                test.sleep(30)
                wait_count = wait_count + 1


        else:
            pass


    def check_after_delete_subscription(test):

        test.log.step("Check if Bootstrap state is back")
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
            test.log.info("Your active Bootstrap Profile is back")
        else:
            test.log.info("Bootstrap Profile is not active something went wrong")

        test.log.step(
            "Check if APN of subscription occurs in response of 'at+cgdcont?' and 'AT^SNLWM2M=cfg/ext,MODS'")
        test.expect(test.dut.at1.send_and_verify('at+cgdcont?', expect='.*OK.*'))
        if "JTM2M" in test.dut.at1.last_response:
            test.log.info("Your current APN is JTM2M")
        else:
            test.log.info("JTM2M does not occur in response, anything went wrong and test will be terminated")
            test.expect(False, critical=True)

        test.dut.at1.send_and_verify('AT^SNLWM2M=cfg/ext,MODS', expect='.*OK.*')
        last_response = test.dut.at1.last_response
        if '"APN_NAME","JTM2M"' in last_response and '"APN","JTM2M"' in last_response:
            test.log.info("Required APN occurs in response")
        else:
            test.log.info("Required APN not found, test will be terminated")
            test.expect(False, critical=True)


        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode"', expect='.*OK.*')

        test.log.info("Send pending notification(s) to SMDP+ server. ---- Internal Write Command (Do not publish!) ")
        test.dut.at1.send_and_verify_retry('AT^SUSMA="LPA/Ext/NotificationSent"', expect='.*OK.*')
        notif_response = f'\^SUSMA: "LPA/Ext/NotificationSent",0,0,0x0000'

        test.sleep(10)

        test.attempt(test.dut.at1.send_and_verify,'AT^SUSMA="LPA/Ext/NotificationSent"', notif_response, sleep=3, retry=15)


    def delete_device(test, device_id):
        test.log.info(f'{20 * "*"} Delete Device {20 * "*"}')
        deleted_device_obj = delete_device(device_id).json()
        log_body(deleted_device_obj)
        test.expect(delete_device(device_id).json() != [])


    def create_subscription(test, iccid):
        test.log.info(f'{20 * "*"} Create Subscription on MODS {20 * "*"}')
        request = create_subscription(iccid, "3f1ba891-617f-4441-955c-97181c824ad4")
        response = request.json()
        log_body(response)

        test.expect(request.status_code == 200, critical=True)

        test.sleep(10)

    def setup(test):

        test.log.com('***** Testcase: ' + test.test_file + ' - Start *****')

        test.dut.dstl_detect()
        test.dut.dstl_restart()
        test.dut.dstl_set_real_time_clock()
        test.expect(test.dut.at1.send_and_verify('at+creg=2', ".*OK.*"))


    def run(test):
        test.dut.at1.send_and_verify('at^srvctl="MODS","status"')
        if "service is running" in test.dut.at1.last_response:
            test.log.info("Agent is already started")
        else:
            test.expect(test.dut.at1.send_and_verify_retry('at^srvctl="MODS","start"',
                                                           expect='^SRVCTL: "MODS","start",0', retry=15,
                                                           retry_expect="service start failed"))

        test.expect(test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3,
                                                       retry_expect="no network service"))
        test.expect(test.dut.at1.send_and_verify('at+cops?', wait_for='\+COPS: .,.,".*",7'))


        test.sleep(5)

        imei = test.dut.dstl_get_imei()
        test.log.info("This is your IMEI: " + imei)

        test.log.step("Check/create device on MODS")
        label = 'Unicorn E2E Tests'

        devices = get_devices().json()
        device_id = get_device_id(devices, imei)
        if device_id is None:
            test.log.info(f'{20 * "*"} Device will be created {20 * "*"}'),
            response = create_device(imei, label)
            body = response.json()
            log_body(body)
            test.expect(response.status_code == 200)
            test.expect(body != [])
            device_id = body["id"]
        else:
            test.log.info(f'{20 * "*"} Device already exists {20 * "*"}')


        test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
        wait_count = 0
        while ",registered" not in test.dut.at1.last_response and wait_count < 30:
            # wait_count: 30 * 30 => 900 seconds => 15 minutes
            test.expect(test.dut.at1.send_and_verify('at^snlwm2m=status/srv,<list>', expect='.*OK.*'))
            test.sleep(30)
            wait_count = wait_count + 1

        test.log.info(f'{20 * "*"} Get all subscriptions ICCIDs which belong to your IMEI {20 * "*"}')
        iccids = test.get_all_iccid(imei)

        test.log.info(
            f'{20 * "*"} Get all subscriptions IDs which belong to your IMEI and delete all subscriptions{20 * "*"}')
        subscription_ids = test.get_all_subscription_ids(imei)

        for subscription_id in subscription_ids:
            test.delete_subscription(subscription_id)
            test.activate_oper_prof_manually()
            test.sleep(10)

        test.log.info(f'{20 * "*"} Check if values after deletion of all subscriptions are correct {20 * "*"}')
        test.check_after_delete_subscription()

        test.log.info(f'{20 * "*"} Delete device {20 * "*"}')
        test.delete_device(device_id)

        test.log.info(f'{20 * "*"} Create already deleted subscriptions back on MODS {20 * "*"}')
        for iccid in iccids:
            test.create_subscription(iccid)
            test.sleep(5)

        # test.expect(test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/0/0/10","APN_NAME","JTM2M"', expect='.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('at^snlwm2m="cfg/ext","MODS","/","APN","JTM2M"', expect='.*OK.*'))
        # test.expect(test.dut.at1.send_and_verify('at+cgdcont=1,"IP","JTM2M"', expect='.*OK.*'))

        test.log.info(f'{20 * "*"} Check status of module {20 * "*"}')

        test.dut.at1.send_and_verify_retry("at+cops=1,2,26201,7", expect="OK", retry=15, wait_after_send=3,
                                           retry_expect="no network service")

        #test.dut.dstl_stop_mods_agent()





    def cleanup(test):

        test.dut.at1.send_and_verify('at^srvctl="MODS","stop"')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/prid",UNICORN-POC', expect='.*OK.*')
        test.dut.at1.send_and_verify('AT^SRVCFG="MODS","usm/downloadMode",0', expect='.*OK.*')

        test.dut.at1.send_and_verify_retry('at^SUSMA="LPA/Engine",1', expect='^SUSMA: "LPA/Engine",2', retry=10,
                                           sleep=3, retry_expect='^SUSMA: "LPA/Engine",1')
        test.dut.at1.send_and_verify('at^susma?', expect='.*OK.*')
        if '"LPA/Profiles/Info",0,1' in test.dut.at1.last_response:
            test.dut.at1.send_and_verify('"LPA/Profiles/Disable",0', expect='.*OK.*')
        else:
            test.log.error("Something went wrong")

        test.log.com('***** Testcase: ' + test.test_file + ' - End *****')


if "__main__" == __name__:
    unicorn.main()
