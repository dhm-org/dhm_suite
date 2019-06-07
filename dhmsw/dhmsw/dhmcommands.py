###############################################################################
#    dhmcommand.py
#
###############################################################################
import re
from .command_dictionary_ag import CmdDict

class CommandDictionary(object):
    def __init__(self, root_delimeter=' ', parameter_delimeter=','):
        self._root_delimeter = root_delimeter
        self._parameter_delimeter = parameter_delimeter
        self._CmdDict = CmdDict

    def _find_brackets(self,s):
        toret = {}
        pstack = []

        for i, c in enumerate(s):
            if c == '[':
                pstack.append(i)
            elif c == ']':
                if len(pstack) == 0:
                    raise IndexError("No matching closing parens at: " + str(i))
                toret[pstack.pop()] = i

        if len(pstack) > 0:
            raise IndexError("No matching opening parens at: " + str(pstack.pop()))

        return toret

    def get_value_pairs(self, cmd):

        cmd_dict = {}
        temp1 = cmd.strip().split(';')

        for pp in temp1:
            temp = pp.strip().split(self._root_delimeter, 1)
            root_cmd = temp[0].lower()
            param_list = temp[1:]
            cmd_dict[root_cmd] = {}

            if not param_list: return cmd_dict

            # Character class states to not match the characters withing the brackets: [^,"']  
            # ? matches either once or zero times
            PATTERN = re.compile(r'''
                (     # Start Group 0
                (?:[^,"'\[\]]|"[^"]*"|'[^']*'|\[[^\]]*\])+
                )     # End of Group 0
                ''', re.VERBOSE)
            #PATTERN = re.compile(r'''((?:[^,"'\[\]]|"[^"]*"|'[^']*'|\[[^\]]*\])+)''')

            param_list = PATTERN.split(param_list[0])[1::2]
            print(param_list)
            for p in param_list:
                print(p)
                pv_pair = p.split('=')
                print(len(pv_pair))
                if len(pv_pair) == 2:
                    key = pv_pair[0].replace(' ','').lower()
                    val = pv_pair[1]
                    if self._find_brackets(val):
                        temp = val
                        for ch in ['[', ']']:
                            if ch in val:
                                val = val.replace(ch,"")
                        val = val.split(',')
                    cmd_dict[root_cmd][key]=val
                elif len(pv_pair) == 1:
                    key = pv_pair[0].replace(' ','')
                    cmd_dict[root_cmd][key]=None
                else:
                    raise ValueError('Parameter/Value pairs [%s] must be seperated by "="'%(p))

        return cmd_dict
    
    def validate_command(self, cmdstr):
        
        statusstr = cmdstr

        if not isinstance(cmdstr, str):
            raise ValueError('cmdstr must be a string')

        # Quick validation
        cmdroot = cmdstr.split(' ', 1)[0].lower()
        try:
            self._CmdDict[cmdroot]
        except KeyError as e:
            statusstr += "'%s' not found in command dictionary."%(cmdroot)
            return (None, statusstr)

        ### Seperate the string into command key,value pairs
        # where root key
        cmd_dict = self.get_value_pairs(cmdstr)
        print('cmd_str: ', cmdstr)
        print("cmd_dict: ", cmd_dict)
        cmd_out = {} #New command that we will build
        for in_k, in_v in cmd_dict.items():
            param_out = {}
            print('Key: [%s]'%(in_k))
            print(in_v)
            ### Check if command key matches that in the command dictionary
            try:
                self._CmdDict[in_k] # Used to check if 
                for dict_key, dict_val in self._CmdDict.items():
                    temp = None
                    if dict_key == in_k:
                        cmd_out[dict_key] = None
                        for param, val in in_v.items():
                            tp = self._CmdDict[dict_key][param]['type'] # Parameter type
                            if tp == float:
                                if val is None: raise ValueError('Value type expected: %s'%(repr(tp)))
                                # Remove brackets
                                #val = val.replace('[','')
                                #val = val.replace(']','')
                                if self._CmdDict[dict_key][param]['islist']:
                                    if type(val) is list:
                                        temp = [float(i) for i in val]
                                        print("Value is a list", temp)
                                    elif ',' in val:
                                        temp = [float(x) for x in val.split(',')]
                                    else:
                                        temp = [float(val)]
                                else:
                                    temp = float(val)
                            elif tp == bool:
                                if val is None: raise ValueError('Value type expected: %s'%(repr(tp)))
                                if 'true' == val.lower() or 'on' == val.lower() or 'yes' == val.lower():
                                    temp = True
                                elif 'false' == val.lower() or 'off' == val.lower() or 'no' == val.lower():
                                    temp = False
                                else:
 
                                    statusstr = 'Unexpected string for a boolean [%s]. Expect [yes|no, true|false, or on|off]'%(val)
                                    print(statusstr)
                                    return (None, statusstr)
                            elif tp == str:
                                if val is None: raise ValueError('Value type expected: %s'%(repr(tp)))
                                print('Enumlist: %s'%(repr(self._CmdDict[dict_key][param]['enumlist'])))
                                if self._CmdDict[dict_key][param]['enumlist']:
                                    val = val.lower()
                                    enumlist = [s.lower() for s in self._CmdDict[dict_key][param]['enumlist']]
                                    if val in enumlist:
                                        temp = val
                                    else:
                                        statusstr = 'Value [%s] is not recognized, valid values are [%s].'%(val, repr(enumlist))
                                        print(statusstr)
                                        return (None, statusstr)
                                else:
                                    temp = val
                            elif tp == int:
                                if val is None: raise ValueError('Value type expected: %s'%(repr(tp)))
                                if self._CmdDict[dict_key][param]['islist']:
                                    if type(val) is list:
                                        temp = [int(i) for i in val]
                                        print("Value is a list", temp)
                                    elif ',' in val:
                                        temp = [int(x) for x in val.split(',')]
                                    else:
                                        temp = [int(val)]
                                else:
                                    temp = int(val)

                            param_out[param] = temp
                            print('Param_out[%s]='%(param), param_out[param], tp)
                            cmd_out[dict_key] = param_out
                        print('Returned command:',cmd_out)

            except (KeyError, ValueError) as e:
                statusstr = 'Error in parameter of [%s] command: [%s]'%(in_k, repr(e))
                print(statusstr)
                return (None, statusstr)
        return (cmd_out, statusstr)
