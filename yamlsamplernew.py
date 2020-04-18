import sys
from ruamel.yaml import YAML
import yaml
from pprint import pprint
import csv

#from statelistlist import statelist

#Read list of examples from csv

statelist = []
with open("logs.csv", mode='r', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile, delimiter=';') 
    for row in reader: # each row is a list
        statelist.append(row)
    print(statelist)
    print(len(statelist))
    


levels = {}
pairs = { }
print(len(statelist))




def get_pairs():
    #формирование пар "стейт - примеры"
    for state, question in statelist[start:end]:
        print(start,end)
        #print(state)
        #print(question)
    
        if state in pairs.keys():
            pairs[state].append(question) 
        else:
            pairs[state] = [question]
            levels[state] = state[1:].split('/') 
    print(len(pairs))
    print(len(levels))
    
    
    Dict = { }
    print("Initial nested dictionary") 
    Dict['classes'] = {} 
    
    #Cписок родителей для стейта 
    for state, lst in levels.items():
        q = [] 
        qs = []
        print(pairs[state])
        qsamples = {}
        qsamples['q'] = pairs[state] 
        q.append(qsamples)
    
        for i in range(0, len(lst)):
            print(lst[i])
            parent = lst[i]
            if i == 0: 
                parent1 = lst[i]
                if Dict['classes'].get(parent1) == None:
                    Dict['classes'][parent1] = {}
                if parent1 == lst[-1]:
                    Dict['classes'][parent1]['qs'] = q; 
            if i == 1:
                parent2 = lst[i]
                if Dict['classes'][parent1].get(parent2) == None: 
                    Dict['classes'][parent1][parent2] = {}
                if parent2 == lst[-1]:
                    Dict['classes'][parent1][parent2]['qs'] = q; 
    
            if i == 2:
                parent3 = lst[i]
                if Dict['classes'][parent1][parent2].get(parent3) == None: 
                    Dict['classes'][parent1][parent2][parent3] = {}
                if parent3 == lst[-1]:
                    Dict['classes'][parent1][parent2][parent3]['qs'] = q; 
            if i == 3:
                parent4 = lst[i]
                if Dict['classes'][parent1][parent2][parent3].get(parent4) == None: 
                    Dict['classes'][parent1][parent2][parent3][parent4] = {}
                if parent4 == lst[-1]:
                    Dict['classes'][parent1][parent2][parent3][parent4]['qs'] = q; 


k = int(len(statelist)/50)
#k = 500
e = int(len(statelist)/k)
start = 0
end = k 
for i in range (0, e):
    get_pairs()
    if end + int(len(statelist)%k) < len(statelist):
        start = start + k
        end = end + k
        i = end 
        print(start, end)
    else:
        start = end - k
        end = len(statelist) 
        print(start, end)
#print(Dict)
        
#Запись готового словаря в yaml
yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=4)
yaml.width = 4096
with open('classifier_samples_new.yaml', 'w', encoding='utf-8') as f:
    data = yaml.dump(Dict, f)
