from escpos2.printer import Usb

p = Usb(0x0416, 0x5011)   # vendor_id, product_id
p.text("Hello world!\n")
p.text("This should work!\n")
p.cut()
