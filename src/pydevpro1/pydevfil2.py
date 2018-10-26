#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" ----------------------------------------------------------------
    checkdr2 -- check bind9 direct and reverse zone files
    Integrate simple regexp stuff and dictionaries.
    -----------------------------------------------------------------
"""

import sys
import re
import os.path
from socket import inet_aton
# import struct

""" define regexps """

expComment = re.compile( '^.*;' )
expArecord = re.compile( '.*IN.*A.*' )
expPTRrecord = re.compile( '.*IN.*PTR.*' )

""" -----------------------------------------------------------------
    Process cmd line args  
    -----------------------------------------------------------------
"""

argc = len( sys.argv )
print( "; Got {:d} args".format( argc ) ) 

if argc < 3:
    print( "; three args needed. Exiting." )
    exit( 1 )
else:
    dirName = sys.argv[1]
    revName = sys.argv[2]
    print( "; direct file name", dirName ) 
    print( "; reverse file name", revName ) 

""" -----------------------------------------------------------------
    check if args are names of existing files 
    -----------------------------------------------------------------
""" 

if not os.path.exists( dirName ) or not os.path.exists( revName ):
    print( ";", dirName, "and", revName, "must be valid files. Exiting." )
    exit( 2 )

""" -----------------------------------------------------------------
    assume name format is 'zone.DOMAIN.db' for direct 
    -----------------------------------------------------------------
"""

try:
    dirDomain = re.search( 'zone\.(.+?)\.db', dirName ).group( 1 )

except AttributeError:
    print( "; direct domain name", dirDomain, "not valid. Exiting." )
    exit( 3 )

""" -----------------------------------------------------------------
    local CHAPUZA to overcome naming defects 
    -----------------------------------------------------------------
"""

if dirDomain == "XXXX":
    dirDomain = "XXXX.ch"
if dirDomain == "YYYY":
    dirDomain = "YYYY.ch"
if dirDomain == "":
    dirDomain = "ERRRORRR"
print( "; direct domain '" + dirDomain + "'" )

""" -----------------------------------------------------------------
    Read direct file into a list
    -----------------------------------------------------------------
"""

try:
    dirFile = open( dirName ).readlines( )

except IOError as e:
    print( "; an i/o error occurred opening", dirName + ". Exiting." )
    errno, strerror = e.args
    print( e )
    exit( errno )

""" 
    -----------------------------------------------------------------
    create empty dictionary
    -----------------------------------------------------------------
"""

dirDict = { }

""" 
    -----------------------------------------------------------------
    Loop thru text file lines
    remove trailing newline character on each
    ignore lines starting with ";" and not like 'xxx IN A yyy'
    split the line in words and put them into the 'cols' list
    analyze each word to find the mymynext to the "A" token
    -----------------------------------------------------------------
"""

for i, line in enumerate( dirFile ):
    line = line.rstrip( "\n" )
    if not expComment.match( line ) and expArecord.match( line ):
        cols = line.split( )
        key = ""
        val = cols[ 0 ]
        for j, word in enumerate( cols ):
            if word == "A":
                mynext = j + 1
                if mynext < len( cols ):
                    key = cols[ mynext ]
                    if key != "":
                        dirDict[ key ] = val + "." + dirDomain

""" 
    -----------------------------------------------------------------
    Print the 'direct' dictionary
    -----------------------------------------------------------------
"""

print( "\n\nDirect entries\n" )
for key, val in sorted( dirDict.items( ), key=lambda item: inet_aton( item[0] ) ):
    print( "; {:16s} - {}".format( key, val ) )

""" 
    -----------------------------------------------------------------
    assume name format is 'x.y.z.in-addr.arpa.db' for reverse 
    -----------------------------------------------------------------
"""

try:
        revDomain = re.search( '.*/(.+?)\.db', revName ).group( 1 )

except AttributeError:
        print( "; reverse domain name", revDomain, "is not valid. Exiting." )
        exit( 3 )

""" 
    -----------------------------------------------------------------
    convert in-addr.arpa domain to its corresponding direct
    -----------------------------------------------------------------
"""

rtod = revDomain.split( "." )
rtod.remove( "in-addr" )
rtod.remove( "arpa" )
rtod = rtod[::-1]
turnDomain = '.'.join( rtod )
print( "; reverse to direct domain", turnDomain )

""" 
    -----------------------------------------------------------------
    local CHAPUZA to overcome naming defects
    -----------------------------------------------------------------
"""

if revDomain == "":
        revDomain = "ERRRORRR"

print( "; reverse domain '" + revDomain + "'" )

""" 
    -----------------------------------------------------------------
    Read reverse file into a list
    -----------------------------------------------------------------
"""

try:
    revFile = open( revName ).readlines( )

except IOError as e:
    print( "; an i/o error occurred opening", revName + ". Exiting." )
    errno, strerror = e.args
    print( e )
    exit( errno )

"""
    -----------------------------------------------------------------
    create empty dictionary
    -----------------------------------------------------------------
"""

print( "; after opening reverse file '" + revName + "'" )
revDict = { }

"""
    -----------------------------------------------------------------
    Loop thru reverse file lines
    remove trailing newline character on each
    ignore lines starting with ";" and not like 'yyy IN PTR xxx'
    split the line in words and put them into the 'cols' list
    analyze each word to find the mynext to the "PTR" token
    -----------------------------------------------------------------
"""

for i, line in enumerate( revFile ):
    line = line.rstrip( "\n" )
    if expPTRrecord.match( line ) and not expComment.match( line ):
        cols = line.split( )
        key = turnDomain + "." + cols[ 0 ]
        val = ""
        for j, word in enumerate( cols ):
            if word == "PTR":
                mynext = j + 1
                if mynext < len( cols ):
                    val = cols[ mynext ]
                    if val != "":
                        revDict[ key ] = val.strip( "." )

"""
    -----------------------------------------------------------------
    Print the 'reverse' dictionary
    -----------------------------------------------------------------
"""

print( "\n\nReverse entries\n" )
for key, val in sorted( revDict.items( ), key=lambda item: inet_aton( item[0] ) ):
    print( "; {:16s} - {}".format( key, val ) )

"""
    -----------------------------------------------------------------
    Compare both dictionaries for missing entries
    -----------------------------------------------------------------
"""

print( "\n\nDifferent entries\n" )

for k in sorted( set( dirDict.keys() ).union( revDict.keys() ), key=lambda i: inet_aton( i ) ):
    dirValue = dirDict.get( k )
    revValue = revDict.get( k )
    test = revValue == dirValue
    if not test:
        print( "; {:16s} - {:30s} - {}".format( k, dirValue, revValue ) )

""" That's all folks """