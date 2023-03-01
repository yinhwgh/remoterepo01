#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn
import os
from core.basetest import BaseTest


dir = "temp_sdk_basic_cpp_compile_dut"

class Test(BaseTest):

    def setup(test):
        
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -r {dir}")
       
        os.mkdir(dir)
        test.log.info("Add basic cpp file: testcpp.cpp")
        cpp_example_file(dir)
        test.log.info("Add basic build script: basic_cpp_build.sh")
        cpp_build_script(dir,test.path_to_sdk)
        
        pass

    def run(test):

        """
        Run simple cpp compile process
        """
        
        
        test.log.info("Run basic compile process:")
        ret1 = test.os.execute_and_verify(f"./{dir}/basic_cpp_build.sh", ".*Compile.*Success.*ELF.*64-bit.*ARM.*dynamically.*linked.*")
        test.expect(ret1)
        #test.log.info("Push test application to module ubi filesystem:")
        #ret2 = test.dut.adb.push(f"./{dir}/testcpp", "/home/root/testcpp")
        #test.expect(ret2)
        #test.log.info("Add +x to file:")
        #ret3 = test.dut.adb.send_and_receive(f"chmod +x /home/root/testcpp")
        #test.expect(test.dut.adb.last_retcode == 0)
        #test.log.info("Execute test application on module:")
        #ret4 = test.dut.adb.send_and_verify(f"/home/root/testcpp", "WorksCpp!")
        #test.expect(ret4)
        test.log.info("Push test application to module tmpfs filesystem:")
        ret5 = test.dut.adb.push(f"./{dir}/testcpp", "/tmp/testcpp")
        test.expect(ret5)
        test.log.info("Add +x to file:")
        ret6 = test.dut.adb.send_and_receive(f"chmod +x /tmp/testcpp")
        test.expect(test.dut.adb.last_retcode == 0)
        test.log.info("Execute test application on module:")
        ret7 = test.dut.adb.send_and_verify(f"/tmp/testcpp", "WorksCpp!")
        test.expect(ret7)
        
     
        
      
        

    def cleanup(test):
        
        test.os.execute(f"rm -r {dir}")
        test.dut.adb.send_and_receive("rm /tmp/testcpp")
        
        pass


## Functions

def cpp_example_file(dir):

 
    x = """
            #include <iostream>

            int main()
            {
                std::cout << "WorksCpp!" << std::endl;
                
                return 0;
            }
        """
    with open(dir + "/testcpp.cpp","w+") as f:
         f.writelines(x)

         
def cpp_build_script(dir,path):
    x = f"""#!/bin/bash
        source {path}/sdk/install/environment-setup-aarch64-poky-linux  && \\
        $CXX -v ./{dir}/testcpp.cpp -o ./{dir}/testcpp && echo "Compile Success" 
        echo $CXX
        file ./{dir}/testcpp 
        exit 0 
        """
    with open(dir + "/basic_cpp_build.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/basic_cpp_build.sh", 509)