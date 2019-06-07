import xml.etree.ElementTree as ET
import sys
import os
import datetime

WRITE_AUTOGEN_FILE = True

xmldict = 'telemetry_dictionary.xml'
outfilename = 'telemetry_iface_ag.py'
tree = ET.parse(xmldict)
root = tree.getroot()

try:
    filecontents = ''
    expectedroottagname = 'DhmTelemetryDictionary'
    if root.tag != expectedroottagname:
       raise ValueError('XML file [%s] is invalid format. Root must be named [%s]'%(xmldict, expectedroottagname))
    
    ### Get version of dictionary
    tagname = 'TelemetryStruct'
    _struct = root.findall(tagname)
    if not _struct and len(_struct) != 1:
        raise ValueError('XML file [%s] is invalid format. Expected element [%s]'%(xmldict, tagname))
    
    version = _struct[0].attrib['Version']

    ### Write file header with some imports and empty class
    filecontents += '###############################################################################\n'
    filecontents += '#    %s\n'%(outfilename)
    filecontents += '#\n'
    filecontents += '#    IMPORTANT NOTE:  This file is auto-generated by the script: %s\n'%(os.path.basename(__file__))
    filecontents += '#\n'
    filecontents += '#    Generated on:                 %s\n'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    filecontents += '#    Telemetry dictionary filename:  %s\n'%(xmldict)
    filecontents += '#    Telemetry dictionary version:   %s\n'%(version)
    filecontents += '###############################################################################\n'
    filecontents += '\n'
    filecontents += 'import struct\n'
    filecontents += 'import numpy as np\n'
    filecontents += '\n'
    filecontents += 'class Telemetry_Object(object):\n'
    filecontents += '    pass\n'
    filecontents += '\n'

    padding4 = 4*' '
    padding8 = 2*padding4
    padding12 = 3*padding4
    padding16 = 2*padding8

    ### Build based on the version of dictionary
    if version == '0.1':
        ### Get list of telemetry groupings
        tagname = 'TelemetryList'
        elementname = 'Telemetry'
        _list = root.findall(tagname)[0].findall(elementname) 
        for entry in _list:
            _id = entry.attrib['Id']
            paramlist = entry.findall('Item')

            ### Start the telemetry item class
            filecontents += 'class %s_Telemetry(Telemetry_Object):\n'%(_id)

            ### Build the inner data class
            filecontents += '    class Data(object):\n'
            filecontents += '        def __init__(self):\n'
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])

                valstr = ''
                if _type == 'float':
                    if _maxcount > 1:
                        valstr += '['
                        for i in range(_maxcount):
                            valstr += 'float(0),'
                        valstr += ']'
                    else:
                        valstr += 'float(0)'
                elif _type == 'integer':
                    if _maxcount > 1:
                        valstr += '['
                        for i in range(_maxcount):
                            valstr += 'int(0),'
                        valstr += ']'
                    else:
                        valstr += 'int(0)'
                elif _type == 'boolean':
                    if _maxcount > 1:
                        valstr += '['
                        for i in range(_maxcount):
                            valstr += 'False,'
                        valstr += ']'
                    else:
                        valstr += 'False'
                elif _type == 'enumeration':
                    if _maxcount > 1:
                        valstr += '['
                        for i in range(_maxcount):
                            valstr += '0,'
                        valstr += ']'
                    else:
                        valstr += '0'
                elif _type == 'string':
                    valstr += '""'
                elif _type == 'binary':
                    valstr += '[0 for i in range(%d)]'%(_maxcount)
            
                filecontents += padding12 + 'self.%s = %s\n'%(pid, valstr)
            ### Build __repr__() function
            filecontents += '\n'        
            padding = 8*' '
            filecontents += '        def __repr__(self):\n'
            count = 0
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])
                if _type == 'string':
                    filecontents += '            print("%s: %%s"%%(self.%s.decode()))'%(pid,pid)
                elif _type == 'binary':
                    filecontents += '            print("%s: binary of size %d bytes")'%(pid,_maxcount)
                else:
                    filecontents += '            print("%s: ", self.%s)'%(pid, pid)
                filecontents += '\n' 
            filecontents +='            return ""\n'
            filecontents += '\n'

            ### Build struct format
            structstr = ''
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])
                if _maxcount > 1:
                    structstr += str(_maxcount)

                if _type == 'float':
                    structstr += 'f'
                elif _type == 'integer':
                    structstr += 'i'
                elif _type == 'boolean':
                    structstr += '?'
                elif _type == 'enumeration':
                    structstr += 'H'
                elif _type == 'string' or _type == 'binary':
                    structstr += 's'
         
            ### Fill in the contents of the __init__ function
            filecontents += padding4 + 'def __init__(self):\n'
            filecontents += padding8 + 'self.telemstruct = struct.Struct("%s")\n'%(structstr)
            filecontents += padding8 + 'self.buff = bytearray(struct.calcsize(self.telemstruct.format))\n'
            filecontents += padding8 + 'self.data = self.Data()\n'


            ### Fill in the pack() function contents
            filecontents += padding4 + 'def pack(self):\n'
            filecontents += padding8 + 'self.telemstruct.pack_into(self.buff, 0, \n'

            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])
         
                if _type == 'string':
                    filecontents += 2*padding16
                    filecontents += 'bytes(self.data.%s,encoding="utf-8"),\n'%(pid)
                elif _type == 'binary':
                    filecontents += 2*padding16
                    filecontents += 'bytes(self.data.%s[0:%d]),'%(pid,_maxcount)
                    filecontents += '\n'
             
                else:
                    filecontents += 2*padding16
                    if _maxcount > 1:
                        for i in range(_maxcount):
                            filecontents += 'self.data.%s[%d], '%(pid, i)
                        filecontents += '\n'
                    else:
                        filecontents += 'self.data.%s,\n'%(pid)
            filecontents += '                                '
            filecontents += ')\n'
            filecontents += padding8 + 'return bytes(self.buff)\n'

            ### Build set_values() function inputs
            filecontents += '    def set_values(self, '
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])
                filecontents += '%s, '%(pid)
            filecontents += '):\n\n'

            # Build set_values() function contents
            padding = 8*' '
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])

                if _maxcount > 1 and _type != 'string':
                    valstr = ''
                    filecontents += padding + 'self.data.%s = '%(pid)
                    valstr += '['
                    if _type == 'float':
                        valstr += _maxcount * 'float(0),'
                    elif _type == 'boolean':
                        valstr += _maxcount * 'False,'
                    elif _type == 'integer':
                        valstr += _maxcount * 'int(0),'
                    elif _type == 'enumerate':
                        valstr += _maxcount * '0,'
                    elif _type == 'binary':
                        valstr += '0 for i in range(%d)'%(_maxcount)
                    valstr += ']'
                    filecontents += '%s\n'%(valstr)
                    filecontents += padding + 'if not hasattr(%s, "__iter__"):\n'%(pid)
                    filecontents += padding + '    ' + '%s = [%s]\n'%(pid,pid)
                    filecontents += padding + 'if len(%s) > %d:\n'%(pid, _maxcount)
                    filecontents += padding + '    ' + 'raise ValueError("%s must have no more than %d items in the list.")\n'%(pid, _maxcount)
                    if _type == 'binary':
                        filecontents += padding + 'self.data.%s = %s[:]'%(pid,pid)
                    else:
                        filecontents += padding + 'for i,p in enumerate(%s):\n'%(pid)
                        filecontents += padding + '    ' + 'self.data.%s[i] = p\n'%(pid)
                else:
                    filecontents += padding + 'self.data.%s = %s'%(pid, pid)
                filecontents += '\n'        

            ### Build unpack() function
            filecontents += '\n'        
            padding = 8*' '
            filecontents += '    def unpack_from(self, buff, offset=0):\n'
            filecontents += '        ret = self.telemstruct.unpack_from(buff, offset)\n'
            count = 0
            for p in paramlist:
                pid = p.attrib['Id']
                _type = p.attrib['Type'].lower()
                _bytes = int(p.attrib['Bytes'])
                _maxcount = int(p.attrib['MaxCount'])
                filecontents += '        self.data.%s = '%(pid)
                if _maxcount > 1 and _type != 'string' and _type != 'binary':
                    filecontents += 'list(ret[%d:%d])\n'%(count, count+_maxcount) 
                    count += _maxcount
                else:
                    filecontents += 'ret[%d]\n'%(count) 
                    count += 1
            filecontents +='        return self.data\n'
        filecontents += '\n'

    else:
        raise ValueError('XML file [%s] version [%s] is unsupported.'%(xmlcmddict, version))
    

    if WRITE_AUTOGEN_FILE:
        filecontents += '\n'
        with open(outfilename,'w') as f:
            f.write(filecontents)
        pass

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print('Error building telemetry dictionary: [%s], lineno: %d'%(repr(e), exc_tb.tb_lineno))
    raise e
