#!/usr/bin/python
import threading
import commands
import click
import time
import argparse
import logging
import logging . handlers
from tabulate import tabulate
o0OO00 = "PORT_ALARM_LED"
oo = o0OO00
i1iII1IiiIiI1 = "/var/log/%s.log" % o0OO00 . lower ( )
iIiiiI1IiI1I1 = 30
o0OoOoOO00 = 3
o0OOO = None
iIiiiI = {
 "100G_SR4_QSFP28" : - 5.3 ,
 "100G_PSM4_QSFP28" : - 7.6 ,
 "100G_CWDM4_QSFP28" : - 6.5 ,
 "100G_LR4_QSFP28" : - 9 ,
 "100G_ER4_QSFP28" : - 17 ,
 "25G_AOC_SFP28" : - 5.3 ,
 "25G_SR_SFP28" : - 5.3
 }
o0oO0 = 3
oo00 = 4
o00 = 6
Oo0oO0ooo = 7
def i1iIIII ( docker , wait_seconds ) :
 I1 = 360 / 3
 O0OoOoo00o = 'docker ps | grep %s' % docker
 try :
  while I1 > 0 :
   OoOooOOOO = commands . getoutput ( O0OoOoo00o )
   i11iiII = OoOooOOOO . splitlines ( )
   for I1iiiiI1iII in i11iiII :
    IiIi11i = I1iiiiI1iII . strip ( ) . split ( )
    if len ( IiIi11i ) == 10 or len ( IiIi11i ) == 11 :
     if IiIi11i [ 8 ] == 'seconds' or IiIi11i [ 8 ] == 'second' :
      if int ( IiIi11i [ 7 ] ) > wait_seconds :
       return True
     elif IiIi11i [ 8 ] == 'minutes' :
      if int ( IiIi11i [ 7 ] * 60 ) > wait_seconds :
       return True
     elif IiIi11i [ 8 ] . startswith ( 'hour' ) or IiIi11i [ 9 ] . startswith ( 'hour' ) :
      return True
     elif IiIi11i [ 8 ] . startswith ( 'day' ) or IiIi11i [ 8 ] . startswith ( 'week' ) or IiIi11i [ 8 ] . startswith ( 'month' ) :
      return True
     else :
      return False
   I1 -= 3
   time . sleep ( 3 )
 except Exception :
  iii11iII ( "wait for docker %s startup failed" % docker )
  return False
 return False
class oOo ( object ) :
 def __init__ ( self , module_name , log_file_name ) :
  self . log = logging . getLogger ( module_name )
  self . log . setLevel ( logging . DEBUG )
  ooOoOoo0O = 4 * 1024 * 1024
  OooO0 = 1
  ooO0o0Oo = logging . handlers . RotatingFileHandler ( log_file_name ,
 maxBytes = ooOoOoo0O ,
 backupCount = OooO0 )
  ooO0o0Oo . setLevel ( logging . DEBUG )
  o0o0oOOOo0oo = logging . Formatter (
 "%(asctime)s - %(name)s - %(levelname)s - %(message)s" )
  ooO0o0Oo . setFormatter ( o0o0oOOOo0oo )
  self . log . addHandler ( ooO0o0Oo )
  self . log_fn_map = { Oo0oO0ooo : self . log . debug ,
 o00 : self . log . info ,
 oo00 : self . log . warning ,
 o0oO0 : self . log . error }
 def sys_log ( self , log_level , info ) :
  if log_level in self . log_fn_map :
   self . log_fn_map [ log_level ] ( info )
def oO ( info ) :
 o0OOO . sys_log ( Oo0oO0ooo , info )
def O0ooOooooO ( info ) :
 o0OOO . sys_log ( o00 , info )
def oo0 ( info ) :
 o0OOO . sys_log ( oo00 , info )
def iii11iII ( info ) :
 o0OOO . sys_log ( o0oO0 , info )
