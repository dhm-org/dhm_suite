import re

class CmdParser(object):
    """ Command Parser
    Command syntax is as follows:
       cmd_name param=value param=val1,val2,val3
    """
    def __init__(self):
        pass

    def validate_syntax(self, cmd):
        # Ensure the command is a string
        if not isinstance(cmd, str):
            raise ValueError('cmd must be a string')

    def find_brackets(self,s):
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
        
    def get_value_pairs(self, cmd, root_delimeter=' ', param_delimeter=','):

        if not isinstance(cmd, str):
            raise ValueError('cmd must be a string')

        cmd_dict = {}
        temp1 = cmd.strip().split(';')

        for pp in temp1:
            temp = pp.strip().split(root_delimeter, 1)
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
                    if self.find_brackets(val):
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
        
       
if __name__=="__main__":
    import sys
    print(sys.argv[1:])
    #cmd = ' '.join(sys.argv[1:])
    cmd = 'session name=Santos, description=["This is my description","string two"], wavelength=[5e-9,4e-9]'
    cmd = 'session name=Santos, description=["This is my description","string two"], wavelength=[5e-9]'
    cmd = 'framesource filepath=["path1","path2","path3"]'
    a = CmdParser()
    cmd = a.get_value_pairs(cmd)
    print(cmd)
   
