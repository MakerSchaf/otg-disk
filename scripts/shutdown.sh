#!/bin/sh
#

#
# :title Shutdown
# :name System ausschalten oder booten
#
# :label reboot Operation:
# :radio reboot --checked shutdown Shutdown
# :radio reboot reboot Reboot computer
#

M=-h
if [ "$reboot" = "reboot" ]; then
    M=-r
    echo rebooting ...
else
    echo shutting down ...
fi

sudo shutdown $M now
echo ok.

