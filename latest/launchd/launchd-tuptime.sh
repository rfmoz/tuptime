#!/bin/bash

#
# From: https://github.com/freedev/macosx-script-boot-shutdown
#

function shutdown()
{
  /usr/local/bin/tuptime -gx
  exit 0
}

function startup()
{
  /usr/local/bin/tuptime -x
  tail -f /dev/null &
  wait $!
}

trap shutdown SIGTERM
trap shutdown SIGKILL

startup;
