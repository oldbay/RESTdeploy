#!/bin/bash

/usr/bin/python2 setup_cx.py build
cp -r deploy_rest_server build/exe.linux-$(uname -m)-2.7/
/usr/bin/python2 setup_cx.py bdist

