#responsible: lukasz.bednarz@globallogic.com
#location: Wroclaw
#TC0000001.001

import unicorn

import os
from core.basetest import BaseTest


dir = "temp_sdk_basic_c_compile"

class Test(BaseTest):

    def setup(test):
        
        
        if(os.path.isdir(dir)):
            print(os.path.isdir(dir))
            test.os.execute(f"rm -r {dir}")
       
        os.mkdir(dir)
            
        c_example_file(dir)
        test.log.info("Add basic c file: testcpp.cpp")
        c_build_script(dir,test.path_to_sdk)
        test.log.info("Add basic build script: basic_c_build.sh")

        
        pass

    def run(test):

        """
        Run simple sdk install command
        """
        
        test.log.info("Run basic compile process:")
        ret2 = test.os.execute_and_verify(f"./{dir}/basic_c_build.sh", ".*Compile.*Success.*ELF.*64-bit.*ARM.*dynamically.*linked.*WorksC!.*")
        test.expect(ret2)
      
        

    def cleanup(test):
        test.os.execute(f"rm -r {dir}")
      
        
        pass


## Functions
def c_example_file(dir):

 
    x = """
            #include <stdio.h>
            int main(void) {
                printf("WorksC!\\n");
                return 0;
            }
        """
    with open(dir + "/testc.c","w+") as f:
         f.writelines(x)
         

 
def c_build_script(dir,path):
    x = f"""#!/bin/bash
        source {path}/sdk/install/environment-setup-aarch64-poky-linux  && \\
        $CC -v ./{dir}/testc.c -o ./{dir}/testc && echo "Compile Success" 
        echo $CC
        file ./{dir}/testc
        export QEMU_LD_PREFIX={path}/sdk/install/sysroots/aarch64-poky-linux/
        qemu-aarch64 ./{dir}/testc 
        exit 0 
        """
    with open(dir + "/basic_c_build.sh","w+") as f:
         f.writelines(x)
    os.chmod(dir + "/basic_c_build.sh", 509)
         

