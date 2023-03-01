#responsible: agata.mastalska@globallogic.com
#location: Wroclaw

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
import re

class Test(BaseTest):
    """
    #2 SAR implementation
    Main goal is to check if is possible to handle the maximum output
    power for specific bands by command: at^scfg=”Radio/Mtpl”
    author: agata.mastalska@globallogic.com
    """

    def setup(test):
        test.dut.dstl_detect()
        profiles_bands = [1,2,4,8]
        profiles = [1,2,3,4,5,6]

        for profile in profiles:
            for band in profiles_bands:
                test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,{},{},20'.format(profile, band), '."Radio/Mtpl","0".*'))
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))
        test.dut.dstl_restart(test.dut.at1)
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))
        pass

    def run(test):
        test.log.step('1. Disable power limitation => mode=0, at^scfg="Radio/Mtpl",0')
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",0', '.*"Radio/Mtpl","0".*'))
        profiles_bands = [1,2,4,8]

        test.log.step('2. Configure profile 1 band 1 and set power limit to 15, at^scfg="Radio/Mtpl",3,1,1,15. Repeat for 2,4,8 bands.')
        for band in profiles_bands:
             test.log.step("profile 1 band {}".format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,1,{},15'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('3. Configure profile 2 band 1,8 and set power limit to 33, at^scfg="Radio/Mtpl",3,2,1,33 and at^scfg="Radio/Mtpl",3,2,8,33')
        second_profile_bands = [1,8]
        for band in second_profile_bands:
             test.log.step('profile 2 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,2,{},33'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('4. Configure profile 2 band 2,4 and set power limit to 30, at^scfg="Radio/Mtpl",3,2,2,30 and at^scfg="Radio/Mtpl",3,2,4,30')
        second_profile_bands = [2,4]
        for band in second_profile_bands:
             test.log.step('profile 2 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,2,{},30'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('5. Configure profile 3 band 1 and set power limit to 19, at^scfg="Radio/Mtpl",3,3,1,19. Repeat for 2,4,8 bands')
        for band in profiles_bands:
             test.log.step('profile 3 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,3,{},19'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('6. Configure profile 4 band 1 and set power limit to 22. Repeat for 2,4,8 bands')
        for band in profiles_bands:
             test.log.step('profile 4 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,4,{},22'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('7. Configure profile 5 band 1 and set power limit to 25. Repeat for 2,4,8 bands')
        for band in profiles_bands:
             test.log.step('profile 5 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,5,{},25'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('8. Configure profile 6 band 1 and set power limit to 28. Repeat for 2,4,8 bands')
        for band in profiles_bands:
             test.log.step('profile 6 band {}'.format(band))
             test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",3,6,{},28'.format(band), '."Radio/Mtpl","0".*'))
             test.expect(check_limit_change(test))

        test.log.step('9. Display current profiles settings => mode=2')
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))

        test.log.step('10. Restart module')
        test.dut.dstl_restart(test.dut.at1)
        
        test.log.step('11. Display current profiles settings => mode=2')
        test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))
        profiles = [1,2,3,4,5,6]
        for profile in profiles:
            test.log.step('Profile {} | 12. For all profiles enable power limitation via profile and display current profile settings'.format(profile))
            test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",1,{}'.format(profile), '."Radio/Mtpl","1","{}".*'.format(profile)))
            test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2,{}'.format(profile), '."Radio/Mtpl","2","{}".*'.format(profile)))

    def cleanup(test):
        pass

if "__main__" == __name__:
    unicorn.main()

def check_limit_change(test):
    matched = re.search(r'Radio/Mtpl\",.,(.),(.),(\d+)', test.dut.at1.last_response)
    profile, band, set_limit = matched.group(1), matched.group(2), matched.group(3)
    test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))
    test.dut.dstl_restart(test.dut.at1)
    test.expect(test.dut.at1.send_and_verify('at^scfg="Radio/Mtpl",2', '."Radio/Mtpl","2".*'))
    matched = re.search(r'Radio/Mtpl\",\"2\",\"{}\",\"{}\",\"(\d+)'.format(profile, band), test.dut.at1.last_response)
    check_limit = matched.group(1)
    if set_limit == check_limit:
        test.log.info("Power limit changed successfully to {}".format(check_limit))
        return True
    else:
        test.log.error("Power limit changed unsuccessfully")
        return False
