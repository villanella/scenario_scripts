import re
import os
from shutil import copyfile, rmtree
import sys
from ruamel.yaml import YAML

#Distribute Files 
files = [item for item in os.listdir('.') if os.path.isfile(item)]
current_file = os.path.basename(__file__)
input_yaml_files = []
for item in files:
    if re.search(r"(.*(viber|Dict).yaml)", item):
        continue
    if re.search(r"(.*qa.*.yaml)", item):
        input_yaml_files.append(item)
print(input_yaml_files)



#Build Dict
yaml_state = r"(^([#\s]*)([\w\d\s.-]+)(?<![qa]):\s*$)"
#yaml_indent = r"(^#?\s*)"
yaml_q = r"(^[#\s]*q:\s*)"
yaml_a = r"(^[#\s]*a:\s*)"
yaml_example = r"(^[\s#]*- ([^|]*))"
regspace = ''

tempcontent = "" 
check = 'false'
q_list = 'false'
added_parent = [] 

#Dict = { }
#print("Initial nested dictionary") 

#with open(output_file_name, 'w', encoding='utf-8') as result_file:
for file in input_yaml_files:
    print(file)
    Dict = { }
    regspace = ''
    expDictName = file[0:-5] + 'Dict.yaml'
    with open(file, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            state_search = re.search(yaml_state, line)
            if state_search:
                if len(state_search.group(2)) <= (len(regspace) + 5):
                    regstate = state_search.group(3)
                    regspace = state_search.group(2)
                    #print(len(regspace))
                    #print("regstate = " + regstate)
                    #print("regspace = '" + regspace + "'")
                    Dict[regspace + regstate] = {}
                    #Dict[regspace + regstate]["indent"] = regspace
                    check = 'false'
                    q_list = 'false'
            q_search = re.search(yaml_q, line)
            if q_search:
                q_list = 'true'
                Dict[regspace + regstate][regspace + 'q'] = []
                #print("q: = " + line)
            a_search = re.search(yaml_a, line)
            if a_search:
                q_list = 'false'
            example_search = re.search(yaml_example, line)
            if  example_search and (q_list == 'true'):
                regexample = example_search.group(2)[:-1]
                #print("regexample " + regexample)
                Dict[regspace + regstate][regspace + 'q'].append(regspace + regexample)
            else:
                if check == 'true':
                    #странно обрабатываются некоторые символы, поэтому такой костыль
                    if '- |' in line:
                        line = '  ' + line.rstrip('- |') 
                    elif '|' in line:
                        line = '    ' + line.rstrip('|')
                    elif '?' in line:
                        line = '    ' + line.rstrip('?')
                    elif '(' in line:
                        line = '    ' + line.rstrip('(')
                    elif ')' in line:
                        line = '    ' + line.rstrip(')')
                    elif '+' in line:
                        line = '    ' + line.rstrip('+')
                    elif '*' in line:
                        line = '    ' + line.rstrip('*')
                    elif '{' in line:
                        line = '    ' + line.rstrip('{')
                    elif '}' in line:
                        line = '    ' + line.rstrip('}')
                    else:
                        line = re.sub(line, '    ' + line, line)
#            result_file.write(line)
        print(Dict)
        print("словарь готов")
            

#Запись готового словаря в yaml
        yaml = YAML()
        yaml.indent(mapping=4, sequence=4, offset=4)
        yaml.width = 4096
        yaml.default_flow_style = False 
        with open(expDictName, 'w', encoding='utf-8') as f:
            data = yaml.dump(Dict, f)
            

            
