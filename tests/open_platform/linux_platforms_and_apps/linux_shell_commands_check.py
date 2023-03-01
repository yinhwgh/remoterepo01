#responsible: christian.gosslar@thalesgroup.com; tomasz.witka@globallogic.com
#location: Berlin
#TC0000000.001

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.restart_module import dstl_restart
from dstl.network_service.attach_to_network import dstl_enter_pin

"""

https://confluence.gemalto.com/display/GMVTIB/Linux+shell+commands+check

iptables/ip6tables iptables-restore/ip6tables-restore | iptables incl restore support to speed up load firewall rules during startup
iproute2 package version 5.5.0 | Supported features must include: * IPv6 * VLAN * egress-qos-map * L2TP support * Batch mode support
mpstat | Monitor CPU/Memory utiliziation
conntrack | Monitor and manipulate connection tracking table
dnsmasq | Incl. conntrack support
mtd-utils | ubiupdatevol, ubiattach, …
shell | Busybox or similar shell with ls, cat, cd, …
basename | Shell scripting
cat | Shell scripting
cd | Shell scripting
chmod | Shell scripting
chown | Shell scripting
cp | Shell scripting
cut | Shell scripting
date | Shell scripting
dc | Shell scripting
dirname | Shell scripting
echo | Shell scripting
find | Shell scripting
grep | Shell scripting
gzip | Shell scripting
head | Shell scripting
kill | Shell scripting
ln | Shell scripting
ls | Shell scripting
mkdir | Shell scripting
mount | Shell scripting during init
mpstat | Performance monitoring
mv | Shell scripting
pgrep | Shell scripting
pkill | Shell scripting
ps | Process monitoring
rm | Shell scripting
sed | Shell scripting
seq | Shell scripting
sh | Shell scripting
sleep | Shell scripting
stty | Configure UART and debug
sync | Synchronize flash filesystem
tail | Shell scripting
tar | Shell scripting
test (and [ and [[) | Shell scripting
touch | Shell scripting
umount | Shell scripting
uname | Shell scripting
wc | Shell scripting
chroot | Shell scripting (security)
ifconfig | connectionmanager
insmod | Wifi/Ethernet driver loading
klogd | Logging special messages to kernel log
mkfs (supporting all available filesystems) | Shell scripting
reboot | Shell scripting
rmmod | Shell scripting
udhcpc | connectionmanager
cryptosetup


"""

class Test(BaseTest):
    
    def setup(test):
        test.require_plugin('adb')
        test.dut.dstl_detect()

    def run(test):
        
        BUILTIN = []
        
        BUILTIN1 = [
            'cd'
        ]
        
        
        BIN = []
        
        BIN1 = [
            'iptables',
            'ip6tables',
            'iptables-restore &',
            'ip6tables-restore &',
            'iproute',
            'mpstat',
            'conntrack',
            'dnsmasq',
            'ubiupdatevol',
            'ubiattach',
            'udhcpc',
            'ls',
            'cat &',
            'chmod',
            'chown',
            'cp',
            'cut',
            'date',
            'dc &',
            'dirname',
            'echo',
            'find --help',
            'grep',
            'head &',
            'gzip',
            'kill',
            'ln',
            'mkdir',
            'mount',
            'mpstat',
            'mv',
            'pgrep',
            'pkill',
            'ps',
            'rm',
            'sed',
            'seq',
            'sh &',
            'sleep',
            'stty',
            'sync',
            'tail &',
            'tar',
            'test',
            'touch',
            'umount',
            'uname',
            'wc &',
            'chroot',
            'ifconfig',
            'insmod',
            'klogd',
            'reboot --help',
            'rmmod'
        ]
        
        BIN2 = [
            'iproute2',
            'mtd-utils',
            'mkfs',
            'connectionmanager',
            'cryptosetup'
        ]
        
        
        if str(test.dut.step) == '4' and test.dut.project == 'BOBCAT':
            BIN = BIN1
            BUILTIN = BUILTIN1
        
        
        for b in BIN:
            call = b.replace('--help', '')
            call = call.rstrip('&')
            call = call.rstrip()
            res = test.dut.adb.send_and_receive("which {}".format(call))
            test.expect(test.dut.adb.last_retcode == 0)
            
        for b in BIN + BUILTIN:
            res = test.dut.adb.send_and_receive(b)
            test.expect('not found' not in test.dut.adb.last_response)


    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
    
  