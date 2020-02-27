"""
###############################################################################
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED.
#  United States Government Sponsorship acknowledged. Any commercial use must be
#  negotiated with the Office of Technology Transfer at the
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software,
#  the user agrees to comply with all applicable U.S. export laws and regulations.
#  User has the responsibility to obtain export licenses, or other export authority
#  as may be required before exporting such information to foreign countries or providing
#  access to foreign persons.
#
#  file:	dhmcommands.py
#  author:	S. Felipe Fregoso
#  description:	Classes for DHM commands
#
###############################################################################
"""
import re
from .command_dictionary_ag import CmdDict

class CommandDictionary():
    """
    Command Dictionary Class
    """
    def __init__(self, root_delimeter=' ', parameter_delimeter=','):
        """
        Constructor
        """
        self._root_delimeter = root_delimeter
        self._parameter_delimeter = parameter_delimeter
        self._cmd_dict = CmdDict

    def get_dict(self):
        """
        Return command dictionary object
        """
        return self._cmd_dict

    def _find_brackets(self, s):
        """
        Find the brackets within a command string
        """
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

    def _seperate_to_value_pairs(self, cmd):
        """
        Return the key value pairs in command string
        """
        cmd_dict = {}
        temp1 = cmd.strip().split(';')

        for pp in temp1:
            temp = pp.strip().split(self._root_delimeter, 1)
            root_cmd = temp[0].lower()
            param_list = temp[1:]
            cmd_dict[root_cmd] = {}

            if not param_list:
                return cmd_dict

            # Character class states to not match the characters withing
            # the brackets: [^,"'] ? matches either once or zero times
            PATTERN = re.compile(r'''
                (     # Start Group 0
                (?:[^,"'\[\]]|"[^"]*"|'[^']*'|\[[^\]]*\])+
                )     # End of Group 0
                ''', re.VERBOSE)

            param_list = PATTERN.split(param_list[0])[1::2]
            print(param_list)
            for p in param_list:
                print(p)
                pv_pair = p.split('=')
                print(len(pv_pair))
                if len(pv_pair) == 2:
                    key = pv_pair[0].replace(' ', '').lower()
                    val = pv_pair[1]
                    if self._find_brackets(val):
                        temp = val
                        for ch in ['[', ']']:
                            if ch in val:
                                val = val.replace(ch, "")
                        val = val.split(',')
                    cmd_dict[root_cmd][key] = val
                elif len(pv_pair) == 1:
                    key = pv_pair[0].replace(' ', '')
                    cmd_dict[root_cmd][key] = None
                else:
                    raise ValueError('Parameter/Value pairs [%s] must be seperated by "="'%(p))

        return cmd_dict

    def _is_in_command_dictionary(self, cmdstr):
        """
        Returns True if command string is found in command dictionary
        """
        found = True
        cmdroot = cmdstr.split(' ', 1)[0].lower()
        try:
            self._cmd_dict[cmdroot]
        except KeyError:
            found = False

        return found

    def validate_command(self, cmdstr):
        """
        Validate the command string
        """

        statusstr = cmdstr

        if not isinstance(cmdstr, str):
            raise ValueError('cmdstr must be a string')

        # Check if in command dictioanry
        if not self._is_in_command_dictionary(cmdstr):
            statusstr += "[%s] not found in command dictionary."%(cmdstr)
            return (None, statusstr)

        ### Seperate the string into command key,value pairs
        # where root key
        cmd_str_dict = self._seperate_to_value_pairs(cmdstr)
        print('cmd_str: ', cmdstr)
        print("cmd_dict: ", cmd_str_dict)

        # Container of new command object that will be built
        cmd_out = {}

        for param, value in cmd_str_dict.items():

            # Container of parameter dictionary that will be built
            param_out = {}
            print('Key: [%s]'%(param))
            print(value)

            ### Check if command key matches that in the command dictionary
            try:
                self._cmd_dict[param] # Used to check if
                for dict_key, _ in self._cmd_dict.items():
                    temp = None
                    if dict_key == param:
                        cmd_out[dict_key] = None
                        for param, val in value.items():
                            tp = self._cmd_dict[dict_key][param]['type'] # Parameter type
                            if tp == float:
                                if val is None:
                                    raise ValueError('Value type expected: %s'%(repr(tp)))
                                # Remove brackets
                                #val = val.replace('[','')
                                #val = val.replace(']','')
                                if self._cmd_dict[dict_key][param]['islist']:
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
                                if val is None:
                                    raise ValueError('Value type expected: %s'%(repr(tp)))
                                if val.lower() == 'true' or\
                                   val.lower() == 'on' or\
                                   val.lower() == 'yes':

                                    temp = True

                                elif val.lower() == 'false' or\
                                     val.lower() == 'off' or\
                                     val.lower() == 'no':

                                    temp = False

                                else:

                                    statusstr = 'Unexpected string for a boolean [%s]. Expect [yes|no, true|false, or on|off]'%(val)
                                    print(statusstr)
                                    return (None, statusstr)
                            elif tp == str:
                                if val is None:
                                    raise ValueError('Value type expected: %s'%(repr(tp)))
                                print('Enumlist: %s'%(repr(self._cmd_dict[dict_key][param]['enumlist'])))
                                if self._cmd_dict[dict_key][param]['enumlist']:
                                    val = val.lower()
                                    enumlist = [s.lower() for s in self._cmd_dict[dict_key][param]['enumlist']]
                                    if val in enumlist:
                                        temp = val
                                    else:
                                        statusstr = 'Value [%s] is not recognized, valid values are [%s].'%(val, repr(enumlist))
                                        print(statusstr)
                                        return (None, statusstr)
                                else:
                                    temp = val
                            elif tp == int:
                                if val is None:
                                    raise ValueError('Value type expected: %s'%(repr(tp)))
                                if self._cmd_dict[dict_key][param]['islist']:
                                    if isinstance(val, list):
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
                        print('Returned command:', cmd_out)

            except (KeyError, ValueError) as err:
                statusstr = 'Error in parameter of [%s] command: [%s]'%(param, repr(err))
                print(statusstr)
                return (None, statusstr)

        return (cmd_out, statusstr)