class o0OOoo0OO0OOO ( object ) :
 def __init__ ( self , mgr ) :
  self . sfp_presence = { }
  self . mgr = mgr
 def sfp_update ( self ) :
  O0OoOoo00o = "sudo sfputil show presence"
  oo0OooOOo0 , OoOooOOOO = commands . getstatusoutput ( O0OoOoo00o )
  if oo0OooOOo0 != 0 :
   iii11iII ( "cmd: %s failed" % O0OoOoo00o )
   return
  i11iiII = OoOooOOOO . splitlines ( )
  for I1iiiiI1iII in i11iiII :
   if I1iiiiI1iII . startswith ( "Ethernet" ) :
    IiII1I11i1I1I = I1iiiiI1iII . split ( )
    if I1iiiiI1iII . find ( "Not present" ) != - 1 :
     oO0Oo = "no"
    elif I1iiiiI1iII . find ( "Present" ) != - 1 :
     oO0Oo = "yes"
    else :
     continue
    O0o0 = IiII1I11i1I1I [ 0 ]
    if O0o0 in self . sfp_presence :
     if oO0Oo != self . sfp_presence [ O0o0 ] :
      self . syncup ( O0o0 , oO0Oo )
    else :
     self . syncup ( O0o0 , oO0Oo )
 def sfp_poll ( self ) :
  oO0OOoO0 = { }
  O0OoOoo00o = "sudo sfputil show presence"
  oo0OooOOo0 , OoOooOOOO = commands . getstatusoutput ( O0OoOoo00o )
  if oo0OooOOo0 != 0 :
   return None
  i11iiII = OoOooOOOO . splitlines ( )
  for I1iiiiI1iII in i11iiII :
   if I1iiiiI1iII . startswith ( "Ethernet" ) :
    IiII1I11i1I1I = I1iiiiI1iII . split ( )
    if I1iiiiI1iII . find ( "Not present" ) != - 1 :
     oO0Oo = "no"
    elif I1iiiiI1iII . find ( "Present" ) != - 1 :
     oO0Oo = "yes"
    else :
     continue
    O0o0 = IiII1I11i1I1I [ 0 ]
    oO0OOoO0 [ O0o0 ] = oO0Oo
  iI1ii1Ii = len ( oO0OOoO0 )
  oooo000 = [ 32 , 56 , 128 ]
  if iI1ii1Ii not in oooo000 :
   return None
  return oO0OOoO0
 def syncup ( self , port , presence ) :
  iii11iII ( "sync up: port %s presence %s" % ( port , presence ) )
  self . sfp_presence [ port ] = presence
  self . mgr . handle_sfp_presence ( port , presence )
 def run ( self ) :
  while True :
   self . sfp_update ( )
   time . sleep ( o0OoOoOO00 )
