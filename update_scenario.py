import re
import os
from shutil import copyfile, rmtree

#Make Result dir
dir = os.path.join('result/')
if not os.path.exists(dir):
    dir = os.mkdir('result/')


#Make newroot tmp dir
dir = os.path.join('newroot/')
if not os.path.exists(dir):
    dir = os.mkdir('newroot/')

#Make replaces dictionary
replaces = {} 

#Distribute Files 
files = [item for item in os.listdir('.') if os.path.isfile(item)]
current_file = os.path.basename(__file__)
input_files_name = []
for item in files:
    #if re.search(r"(.*\.(swp|zip))", item) or re.search(current_file, item) or re.search('chatbot.yaml', item): 
    if re.search(r"(.*\.(swp|zip))", item) or re.search(current_file, item): 
        continue
    if re.search(r"(.*\.sc)", item):
        input_files_name.append(item)
    if re.search(r"([a-zA-Z0-9а-яА-Я-_]*qa.*.yaml)", item):
        qa_yaml = item
        copyfile(item, 'result/' + item)
    else:
        copyfile(item, 'result/' + item)
print(input_files_name)


#Check double roots
#Count roots in file

#Save list of files with new roots for replace list building:
input_files_newroot = []

for file in input_files_name:
    output_file_name = 'newroot/' + file
    with open(output_file_name, 'w', encoding='utf-8') as result_file:
        with open(file, 'r', encoding='utf-8') as input_file:
            inc = 0
            rootinc = 0
            parent_regex = re.compile(r'^(state|theme):\s+(.*)$', re.M)
            doubleroot_regex = re.compile(r'^(state|theme):\s+/\s*$', re.M)
            for line in input_file:
                if re.findall(parent_regex, line): 
                   inc += 1; 
                if re.findall(doubleroot_regex, line):
                   rootinc +=1

#Add new root state with filename
            if inc <= 1:
                print(file + ' contains ' + str(inc) + ' root state. It\'s ok.\n')
                copyfile(file, 'newroot/' + file)
            elif inc > 1 and rootinc == 0:
                print(file + ' contains ' + str(inc) + ' root states')
                input_files_newroot.append(file)
                input_file.seek(0,0)
                newroot = 'state: ' + file[:-3] + '\n    title: ' + file[:-3] + '\n'
                #result_file.write(newroot + '\n')
                content = newroot + '\n'
                for line in input_file:
                    newline = '    ' + line;
                    content += newline
                result_file.write(content)
                print(file + ' fixed\n')

            #NEW! Обработка редких случаев наличия в сценарии не вложенных в рут стейтов на одном уровне с /:
            #Вкладываем такие стейты в рута и записываем в словарь замен путей 'replaces', чтобы впоследствии обновить пути к ним в вызовах и fromState (на практике подобные вызовы мне не встречались, сделано на всякий случай)
            elif inc > 1 and rootinc >= 1:
                print("Double root in the same sc-file detected!")
                roottochild_regex = re.compile(r'^state:\s+[^/]*$', re.M)
                child_regex = re.compile(r'^    state:\s+(.*)$', re.M)
                content = ''
                with open(file, 'r', encoding='utf-8') as input_file:
                    actual_parent = 'false'
                    for line in input_file:
                        if re.findall(roottochild_regex, line):
                            print(line)
                            actual_parent = 'true'
                            parent = line[7:-1]
                            replaces[parent] = '/' + parent
                            print(parent + ' -> ' + replaces[parent])
                        if re.findall(child_regex, line):
                            actual_parent = 'false'
                        if actual_parent == 'true':
                            line = '    ' + line
                        content += line
                    result_file.write(content)
                    print(file + ' with root to child state fixed')

print('Done!\nTo get result open \'newroot\' folder.')

#Make Dictionary of replaces
#Наполняем "словарь замен путей" стейтами, вложенными в нового общего родителя  
#replaces = {} 
actual_parent = 'false'
for file in input_files_newroot:
    with open('newroot/' + file, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            parent_regex = re.compile(r'^state:\s+(.*)$', re.M)
            child_regex = re.compile(r'^    state:\s+(.*)$', re.M)
            if re.findall(parent_regex, line): 
                actual_parent = 'true'
                parent = "/" + line[7:-1]
            
            if actual_parent == 'true':
                if re.findall(child_regex, line):
                    child = '/' + line[11:-1]
                    newchild = parent + '/' + line[11:-1]
                    replaces[child] = newchild
        actual_parent = 'false'
print(replaces)
print('Replaces List is prepared.\nStart replacing.')

#Replace Paths
for file in input_files_name:
    output_file_name = 'result/' + file
    with open(output_file_name, 'w+', encoding='utf-8') as result_file:
        with open('newroot/' + file, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                for key, value in replaces.items(): 
                    path = r"((include:|extend:|fromState =|go[!]*:|=>|->)[\s]+|qa.yaml)" + key + r"(/|[\s]*$)"
 
                    if re.search(path, line):
                        line = re.sub(key + r"(/|[\s]*$)", value + r"\1", line)
                        print(key + ' -> ' + value)
                        print(line)
                result_file.write(line)
    print(output_file_name + ' is prepared.')

#Correct chatbot.yaml
file = 'chatbot.yaml'
output_file_name = 'result/' + file
with open(output_file_name, 'w', encoding='utf-8') as result_file:
    with open(file, 'r', encoding='utf-8') as input_file:
        old_param = r"(^[#\s]*classifier:[\s]*(enabled|disabled))" 
        #new_param = '  #classifier:\n    #weightRB: 0.5 #коэффициент для score\n    #weightML: 0.5 #коэффициент для confidence\n    #classifierType: flat #возможные значения flat|hierarchical'
        new_param = ''
        for line in input_file:
            if re.search(old_param, line):
                line = re.sub(old_param, new_param, line)
                print('\nChatbot.yaml is corrected\n')
            result_file.write(line)

#Correct qa.yaml
file = qa_yaml
output_file_name = 'result/' + file
yaml_state = r"(^#?(\w|\d)+(?<![qa]):[\s|]*$)"

#yaml_state = r"(^[\s#]*.+(?<![qa]):[\s|]*$)"
#tech = r"(^[\s#]*(a|q):[\s]*$)"
tempcontent = "" 
check = 'false'
added_parent = [] 
with open(output_file_name, 'w', encoding='utf-8') as result_file:
    with open(file, 'r', encoding='utf-8') as input_file:
        for line in input_file:
            if re.search(yaml_state, line):
                check = 'false'
                for key, value in replaces.items(): 
                    state = r"(^[\s#]*)" + key[1:] + r"(:[\s]*$)"
                    parent_re = r"(/.*/)"
                    if re.search(state, line):
                        parent = re.findall(parent_re, value)
                        addparent = (str(parent)[3:-3] + ':')
                        if addparent not in added_parent:
                            line = re.sub(line, addparent + '\n    ' + line, line)
                            added_parent.append(addparent)
                        else:
                            line = re.sub(line, '\n    ' + line, line)
                        print(line)
                        check = 'true'
            #    result_file.write(line)
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
            result_file.write(line)
            #tempcontent += line

#        for line in tempcontent:
#            checkspaces = r"(^([\s]*)q:[\s]*$\n\2-)"
#            if re.search(checkspaces, line):
#                check = 'true'
#            elif re.search(yaml_state, line):
#                check = 'false'
#            if check == true:
#                line = re.sub(line, '    ' + line, line)
#            #result_file.write(line)


#Remove tmp folder
rmtree('newroot')

#Enjoy
print('Done!')
print(replaces)
