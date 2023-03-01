#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_check-home-uid-gid"

class Test(BaseTest):

    def setup(test):
    
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -rf {dir}")
       
        os.mkdir(dir)
       
        
        test.log.info("Create test script: check_home_uid_gid.sh")
        check_home_uid_gid(dir)
        pass

    def run(test):

        """
        Check UIDs/GIDs files in /home directory
        """

        
        test.log.info("Push test script to module tmpfs filesystem:")
        ret5 = test.dut.adb.push(f"./{dir}/check_home_uid_gid.sh", "/tmp/")
        test.expect(ret5)
        test.log.info("Add +x to file:")
        ret6 = test.dut.adb.send_and_receive(f"chmod +x /tmp/check_home_uid_gid.sh")
        test.expect(test.dut.adb.last_retcode == 0)
        test.log.info("Execute test script on module:")
        ret7 = test.dut.adb.send_and_verify(f"/tmp/check_home_uid_gid.sh",".*0.*")
        test.expect(test.dut.adb.last_retcode == 0)
        
        
      
        

    def cleanup(test):
        test.os.execute(f"rm -rf {dir}")
        test.dut.adb.send_and_receive("rm /tmp/check_home_uid_gid.sh")
        pass

    

def check_home_uid_gid(dir):
    x = f"""
        #!/bin/ash

        ret=0
        for DIR in $(find /home/ -type d -maxdepth 1 -mindepth 1);
        do
            USER=$(basename "$DIR")
            # Check if user exist
            id "$USER" > /dev/null 2>&1
            if [ $? -eq 0 ]
            then
                echo "User: $USER exist in the system"
                GROUP=$(id -gn "$USER")
                # Find all files in directory
                for FILE in $(find "$DIR" -type f);
                do
                    # Check user
                    user=$(stat -c %U "$FILE")
                    if [ "$user" != "$USER" ]
                    then
                        echo "------ wrong user ($user) for $FILE-------"
                        ret=1
                    fi
                    # Check group
                    group=$(stat -c %G "$FILE")
                    if [ "$group" != "$GROUP" ]
                    then
                        echo "------ wrong group ($group) for $FILE-------"
                        ret=1
                    fi
                done
            else
                echo "User: $USER does not exist in the system"
                ret=2
            fi
        done

        echo $ret

        """
    with open(dir + "/check_home_uid_gid.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/check_home_uid_gid.sh", 509)