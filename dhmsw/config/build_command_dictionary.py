import xml.etree.ElementTree as ET
import sys
import os
import datetime

WRITE_AUTOGEN_FILE = True

xmlcmddict = 'command_dictionary.xml'
tree = ET.parse(xmlcmddict)
root = tree.getroot()
CmdDict = {}

if WRITE_AUTOGEN_FILE:
    filecontents = ''

try:
    expectedroottagname = 'DhmCommandDictionary'
    if root.tag != expectedroottagname:
       raise ValueError('XML file [%s] is invalid format. Root must be named [%s]'%(xmlcmddict, expectedroottagname))
    
    ### Get version of command dictionary
    cmdstruct = root.findall('CommandStruct')
    if not cmdstruct and len(cmdstruct) != 1:
        raise ValueError('XML file [%s] is invalid format. Expected element [%s]'%(xmlcmddict, 'CommandStruct'))
    
    version = cmdstruct[0].attrib['Version']

    if WRITE_AUTOGEN_FILE:
        filecontents += '"""\n'
        filecontents += '###############################################################################\n'
        filecontents += '#    command_dictionary_ag.py\n'
        filecontents += '#\n'
        filecontents += '#    IMPORTANT NOTE:  This file is auto-generated by the script: %s\n'%(os.path.basename(__file__))
        filecontents += '#\n'
        filecontents += '#    Generated on:                 %s\n'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        filecontents += '#    Command dictionary filename:  %s\n'%(xmlcmddict)
        filecontents += '#    Command dictionary version:   %s\n'%(version)
        filecontents += '###############################################################################\n'
        filecontents += '"""\n'
        filecontents += '\n'
        filecontents += 'CmdDict = {}\n'

    if version == '0.1':
           cmdlist = root.findall('CommandList')[0].findall('Command') 
           for cmd in cmdlist:
               cmdid = cmd.attrib['Id']
               CmdDict[cmdid] = {}
               paramlist = cmd.findall('Parameter')
               if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"] = {}\n'%(cmdid)
               for param in paramlist:
                   ### Parameter ID
                   paramid = param.attrib['Id']
                   CmdDict[cmdid][paramid] = {}
                   if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"] = {}\n'%(cmdid,paramid)
                   _type = param.attrib['Type'].lower()
                   if _type == 'float':
                       CmdDict[cmdid][paramid]['type'] = float
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = float\n'%(cmdid,paramid,'type')
                   elif _type == 'integer':
                       CmdDict[cmdid][paramid]['type'] = int
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = int\n'%(cmdid,paramid,'type')
                   elif _type == 'string' or _type == 'enumeration':
                       CmdDict[cmdid][paramid]['type'] = str
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = str\n'%(cmdid,paramid,'type')
                   elif _type == 'boolean':
                       CmdDict[cmdid][paramid]['type'] = bool
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = bool\n'%(cmdid,paramid,'type')
                   else:
                       raise ValueError('Unsupported type')
                       
                   ### Parameter Max Count
                   maxcount = param.attrib['MaxCount']
                   if maxcount:
                       maxcount = int(maxcount)
                       if maxcount < 1:
                           raise ValueError('MaxCount must be value greater than 0. CommandId=[%s], ParameterId=[%s]'%(cmdid, paramid))
                       elif maxcount > 1:
                           CmdDict[cmdid][paramid]['islist'] = True
                           if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = True\n'%(cmdid,paramid,'islist')
                       else:
                           CmdDict[cmdid][paramid]['islist'] = False
                           if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = False\n'%(cmdid,paramid,'islist')
                       CmdDict[cmdid][paramid]['maxcount'] = maxcount
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = %d\n'%(cmdid,paramid,'maxcount', maxcount)
                   ### Minimum Value
                   minval = param.attrib['MinValue']
                   if minval and CmdDict[cmdid][paramid]['type'] is not str:
                       if minval.lower() == 'yes':
                           minval = True
                       elif minval.lower() == 'no':
                           minval = False
                           if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = False\n'%(cmdid,paramid,'minvalue')
                       else:
                           print(CmdDict[cmdid][paramid]['type'])
                           print(minval)
                           minval = CmdDict[cmdid][paramid]['type'](minval)
                           print(minval)
                       CmdDict[cmdid][paramid]['minvalue'] = minval 
                       if WRITE_AUTOGEN_FILE:
                           if CmdDict[cmdid][paramid]['type'] is bool:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %s\n'%(cmdid,paramid,'minvalue', 'True' if minval else 'False')
                           elif CmdDict[cmdid][paramid]['type'] is int:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %d\n'%(cmdid,paramid,'minvalue', minval)
                           elif CmdDict[cmdid][paramid]['type'] is float:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %g\n'%(cmdid,paramid,'minvalue', minval)
                           elif CmdDict[cmdid][paramid]['type'] is str:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %s\n'%(cmdid,paramid,'minvalue', minval if minval else "")
                   else:
                       CmdDict[cmdid][paramid]['minvalue'] = None
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = None\n'%(cmdid,paramid,'minvalue')
                   ### Maximum Value
                   maxval = param.attrib['MaxValue']
                   if maxval and CmdDict[cmdid][paramid]['type'] is not str:
                       if maxval.lower() == 'yes':
                           maxval = True
                       elif maxval.lower() == 'no':
                           maxval = False
                       else:
                           print(CmdDict[cmdid][paramid]['type'])
                           print(maxval)
                           maxval = CmdDict[cmdid][paramid]['type'](maxval)
                           print(maxval)
                       CmdDict[cmdid][paramid]['maxvalue'] = maxval 
                       if WRITE_AUTOGEN_FILE:
                           if CmdDict[cmdid][paramid]['type'] is bool:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %s\n'%(cmdid,paramid,'maxvalue', 'True' if maxval else 'False')
                           elif CmdDict[cmdid][paramid]['type'] is int:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %d\n'%(cmdid,paramid,'maxvalue', maxval)
                           elif CmdDict[cmdid][paramid]['type'] is float:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = %g\n'%(cmdid,paramid,'maxvalue', maxval)
                           elif CmdDict[cmdid][paramid]['type'] is str:
                               filecontents += 'CmdDict["%s"]["%s"]["%s"] = "%s"\n'%(cmdid,paramid,'maxvalue', maxval if maxval else '')
                   else:
                       CmdDict[cmdid][paramid]['maxvalue'] = None
                       if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = None\n'%(cmdid,paramid,'maxvalue')
                   ### EnumList
                   enumlist = param.attrib['EnumList']
                   CmdDict[cmdid][paramid]['enumlist'] = enumlist.split('|')
                   if WRITE_AUTOGEN_FILE:
                       ee = CmdDict[cmdid][paramid]['enumlist']
                       if len(ee) == 1 and ee[0] == '':
                           filecontents += 'CmdDict["%s"]["%s"]["%s"] = []\n'%(cmdid,paramid,'enumlist')
                       else:
                           filecontents += 'CmdDict["%s"]["%s"]["%s"] = ['%(cmdid,paramid,'enumlist')
                           for e in CmdDict[cmdid][paramid]['enumlist']:
                               filecontents += '"%s", '%(e)
                           filecontents += ']\n'
                       
                   ### Units
                   units = param.attrib['Units']
                   CmdDict[cmdid][paramid]['units'] = units
                   if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = "%s"\n'%(cmdid,paramid,'units', units)
                   ### Description
                   description = param.attrib['Description']
                   CmdDict[cmdid][paramid]['description'] = description
                   if WRITE_AUTOGEN_FILE: filecontents += 'CmdDict["%s"]["%s"]["%s"] = "%s"\n'%(cmdid,paramid,'description', description)
    else:
        raise ValueError('XML file [%s] version [%s] is unsupported.'%(xmlcmddict, version))
    
    print(CmdDict)

    for k,v in CmdDict.items():
        print

    if WRITE_AUTOGEN_FILE:
        filecontents += '\n'
        with open('command_dictionary_ag.py','w') as f:
            f.write(filecontents)

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print('Error building command dictionary: [%s], lineno: %d'%(repr(e), exc_tb.tb_lineno))
    raise e

