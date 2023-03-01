#!/usr/bin/python3

import os
import json
import datetime
import time
import subprocess

def execute_all_tcs(target):
    for root, dirs, files in os.walk(target):
        for f in files:
            if root == target and f.endswith('.py'):
                script = os.path.join(root,f)
                cmd = f"/home/jenkins/unicorn/unicorn {script}"
                subprocess.run(cmd, shell=True)

if __name__=='__main__':
    execute_all_tcs('mercury')