class i1I11i1I ( object ) :
 def __init__ ( self , on_count , on_check_interval , off_period ) :
  self . on_count = on_count
  self . on_check_interval = on_check_interval
  self . off_period = off_period
  self . dom_sync_task_running = False
  self . dom_sync_task = None
  self . sfp_detector = None
  self . alarm_status = { }
  self . admin_status = { }
  self . sfp_present = { }
  self . port_rx_power_low = { }
  self . power_normal_count = { }
  self . reasons = { }
  self . dom_table = { }
  self . port_indice = { }
 def initialize ( self ) :
  self . sfp_detector = o0OOoo0OO0OOO ( self )
  if self . sfp_detector is None :
   iii11iII ( "Failed to create SFP detector." )
   return False
  return self . init_all_ports_status ( )
 def init_all_ports_status ( self ) :
  if not self . update_ports_admin_status ( ) :
   iii11iII ( "Failed to update ports admin status." )
   return False
  i11i1I1 = self . admin_status . keys ( )
  ii1I = "default"
  for O0o0 in i11i1I1 :
   Oo0ooOo0o = self . set_port_alarm_led ( O0o0 , "off" , ii1I )
   if not Oo0ooOo0o :
    self . alarm_status [ O0o0 ] = "on"
   self . power_normal_count [ O0o0 ] = self . off_period
  try :
   o0OO0oOO0O0 = self . sfp_detector . sfp_poll ( )
   if not o0OO0oOO0O0 :
    iii11iII ( "Failed to get sfp initial status" )
    return False
   for O0o0 in i11i1I1 :
    self . handle_sfp_presence ( O0o0 , o0OO0oOO0O0 [ O0o0 ] )
  except Exception as iIi1IIIi1 :
   iii11iII ( "Failed: sfp detector poll failed, %s" % str ( iIi1IIIi1 ) )
   return False
  oO ( "init all ports status done." )
  return True
 def update_ports_admin_status ( self ) :
  O0OoOoo00o = "show interfaces status"
  oo0OooOOo0 , OoOooOOOO = commands . getstatusoutput ( O0OoOoo00o )
  if oo0OooOOo0 != 0 :
   iii11iII ( "Failed to exec: %s" % O0OoOoo00o )
   return False
  i11iiII = OoOooOOOO . splitlines ( )
  if len ( i11iiII ) < 32 + 2 :
   iii11iII ( "Failed: %s outputs length too short." % O0OoOoo00o )
   return False
  OOOOoOoo0O0O0 = - 1
  if not i11iiII [ 0 ] . strip ( ) . startswith ( "Interface" ) :
   if not i11iiII [ 1 ] . strip ( ) . startswith ( "Interface" ) :
    iii11iII ( "Failed: (%s) outputs format invalid" % O0OoOoo00o )
    return False
   OOOOoOoo0O0O0 = 1
  else :
   OOOOoOoo0O0O0 = 0
  IiII1I11i1I1I = i11iiII [ OOOOoOoo0O0O0 ] . split ( )
  IIiIi1iI = - 1
  for i1IiiiI1iI in range ( len ( IiII1I11i1I1I ) ) :
   if IiII1I11i1I1I [ i1IiiiI1iI ] == "Admin" :
    IIiIi1iI = i1IiiiI1iI
    break
  if IIiIi1iI == - 1 :
   iii11iII ( "Failed: %s invalid, Admin not found" % O0OoOoo00o )
   return False
  iii = 0
  for I1iiiiI1iII in i11iiII :
   if I1iiiiI1iII . strip ( ) . startswith ( "Ethernet" ) :
    IiII1I11i1I1I = I1iiiiI1iII . split ( )
    if len ( IiII1I11i1I1I ) < IIiIi1iI :
     iii11iII ( "Failed: line(%s) format invalid" % I1iiiiI1iII )
     return False
    self . admin_status [ IiII1I11i1I1I [ 0 ] ] = IiII1I11i1I1I [ IIiIi1iI ]
    self . port_indice [ IiII1I11i1I1I [ 0 ] ] = iii
    iii += 1
  oooo000 = [ 32 , 56 , 128 ]
  if iii not in oooo000 :
   iii11iII ( "Failed: total updated ports %d not expected" % iii )
   return False
  return True
 def set_port_alarm_led ( self , port , admin_status , reason ) :
  iii11iII ( "Set port %s alarm_led %s, reason %s" % ( port , admin_status , reason ) )
  II111iiiI1Ii = "Ethernet"
  o0O0OOO0Ooo = port . find ( II111iiiI1Ii )
  if o0O0OOO0Ooo == - 1 :
   iii11iII ( "Failed to set port %s alarm to %s" % ( port , admin_status ) )
   return False
  try :
   i1 = int ( port [ o0O0OOO0Ooo + len ( II111iiiI1Ii ) : ] )
  except Exception as iIi1IIIi1 :
   iii11iII ( "Failed to get port from name %s: %s" % ( port , str ( iIi1IIIi1 ) ) )
   return False
  O0OoOoo00o = "sudo port-led %s %d" % ( admin_status , i1 )
  oo0OooOOo0 , I1IiiI = commands . getstatusoutput ( O0OoOoo00o )
  if oo0OooOOo0 != 0 :
   iii11iII ( "Failed to set port %s alarm to %s, %s"
 % ( port , admin_status , I1IiiI ) )
   return False
  self . alarm_status [ port ] = admin_status
  self . reasons [ port ] = reason
  return True
 def show_port_alarm_led_status ( self ) :
  oO00OOoO00 = [ "Port" , "Status" , "Reason" ]
  IiI111111IIII = [ ]
  i11i1I1 = self . alarm_status . keys ( )
  for O0o0 in i11i1I1 :
   IiI111111IIII . append ( [ O0o0 , self . alarm_status [ O0o0 ] ,
 self . reasons [ O0o0 ] ] )
  if len ( IiI111111IIII ) :
   click . echo ( tabulate ( IiI111111IIII , oO00OOoO00 , tablefmt = 'simple' ) )
 def dump_port_alarm_led ( self ) :
  O0OoOoo00o = "sudo port-led show"
  OoOooOOOO = commands . getoutput ( O0OoOoo00o )
  O0ooOooooO ( OoOooOOOO )
 def handle_alarm_led ( self , port_name ) :
  IIi1 = self . port_rx_power_low . get ( port_name )
  if IIi1 :
   if self . alarm_status [ port_name ] == "off" :
    if self . sfp_present [ port_name ] :
     oO ( "rx low, alarm off, set port %s alarm led on"
 % port_name )
     ii1I = "rx power low, sfp present"
     self . set_port_alarm_led ( port_name , "on" , ii1I )
  else :
   if self . alarm_status [ port_name ] == "on" :
    if self . power_normal_count [ port_name ] >= self . off_period :
     ii1I = "rx power normal"
     self . set_port_alarm_led ( port_name , "off" , ii1I )
 def handle_sfp_presence ( self , port , presence ) :
  self . sfp_present [ port ] = presence
  if presence == "yes" :
   self . handle_alarm_led ( port )
  else :
   if self . alarm_status [ port ] == "on" :
    oO ( "port %s plugged out, alarm on, set it off" % port )
    ii1I = "sfp not present"
    self . set_port_alarm_led ( port , "off" , ii1I )
   if port in self . port_rx_power_low :
    self . port_rx_power_low [ port ] = False
   self . power_normal_count [ port ] = self . off_period
 def handle_rx_power_low ( self , port ) :
  self . handle_alarm_led ( port )
 def start_dom_sync_task ( self ) :
  self . dom_sync_task_running = True
  self . dom_sync_task = threading . Thread ( target = self . dom_sync_proc )
  if self . dom_sync_task is None :
   iii11iII ( "Failed to create dom sync task." )
   self . dom_sync_task_running = False
   return False
  self . dom_sync_task . setDaemon ( True )
  self . dom_sync_task . start ( )
  oO ( "dom sync task started" )
  return True
 def update_dom_table ( self ) :
  O0OoOoo00o = "sfputil show eeprom -d"
  oo0OooOOo0 , OoOooOOOO = commands . getstatusoutput ( O0OoOoo00o )
  if oo0OooOOo0 != 0 :
   iii11iII ( "Failed to exec %s" % O0OoOoo00o )
   return
  i11iiII = OoOooOOOO . splitlines ( )
  oOoooo0O0Oo = False
  o00ooO = { }
  OO0OO0O00oO0 = [ ]
  oOI1Ii1I1 = ""
  for I1iiiiI1iII in i11iiII :
   if I1iiiiI1iII . startswith ( "Ethernet" ) :
    oOI1Ii1I1 = I1iiiiI1iII . split ( ) [ 0 ] [ : - 1 ]
    if I1iiiiI1iII . find ( "not detected" ) != - 1 :
     if oOI1Ii1I1 in self . dom_table :
      self . dom_table . pop ( oOI1Ii1I1 )
     continue
    oOoooo0O0Oo = True
    oOI1Ii1I1 = I1iiiiI1iII . split ( ) [ 0 ] [ : - 1 ]
    continue
   elif oOoooo0O0Oo :
    if I1iiiiI1iII == "" :
     oOoooo0O0Oo = False
     o00ooO [ oOI1Ii1I1 ] = OO0OO0O00oO0
     OO0OO0O00oO0 = [ ]
     continue
    OO0OO0O00oO0 . append ( I1iiiiI1iII )
  for O0o0 in o00ooO . keys ( ) :
   IiI1i = o00ooO [ O0o0 ]
   o0O = None
   o00iI = None
   O0O0Oooo0o = None
   oOOoo00O00o = None
   O0O00Oo = None
   oooooo0O000o = None
   OoO = { }
   for ooO0O0O0ooOOO in IiI1i :
    if ooO0O0O0ooOOO . find ( "TypeOfTransceiver" ) != - 1 :
     o0O = ooO0O0O0ooOOO . split ( ) [ 1 ]
    elif ooO0O0O0ooOOO . find ( "RXPower:" ) != - 1 :
     o00iI = ooO0O0O0ooOOO . split ( ) [ 1 ]
    elif ooO0O0O0ooOOO . find ( "RX1Power:" ) != - 1 :
     O0O0Oooo0o = ooO0O0O0ooOOO . split ( ) [ 1 ]
    elif ooO0O0O0ooOOO . find ( "RX2Power:" ) != - 1 :
     oOOoo00O00o = ooO0O0O0ooOOO . split ( ) [ 1 ]
    elif ooO0O0O0ooOOO . find ( "RX3Power:" ) != - 1 :
     O0O00Oo = ooO0O0O0ooOOO . split ( ) [ 1 ]
    elif ooO0O0O0ooOOO . find ( "RX4Power:" ) != - 1 :
     oooooo0O000o = ooO0O0O0ooOOO . split ( ) [ 1 ]
   OoO [ "TypeOfTransceiver" ] = o0O
   if o00iI :
    oOOo0O00o = "MonitorData"
    iIiIi11 = { "RXPower" : o00iI }
    OoO [ oOOo0O00o ] = iIiIi11
   elif O0O0Oooo0o :
    oOOo0O00o = "ChannelMonitorValues"
    iIiIi11 = { "RX1Power" : O0O0Oooo0o ,
 "RX2Power" : oOOoo00O00o ,
 "RX3Power" : O0O00Oo ,
 "RX4Power" : oooooo0O000o }
    OoO [ oOOo0O00o ] = iIiIi11
   else :
    if o0O and o0O . find ( "DAC" ) == - 1 :
     iii11iII ( "Type not recognized: %s" % o0O )
     continue
   self . dom_table [ O0o0 ] = OoO
 def dom_sync_proc ( self ) :
  OOoO = 0
  while self . dom_sync_task_running is True :
   self . update_dom_table ( )
   OO0O000 = { }
   iiIiI1i1 = self . dom_table
   i11i1I1 = iiIiI1i1 . keys ( )
   OOoO = ( OOoO + 1 ) % 10
   if OOoO == 0 :
    oO ( "[DOM sync] ports are:" )
    oO ( i11i1I1 )
   for O0o0 in i11i1I1 :
    if "TypeOfTransceiver" not in iiIiI1i1 [ O0o0 ] :
     self . port_rx_power_low [ O0o0 ] = False
     self . power_normal_count [ O0o0 ] += 1
     oO ( "Port %s TypeOfTransceiver unknown" % O0o0 )
     continue
    o0O = iiIiI1i1 [ O0o0 ] [ "TypeOfTransceiver" ]
    if o0O is None :
     self . port_rx_power_low [ O0o0 ] = False
     self . power_normal_count [ O0o0 ] += 1
     oO ( "Port %s TransceiverType is None" % O0o0 )
     continue
    if o0O in iIiiiI :
     ooooo0O0000oo = iIiiiI [ o0O ]
    else :
     self . port_rx_power_low [ O0o0 ] = False
     self . power_normal_count [ O0o0 ] += 1
     continue
    if "ChannelMonitorValues" in iiIiI1i1 [ O0o0 ] :
     OoOOo0OOoO = iiIiI1i1 [ O0o0 ] [ "ChannelMonitorValues" ]
     ooO0O00Oo0o = False
     OOO = 0
     for oo0o0OO0 in range ( 1 , 5 ) :
      oooO = "RX%dPower" % oo0o0OO0
      if oooO in OoOOo0OOoO :
       o00iI = OoOOo0OOoO [ oooO ]
       if o00iI == "-40.0000dBm" or o00iI == "-infdBm" :
        OOO += 1
       else :
        try :
         o0O0OOO0Ooo = o00iI . find ( "dBm" )
         if o0O0OOO0Ooo == - 1 :
          oO ( "port %s, %s: can not find dBm"
 % ( O0o0 , o00iI ) )
          continue
         o00iI = o00iI [ : o0O0OOO0Ooo ]
         o00iI = float ( o00iI )
         if o00iI < ooooo0O0000oo :
          ooO0O00Oo0o = True
        except ValueError as iiii1 :
         oO ( "port %s channel %d rx power %s "
 "not valid, reason %s"
 % ( O0o0 , oo0o0OO0 , o00iI , str ( iiii1 ) ) )
         continue
     if OOO >= 2 :
      ooO0O00Oo0o = False
     if ooO0O00Oo0o :
      OO0O000 [ O0o0 ] = { "low_thd" : ooooo0O0000oo ,
 "channel" : 4 }
     else :
      self . port_rx_power_low [ O0o0 ] = ooO0O00Oo0o
      self . power_normal_count [ O0o0 ] += 1
      self . handle_rx_power_low ( O0o0 )
    elif "MonitorData" in iiIiI1i1 [ O0o0 ] :
     ooO0O00Oo0o = False
     IIiiIiiI = iiIiI1i1 [ O0o0 ] [ "MonitorData" ]
     if "RXPower" in IIiiIiiI :
      o00iI = IIiiIiiI [ "RXPower" ]
      if o00iI != "-40.0000dBm" and o00iI != "-infdBm" :
       try :
        o0O0OOO0Ooo = o00iI . find ( "dBm" )
        if o0O0OOO0Ooo == - 1 :
         continue
        o00iI = o00iI [ : o0O0OOO0Ooo ]
        o00iI = float ( o00iI )
        if o00iI < ooooo0O0000oo :
         ooO0O00Oo0o = True
       except ValueError as iIi1IIIi1 :
        oO ( "Port %s rx power %s not valid: %s"
 % ( O0o0 , o00iI , str ( iIi1IIIi1 ) ) )
        continue
      if ooO0O00Oo0o :
       OO0O000 [ O0o0 ] = { "low_thd" : ooooo0O0000oo ,
 "channel" : 1 }
      else :
       self . port_rx_power_low [ O0o0 ] = ooO0O00Oo0o
       self . power_normal_count [ O0o0 ] += 1
       self . handle_rx_power_low ( O0o0 )
    else :
     continue
   iiii111II = [ ]
   I11iIiI1I1i11 = [ ]
   OOoooO00o0oo0 = OO0O000 . keys ( )
   IiIi1I1 = 0
   while IiIi1I1 < self . on_count :
    for O0o0 in OOoooO00o0oo0 :
     ooO0O00Oo0o = self . confirm_power_low (
 O0o0 , OO0O000 [ O0o0 ] [ "low_thd" ] ,
 OO0O000 [ O0o0 ] [ "channel" ] )
     if ooO0O00Oo0o :
      if O0o0 not in iiii111II :
       iiii111II . append ( O0o0 )
       self . power_normal_count [ O0o0 ] = 0
     else :
      if O0o0 not in I11iIiI1I1i11 :
       I11iIiI1I1i11 . append ( O0o0 )
       self . power_normal_count [ O0o0 ] += 1
    time . sleep ( self . on_check_interval )
    IiIi1I1 += 1
   for oOOoo0000O0o0 in OOoooO00o0oo0 :
    if oOOoo0000O0o0 not in I11iIiI1I1i11 :
     self . port_rx_power_low [ oOOoo0000O0o0 ] = True
     self . power_normal_count [ oOOoo0000O0o0 ] = 0
    else :
     self . port_rx_power_low [ oOOoo0000O0o0 ] = False
     self . power_normal_count [ oOOoo0000O0o0 ] += 1
    self . handle_alarm_led ( oOOoo0000O0o0 )
  time . sleep ( iIiiiI1IiI1I1 )
 def confirm_power_low ( self , port , low_thd , channel ) :
  O00oOOooo = channel
  OOO = 0
  IIi1 = False
  if channel == 1 :
   iI1iIii11Ii = [ "RXPower" ]
  else :
   iI1iIii11Ii = [ "RX%dPower" % IIi1i1I11Iii for IIi1i1I11Iii in range ( 1 , channel + 1 ) ]
  for oooO in iI1iIii11Ii :
   O0OoOoo00o = 'sudo sfputil show eeprom -d -p %s|grep "%s:"' % ( port , oooO )
   oo0OooOOo0 , OoOooOOOO = commands . getstatusoutput ( O0OoOoo00o )
   if oo0OooOOo0 != 0 :
    if oo0OooOOo0 != 256 :
     oO ( "command %s return %d" % ( O0OoOoo00o , oo0OooOOo0 ) )
    return False
   try :
    i11iiII = OoOooOOOO . splitlines ( )
    I1iiiiI1iII = i11iiII [ 0 ] . strip ( )
    II111iiiI1Ii = "%s: " % oooO
    o0O0OOO0Ooo = I1iiiiI1iII . find ( II111iiiI1Ii )
    if o0O0OOO0Ooo == - 1 :
     oO ( "%s doesn't contain %s" % ( I1iiiiI1iII , oooO ) )
     continue
    ooOo00 = I1iiiiI1iII [ o0O0OOO0Ooo + len ( II111iiiI1Ii ) : ]
    if ooOo00 == "-40.0000dBm" or ooOo00 == "-infdBm" :
     OOO += 1
     continue
    o0O0OOO0Ooo = ooOo00 . find ( "dBm" )
    if o0O0OOO0Ooo == - 1 :
     oO ( "%s doesn't contain dBm" % ooOo00 )
     continue
    o0oO000oo = ooOo00 [ : o0O0OOO0Ooo ]
    o00iI = float ( o0oO000oo )
    if o00iI < low_thd :
     IIi1 = True
   except Exception as iIi1IIIi1 :
    iii11iII ( "Failed to get rx power of port %s: reason %s"
 % ( port , str ( iIi1IIIi1 ) ) )
    continue
  if O00oOOooo == 1 :
   return IIi1
  if OOO >= 2 :
   return False
  return IIi1
 def run ( self ) :
  self . sfp_detector . run ( )
  self . update_ports_admin_status ( )
