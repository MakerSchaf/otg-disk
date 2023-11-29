
## otg-disk

_otg-disk_ is a shell script that turns your Raspberry Pi into an
ad-hoc _samba_ file server:

 - The default is to run a public password-free file share to allow
   easy file exchange on the network.  Think of a networked USB
   drive.  Read the [Safety Instructions][1].

 - Password protected shares are possible as well.

 - A control directory is created that allows shutting down the device
   by deleting the _shutdown_ file.

 - _minidlnad_ can be run to stream files (from the shares) to DLNA
   clients.

 - _otg-disk_ can also run a local W-Lan hotspot on request or if
   there's no network connection available.

The shell script is complete (no other scripts required), needs no
installation (but can run as _systemd_ service) and stores its
configuration (which is also edited inside the script).  Other
scripts implement optional funtionalities.  Documentation is in the
HTML files.

Although _otg-disk_ is a Linux shell script it will only work on
Raspberry Pis because it makes use of password-free _sudo_ when
needed.

When you have issues connection by USB network check if your host's
interface is set for "local-link" (instead of "dhcp") configuration.
Notice also that it might take 90 seconds from power-on to USB
network.

 [1]: safety-instructions.html (Safety Instructions)

