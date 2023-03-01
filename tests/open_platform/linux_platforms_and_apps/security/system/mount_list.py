# responsible: lukasz.bednarz@globallogic.com
# location: Wroclaw


import unicorn
from core.basetest import BaseTest



class Test(BaseTest):

    def setup(test):
        pass

    def run(test):
    
        LIST_TO_CHECK=[
                'rootfs on / type rootfs (rw)',
                'sysfs on /sys type sysfs (rw,relatime)',
                'proc on /proc type proc (rw,relatime)',
                '/dev/ubiblock0_0 on / type squashfs (ro,relatime)',
                'ubi1:home on /home type ubifs (rw,relatime,chk_data_crc,i_version)',
                'proc on /proc type proc (rw,relatime)',
                'sysfs on /sys type sysfs (rw,relatime)',
                'debugfs on /sys/kernel/debug type debugfs (rw,relatime)',
                'tmpfs on /dev type tmpfs (rw,relatime,size=64k,mode=755)',
                'devpts on /dev/pts type devpts (rw,relatime,mode=600)',
                'tmpfs on /run type tmpfs (rw,nosuid,nodev,mode=755)',
                'tmpfs on /var/volatile type tmpfs (rw,relatime)',
                'tmpfs on /var/lib type tmpfs (rw,relatime)',
                'ubi:data on /data type ubifs (rw,relatime,bulk_read,chk_data_crc)',
                'ubi:modem on /firmware type ubifs (ro,relatime,bulk_read,chk_data_crc)',
                'none on /sys/kernel/config type configfs (rw,relatime)',
                'adb on /dev/usb-ffs/adb type functionfs (rw,relatime)'
        ]

        
        test.log.info("Check list of root daemons in the system")
        
        test.dut.adb.send_and_receive("mount")
        test.expect(test.dut.adb.last_retcode == 0)
     

        
        mode_list_ps = list(test.dut.adb.last_response.split("\n"))
        
        
        for i in mode_list_ps:
            print(f"{i}")
            test.expect( search(LIST_TO_CHECK, i.rstrip() ) )
        


    def cleanup(test):
        pass
        
        
        

def search(list, line):
    for i in range(len(list)):
        if list[i] == line:
            return True
    return False