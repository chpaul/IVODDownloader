#!/bin/bash
cd "$(dirname "$0")"

rm *-Frag*
find download/ -mtime +2 -exec rm {} \;
