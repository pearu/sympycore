# Introduction #

This document describes how to build windows installers
of python packages on Linux. I am using Ubuntu but the instructions
should work with minor modifications for other Linux systems as well.

# Setup #

Install wine:
```
sudo apt-get install wine
```

Install Python to wine:
```
wget http://python.org/ftp/python/2.5.2/python-2.5.2.msi
msiexec /i python-2.5.2.msi
```

Download [Automated MinGW Installer](http://sourceforge.net/project/showfiles.php?group_id=2435&package_id=240780), for example, the MinGW-5.1.3.exe file.

Install Mingw compilers to wine:
```
wine MinGW-5.1.3.exe
#IMPORTANT: Make sure that g++, g77 compilers are checked for install.
```

Fix wine PATH environment variable:
```
regedit
# Lookup "PATH" environment variable and append ";C:\Python25;C:\MinGW\bin" to it.
# The path to "PATH" is "HKEY_LOCAL_MACHINE/System/CurrentControlSet/Control/Session Manager/Environment/PATH".
```

Check that python works from wine:
```
wine python
Python 2.5.2 (r252:60911, Feb 21 2008, 13:11:45) [MSC v.1310 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.
Module readline not available.
>>> 
```

# Building windows installer for python package #

Execute
```
wine python setup.py build_ext --compiler=mingw32 bdist_wininst
# the installer file <package>-<ver>-win32-py2.5.exe is created under dist directory.
```

Test the installer under wine:
```
wine dist/<package>-<ver>-win32-py2.5.exe
wine python
>>> import <package>
```