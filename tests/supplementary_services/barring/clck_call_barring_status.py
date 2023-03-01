#author: lei.chen@thalesgroup.com
#location: Dalian
#TC0084430.001
import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service import register_to_network
from dstl.security import lock_unlock_sim

class Test(BaseTest):
    """
    TC0084430.001 - TpCclckCallBarringStatus
    Intention:
        Call barring status test
    Steps: Loop the following tests for all Call barring related commands:'AO', 'OI', 'OX', 'AI', 'IR', 'AB', 'AC', 'AG'
           Loop the following tests for all single classes 1, 2, 4, 8, 16, 32, 64, 128, and two combined classes 7, 255
           Loop order for single classes is 1, 16, 32, 64, 128, 2, 4, 8, 
           in order to get whether services of 16 ~ 128 are subscribed, which will be used by class 2.
           1. Lock facility with looped class
           2. Query facility locked status with class 255 and locked class
           3. Unlock facility with looped class
           4. Query facility locked status with class 255 and unlocked class
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_register_to_network() # including cmee=2
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2"))

    def run(test):
        all_barri_facilities = ['AO', 'OI', 'OX', 'AI', 'IR', 'AB', 'AC', 'AG']
        test.ab_facilities = ['AO', 'OI', 'OX', 'AI', 'IR']
        test.ag_facilities = ['AO', 'OI', 'OX']
        test.ac_facilities = ['AI', 'IR']
        single_classes = ['1', '16', '32', '64', '128', '2', '4', '8']
        combine_classes = ['7', '255']
        test.log.step("1. Disable all previously active call barrings")
        test.expect(test.dut.dstl_lock_unlock_facility(facility="AB", lock=False, classes='255'))
        test.log.step("2. Test barring status for each facilities with all classes and certain combined classes.")
        for facility in all_barri_facilities:
            test.is_class_16_subscribed = False
            test.is_class_32_subscribed = False
            test.is_class_64_subscribed = False
            test.is_class_128_subscribed = False
            test.log.h3("2.1 Test barring status with single classes for facility - {facility}.")
            for clas in single_classes:
                test.log.h3(f"Single classes {clas} for facility - {facility}.")
                test.lock_query_unlock_query(facility, str(clas))
            test.log.h3(f"2.2 Test barring status with combined classes for facility - {facility}.")
            for clas in combine_classes:
                test.log.h3(f"Combined classes {clas} for facility - {facility}.")
                test.lock_query_unlock_query(facility, clas)

    def cleanup(test):
        test.expect(test.dut.dstl_lock_unlock_facility(facility="AB", lock=False, classes='255'))
    
    def lock_query_unlock_query(test, facility, classes):
        if facility in ['AB', 'AC', 'AG']:
            related_facilities = eval("test." + facility.lower() + "_facilities")
            for f in related_facilities:
                test.expect(test.lock_unlock_facility(facility=f, lock=True, classes=classes))
                test.expect(test.check_query_status(facility=f, locked_class=classes, query_class=classes))
            test.expect(test.lock_unlock_facility(facility=facility, lock=False, classes=classes))
            for f in related_facilities:
                test.expect(test.check_query_status(facility=f, locked_class=None, query_class=classes))
        else:
            test.log.info(f"Lock {facility} with class {classes} and query with class 255 and {classes}")
            test.expect(test.lock_unlock_facility(facility=facility, lock=True, classes=classes))
            test.expect(test.check_query_status(facility=facility, locked_class=classes, query_class=classes))
            test.log.info(f"Unlock {facility} with class {classes} and query with class 255 and {classes}")
            test.expect(test.lock_unlock_facility(facility=facility, lock=False, classes=classes))
            test.expect(test.check_query_status(facility=facility, locked_class=None, query_class=classes))
            
    def lock_unlock_facility(test, facility, lock, classes):
        result = test.dut.dstl_lock_unlock_facility(facility=facility, lock=lock, classes=classes, query=False)
        if classes in ['16', '32', '64', '128']:
            if result:
                if classes == '16':
                    test.is_class_16_subscribed = True
                elif classes == "32":
                    test.is_class_32_subscribed = True
                elif classes == "64":
                    test.is_class_64_subscribed = True
                else:
                    test.is_class_128_subscribed = True
            elif "not subscribed" in test.dut.at1.last_response:
                test.log.warning(f"Class {classes} may be not subscribed.")
                result = True
        if result:
            test.log.info(f"Successfully lock:{lock} facility {facility} with class {classes}.")
        else:
            test.log.error(f"unable to lock:{lock} facility {facility} with class {classes}.")
        return result

    def check_query_status(test, facility, locked_class, query_class):
        result = True
        # According to spec: Class 2 ("Data") comprises all those individual data classes between 16 and 128
        if str(locked_class) in ['2', '255']:
            if str(locked_class) == '2':
                locked_class = 2
            else:
                locked_class = 1 + 2 + 4 + 8
            query_class = 16 + 32 + 64 + 128
            if test.is_class_16_subscribed:
                locked_class += 16
            if test.is_class_32_subscribed:
                locked_class += 32
            if test.is_class_64_subscribed:
                locked_class += 64
            if test.is_class_128_subscribed:
                locked_class += 128
        elif str(locked_class) == '7':
            locked_class = 1 + 2 + 4
            # should 16 ~ 128 be impacted by 2?
        if query_class != "255":
            result &= test.dut.dstl_query_facility_lock_status(facility, locked_class, query_class=255)
        result &= test.dut.dstl_query_facility_lock_status(facility, locked_class, query_class=query_class)
        return result


if '__main__' == __name__:
    unicorn.main()


