# -*- coding: utf-8 -*-
"""
Created on Thu May  9 13:29:01 2024

@author: AXIm Admin
"""

import source_commands as sc

xcs = sc.XCS("128.40.160.24")

print("reading monitor:")
xcs.send("vacuum_pressure_mbar?")
rec = xcs.receive()
print("vacuum_pressure_mbar = " +rec)

#xcs.send("nanotube_high_voltage=40000")
#xcs.send("generator?")
#xcs.send("nanotube_spotsize=?")
#xcs.send("state=?")

xcs.send('#user')

xcs.send("nanotube_spotsize=1e-6")
rec = xcs.receive()
print("set spotsize " + rec)
assert rec == "ok\n", "failed to set spot size"

xcs.send("state=on")
rec = xcs.receive()
print(rec)
assert rec == "ok\n", "failed to set 'on' state as target"
sc.wait_for_state_transition(xcs)

#xcs.send("state=quickfocus")
#xcs.send("state=fullfocus")
#xcs.send("state=ready")