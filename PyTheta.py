#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# "object oriented" version of camera-summary.py

# pylint: disable=C0111
# ↑プログラムの説明ドキュメントがないよ！というエラーの防止


from __future__ import print_function

import logging
#import six
import sys
import subprocess as sp
import urllib as url #py3ならば、import urllib.parse as url である。
#import os
import glob
import re # バスデバイス文字列を分割するため使用
import gphoto2 as gp


def port_ptpcam(addr):
	#print('debug [{:s}]'.format(addr) )
	bus,dev = re.split('[:,]', addr)[1:]
	#print('debug [{}] [{}]'.format(bus,dev) )
	return "--bus={} --dev={}".format(bus,dev)

def theta_con_init():
	logging.basicConfig(
		format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING
	)
	callback_obj = gp.check_result(gp.use_python_logging() )
	# make a list of all available cameras
	camera_list = []
	for name, addr in gp.check_result(gp.gp_camera_autodetect() ):
		camera_list.append((name, addr))
	if not camera_list:
		print('カメラが何もありません')
		return 1
	camera_list.sort(key=lambda x: x[0])
	# ask user to choose one

	theta_list = []
	for index, (name, addr) in enumerate(camera_list):
		print('[{:d}]:[{:s}] [{:s}]'.format(index, addr, name))

		if (name == "USB PTP Class Camera"):
			print("シータです")
			if( glob.glob('/run/user/1000/gvfs/gphoto2:host=*') ):
				theta_list.append(addr)
				cmd = "/run/user/1000/gvfs/gphoto2:host=%5B"+url.quote(addr)+"%5D"
				print("[{:s}]をアンマウントします".format(cmd) )
				sp.check_output(["gvfs-mount","-u",cmd])
				# cmd = "gvfs-mount -u /run/user/1000/gvfs/mtp:host=%5B"+url.quote(addr)+"%5D"
				# sp.check_output(cmd,shell=True) #こういう書き方もある。
			else:
				print("アンマウント済みです")
				return 1
		else:
			print("シータではないです")
			return 1

	for addr in theta_list:
		print('[{:s}]'.format(addr) )
	return theta_list


def start_capture(theta_list):
	for addr in theta_list:
		# print('debug[{}]'.format(addr) )
		sp.check_output(
			"gphoto2 --set-config movie=1 --port={}".format(addr),
			shell=True
		)

def finish_capture(theta_list):
	for addr in theta_list:
		# print('debug[{}]'.format( port_ptpcam(addr) ) )
		sp.check_output(
			"ptpcam -R 0x1018,0xFFFFFFFF {}".format( port_ptpcam(addr) ),
			shell=True
		)


if __name__ == "__main__":
	sys.exit(theta_con_init())