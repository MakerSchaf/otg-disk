
2023-12-06

 - Replace *g_ether* with *libcomposite*. 


2023-11-28

 - Fixed support for USB networking under Bookworm.  The right way
   is to configure local-link or DHCP in NetworkManager.  This is
   an option but take really (too) long during startup.  (Booting
   a Raspi Zero is about 90 seconds without a delay in network
   configuration.)  _otg-disk_ can use a (pre-configured) static
   IP address, which is simply set with _ifconfig_.  This is not
   properly documented yet. 


2023-11-23

 - Fixed 2 or 3 mistakes in `--sys-config`.

 - _otg-disk_ does not bring up USB network under Bookworm (Debian
   12).

