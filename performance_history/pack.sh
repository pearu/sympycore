#!/bin/sh

rm -rf sympycore_svn/build
rm -rf sympycore_svn/src
rm -rf sympycore_svn/sympycore
rm -rf sympycore_svn/trunk
rm -f sympycore_svn/setup.py
gzip *.log
gzip */*.pickle

