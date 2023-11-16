#!/bin/sh
#

#
# :title Liste der laufenden Prozesse
# :is-script
#

ps -aux |
awk '
	$11 ~ /^\[/ {
		next;
		}
	
	{
		cmd = $11;
		for (i = 12; i <= NF; i++) {
			cmd = cmd " " $i;
			if (substr($i, "???") > 0)
				break;
			}
			
		printf ("%-10s  %5s %4s %4s %s\n", $1, $2, $3, $4, cmd);
		}'


