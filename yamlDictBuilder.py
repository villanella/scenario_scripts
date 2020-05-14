import re
import os
from shutil import copyfile, rmtree
import sys
from ruamel.yaml import YAML
from fromstates import fromstates
from dictmodels import dictmodels
#import yaml
from pprint import pprint

#Distribute Files 
files = [item for item in os.listdir('.') if os.path.isfile(item)]
current_file = os.path.basename(__file__)
input_yaml_files = []
for item in files:
    if re.search(r"(.*(viber|Dict|Dictall).yaml)", item):
        continue
    if re.search(r"(.*qa.*.yaml)", item):
        input_yaml_files.append(item)
print(input_yaml_files)
yamldicts = []



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

Dict = { }
dataSet = [] 
DictSet = { }
DictNew = { }
inused_states = []
#print("Initial nested dictionary") 

#with open(output_file_name, 'w', encoding='utf-8') as result_file:
for file in input_yaml_files:
    print(file)
    #Dict = { }
    regspace = ''
    expDictName = file[0:-5] + 'Dict.yaml'
    with open(file, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            if line.lstrip().startswith('#'):
                #print(line)
                continue
            state_search = re.search(yaml_state, line)
            if state_search:
                if len(state_search.group(2)) <= (len(regspace) + 5):
                    regstate = state_search.group(3)
                    regspace = state_search.group(2)
                    #print(len(regspace))
                    #print("regstate = " + regstate)
                    #print("regspace = '" + regspace + "'")
                    if regstate not in fromstates:
                        #print("inused state - " + regstate)
                        inused_states.append(regstate)
                    Dict[regspace + regstate] = {}
                    DictNew[regstate] = {}
                    DictNew[regstate]['indent'] = regspace
                    check = 'false'
                    q_list = 'false'
            q_search = re.search(yaml_q, line)
            if q_search:
                q_list = 'true'
                Dict[regspace + regstate][regspace + 'q'] = []
                DictNew[regstate]['samples'] = []
                DictSet[regstate] = []
                #print("q: = " + line)
            a_search = re.search(yaml_a, line)
            if a_search:
                q_list = 'false'
            example_search = re.search(yaml_example, line)
            if  example_search and (q_list == 'true'):
                regexample = example_search.group(2)[:-1]
                #print("regexample " + regexample)
                Dict[regspace + regstate][regspace + 'q'].append(regspace + regexample)
                DictNew[regstate]['samples'].append(regexample)
                DictSet[regstate].append(regexample)
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
        #print(DictSet)
        print("словарь готов")
            

#Запись готового словаря в yaml
        yaml = YAML()
        yaml.indent(mapping=4, sequence=4, offset=4)
        yaml.width = 4096
        yaml.default_flow_style = False 
        with open(expDictName, 'w', encoding='utf-8') as f:
            data = yaml.dump(Dict, f)
            yamldicts.append(expDictName)

print(len(DictSet.items()))
#Example Statistics            
samplesToAdd = {}
zeroStates = []
for key, value in DictSet.items():
    samSum = len(DictSet[key])
    #print(key, samSum)
    if key not in inused_states:
        #if (samSum > 0) and (samSum < 20):
        if samSum < 20:
            samplesToAdd[key] = 20-samSum
        if samSum == 0:
            zeroStates.append(key) 
print(len(zeroStates))
print(len(samplesToAdd))

samples = []
with open('samples.txt', 'r', encoding='utf-8') as samples_file:
    for line in samples_file:
        line = re.sub(r"^\s*", '', line)
        samples.append(line)

#Write new samples to New Dict
n = 0
i = 0
for key in samplesToAdd:
    for n in range(samplesToAdd[key]):
        if n < samplesToAdd[key]:
            #print(n, samplesToAdd[key])
            DictNew[key]['samples'].append(samples[i][:-1])
            n+=1
            i = i+1
#print(DictNew)

#Get list of dozapr only
inusedmodels = []
inusedclasses = []
#key_list = list(DictNew.keys())
models_list = list(dictmodels.keys())
classes_list = []
for key, values in dictmodels.items():
    for item in dictmodels[key]:
        classes_list.append(item)
#for model in models_list:
#    if model not in key_list:
#        inusedmodels.append(model)
        

#Get dozapr samples
dozaprsamples = []
with open('dozaprsamples.txt', 'r', encoding='utf-8') as samples_file:
    for line in samples_file:
        line = re.sub(r"^\s*", '', line)
        line = re.sub(':', '', line)
        dozaprsamples.append(line)
#Write new modelpath-samples to New Dict
i = 0
for key, value in dictmodels.items():
    values = dictmodels[key]
    for item in values:
        #print(key, item)
        if item in list(DictNew.keys()):
            try:
                DictNew[item]['modelPath'][key] = [] 
            except KeyError:
                #print("except")
                DictNew[item]['modelPath'] = { } 
                DictNew[item]['modelPath'][key] = [] 
        else:
            DictNew[item] = { } 
            DictNew[item]['modelPath'] = { } 
            DictNew[item]['indent'] = '' 
            #key_list.append(item)
            DictNew[item]['modelPath'][key] = [] 

        n = 0
        while n < 20:
            DictNew[item]['modelPath'][key].append(dozaprsamples[i][:-1])
            n+=1
            i = i+1
        print("Added 20 new dozapr samples:")
        print(key)
        print(DictNew[item]['modelPath'][key])

#Check unused classes and models
key_list = list(DictNew.keys())
for className in classes_list:
    if className not in key_list:
        inusedclasses.append(className)
for model in models_list:
    if model not in key_list:
        inusedmodels.append(model)

i = 0
#Write new classes 
for className in inusedclasses:
    DictNew[className] = {} 
    #DictNew[className]['modelPath'] = {} 
    DictNew[className]['indent'] = '' 
    for key, value in dictmodels.items():
        if className in dictmodels[key]:
            try:
                DictNew[className]['modelPath'][key] = [] 
            except KeyError:
                DictNew[className]['modelPath'] = { } 
                DictNew[className]['modelPath'][key] = [] 

            n = 0
            for n in range(20):
                if n < 20:
                    DictNew[className]['modelPath'][key].append(dozaprsamples[i][:-1])
                    n+=1
                    i = i+1
            print("Added 20 new dozapr samples:")
            print(DictNew[className]['modelPath'][key])




#print(DictNew)

#Add indents to Dict 
DictIndent = { }
for key, value in DictNew.items():
    #print(key)
    indent = DictNew[key]['indent']
    DictIndent[indent + key] = { }
    samps = []
    samps = DictNew[key].get('samples')
    modelsamps = {}
    modelsamps = DictNew[key].get('modelPath')
    #print(type(modelsamps))
    q = []
    if samps:
        for item in samps:
            item = str(indent) + item 
            q.append(item)
        #print(q)
        DictIndent[indent + key][indent + 'qs'] = {}
        DictIndent[indent + key][indent + 'qs'][indent + '- q'] = q 

    if modelsamps:
        #print(type(modelsamps))
        #print(" должен быть Dict")
        qm = {} 
        qm_samples = []
        for model, samples in modelsamps.items():
            #print(model)
            for item in modelsamps[model]:
                item = str(indent) + item
                qm_samples.append(item)
            model = str(indent) + model 
            qm[model] = qm_samples
            #print(type(qm))
            try:
                DictIndent[indent + key][indent + '    - modelPath'][model] = []
            except KeyError:
                DictIndent[indent + key][indent + '    - modelPath'] = { } 
                DictIndent[indent + key][indent + '    - modelPath'][model] = []
                DictIndent[indent + key][indent + '    - modelPath'][model].append(qm_samples)
        modelsamps = 'false'
#print(DictIndent)
    
with open('dataset.yaml', 'w', encoding='utf-8') as dataset:
    data = yaml.dump(DictIndent, dataset)

with open('dataset0.yaml', 'w', encoding='utf-8') as dataset0:
    data = yaml.dump(DictNew, dataset0)


##Write classifier_samples.yaml with real examples
#with open('classifier_samples.yaml', 'w', encoding='utf-8') as classifier_samples:
#    for file in yamldicts:
#        print(file)
#        with open(file, 'r', encoding='utf-8') as input_yaml:
#            for line in input_yaml:
#                #re.sub(r'(^[']|[']$|':|{}), '', line)
#                line = re.sub(r"[,@\'?\$%_#{}\[\]]", "", line)
#                if 'q:' in line:
#                    line = re.sub(r"([\s#]*)q:", r"\1qs:\n\1  q:", line)
#                if re.findall(r"^\s*-([\s]*)(.*)", line):
#                    line = re.sub(r"-([\s]*)(.*)", r"\1- \2", line)
#                #print(line)
#                classifier_samples.write(line)

            
#Write classifier_samples.yaml with added examples
with open('classifier_samples.yaml', 'w', encoding='utf-8') as classifier_samples:
    with open('dataset.yaml', 'r', encoding='utf-8') as input_yaml:
        for line in input_yaml:
            #re.sub(r'(^[']|[']$|':|{}), '', line)
            line = re.sub(r"[@\'\"?\$%#{}\[\]]", "", line)
            #if 'q:' in line:
            #    line = re.sub(r"([\s#]*)q:", r"\1qs:\n\1  q:", line)
            if re.findall(r"^\s*-([\s]*)(.*)", line):
                line = re.sub(r"-([\s]*)(.*)", r"\1- \2", line)
            #if '- modelPath:' in line:
            #    line = line.rstrip(r"\n\s*") 
            #print(line)
            classifier_samples.write(line)

print(inused_states)
print(zeroStates)
print(inusedmodels)
print(inusedclasses)
print(len(inusedclasses))