def iIIII ( ) :
 iIIIiiI1i1i = argparse . ArgumentParser (
 description = '' , version = '1.0.0' ,
 formatter_class = argparse . RawTextHelpFormatter )
 iIIIiiI1i1i . add_argument ( '-c' , '--oncount' , type = int ,
 help = 'confirm count of power low before turn on alarm' ,
 default = 2 )
 iIIIiiI1i1i . add_argument ( '-i' , '--oncheckinterval' , type = int ,
 help = 'interval between confirm check of power low '
 'before turning on alarm' ,
 default = 5 )
 iIIIiiI1i1i . add_argument ( '-p' , '--offperiod' , type = int ,
 help = 'consecutive period of power normal before '
 'turn off alarm' ,
 default = 5 )
 ii1I1i1iiiI = iIIIiiI1i1i . parse_args ( )
 return ii1I1i1iiiI
def I1i11i ( ) :
 global o0OOO
 o0OOO = oOo ( o0OO00 , i1iII1IiiIiI1 )
 ii1I1i1iiiI = iIIII ( )
 if not i1iIIII ( "syncd" , 10 ) :
  iii11iII ( "Failed: syncd not started." )
  exit ( - 1 )
 try :
  O0O0Ooo = i1I11i1I ( ii1I1i1iiiI . oncount , ii1I1i1iiiI . oncheckinterval ,
 ii1I1i1iiiI . offperiod )
 except Exception as iIi1IIIi1 :
  iii11iII ( "Failed: cannot instantiates PortAlarmLedMgr, %s." % str ( iIi1IIIi1 ) )
  exit ( - 2 )
 try :
  if not O0O0Ooo . initialize ( ) :
   iii11iII ( "Failed to initialize PortAlarmLedMgr" )
   exit ( - 3 )
 except Exception as iIi1IIIi1 :
  iii11iII ( "Failed to initialize PortAlarmLedMgr, reason %s." % str ( iIi1IIIi1 ) )
  exit ( - 4 )
 try :
  if not O0O0Ooo . start_dom_sync_task ( ) :
   iii11iII ( "Failed to start dom sync task" )
   exit ( - 5 )
 except Exception as iIi1IIIi1 :
  iii11iII ( "Failed to start dom sync task, reason %s." % str ( iIi1IIIi1 ) )
  exit ( - 6 )
 try :
  O0O0Ooo . run ( )
 except Exception as iIi1IIIi1 :
  iii11iII ( "Failed to run PortAlarmLedMgr, reason is %s" % ( str ( iIi1IIIi1 ) ) )
  exit ( - 7 )
 oO ( "done, about to exit" )
 exit ( 0 )
if __name__ == '__main__' :
 I1i11i ( )
# dd678faae9ac167bc83abf78e5cb2f3f0688d3a3
