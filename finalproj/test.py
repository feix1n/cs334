from escpos.printer import Usb
import usb.core
import usb.util

# Vendor and Product IDs from lsusb
VENDOR_ID = 0x0416
PRODUCT_ID = 0x5011

# Find the device
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    raise ValueError("Device not found")

# Detach kernel driver if necessary
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

# Initialize printer (use same endpoints and profile)
p = Usb(VENDOR_ID, PRODUCT_ID, in_ep=0x81, out_ep=0x03, profile="POS-5890")

# Printing
p.text("Hello world!\n")
p.text("This print should work!\n")
p.text("---------------\n\n\n")
p.cut()
