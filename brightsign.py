#!/usr/bin/python
import sys
import usb.core
import usb.util
import uinput
import time
from array import array

try:
	# hexadecimal vendor and product values
	dev = usb.core.find(idVendor=0x084f, idProduct=0xee05)
	if dev == None:
		print("Could not detect Brigthsign Tochboard")
		raise SystemExit

	# first endpoint
	interface = 0
	endpoint = dev[0][(0,0)][0]

	# if the OS kernel already claimed the device, which is most likely true
	# thanks to http://stackoverflow.com/questions/8218683/pyusb-cannot-set-configuration
	if dev.is_kernel_driver_active(interface) is True:
	  # tell the kernel to detach
	  dev.detach_kernel_driver(interface)
	  # claim the device
	  usb.util.claim_interface(dev, interface)

	keys = {
		'KEY_UP': array('B', [ 2, 0, 85, 92]),
		'KEY_RIGHT': array('B', [ 32, 0, 85, 92]),
		'KEY_DOWN': array('B', [ 128, 0, 85, 92]),
		'KEY_LEFT': array('B', [ 8, 0, 85, 92]),
		'KEY_ENTER': array('B', [ 16, 0, 85, 92]),
		'KEY_ESC': array('B', [ 1, 0, 85, 92]),
		'KEY_VOLUMEUP': array('B', [ 0, 2, 85, 92]),
		'KEY_VOLUMEDOWN': array('B', [ 0, 4, 85, 92]),
		'KEY_RELEASE': array('B', [ 0, 0, 85, 92])
	}
	brightsign_keys = [
		uinput.KEY_UP,
		uinput.KEY_RIGHT,
		uinput.KEY_DOWN,
		uinput.KEY_LEFT,
		uinput.KEY_ENTER,
		uinput.KEY_ESC,
		uinput.KEY_VOLUMEUP,
		uinput.KEY_VOLUMEDOWN
	]

	key_pressed = False
	last_key = "KEY_ESC"
	touchboard = uinput.Device( brightsign_keys )
	while True:
		try:
			data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
			for key, code in keys.items():
				if code == data[0:4]:
					if 'KEY_RELEASE' != key:
						touchboard.emit(eval('uinput.'+key), value=1) # press key
						last_key = key
					else:
						touchboard.emit(eval('uinput.'+last_key), value=0)
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation timed out',):
				continue
finally:
	# release the device
	usb.util.release_interface(dev, interface)
	touchboard.destroy()
	# reattach the device to the OS kernel
	dev.attach_kernel_driver(interface)
