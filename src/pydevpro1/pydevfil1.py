#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" hola """

import sys

if __name__ == "__main__":
    
    print("I made some changes")
    
    for index, item in enumerate(sys.argv[1:]):
        
        print("This arg is # {} contains {}".format(index, item))
        scan = "nmap -sL -n " + str(item)
        print("\tScan command number {} is '{}'".format(index, scan))
    
    print("bye")

""" adeu """