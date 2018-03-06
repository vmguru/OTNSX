#!/bin/bash
#
# This script should be initiated by the job engine of OTRS.
#
ticketnr=$1
ticketid=$2

curl -H "Content-Type: application/json" -X POST -d '{"TicketNR":'$ticketnr',"TicketID":'$ticketid'}' http://192.168.178.19:5000
