from __future__ import division
import re
import os
import csv
from shutil import copyfile, rmtree
from statistics import mean, median

#Get list of scenario files 
files = [item for item in os.listdir('.') if os.path.isfile(item)]
input_files_name = []
for item in files:
    if re.search(r"(.*\.sc)", item):
        input_files_name.append(item)
print(input_files_name)
print(len(input_files_name))

#Берем название сценария из названия его папки
scenario_name = os.path.basename(os.getcwd())
output_file_name = scenario_name + '.csv'
print(output_file_name)

def calc_states():
    total = 0
    state_regex = re.compile(r'^\s*(state|theme):\s+([^,#]*).$', re.M)
    for file in input_files_name:
        with open(file, 'r', encoding='utf-8') as input_file:
            count = 0
            for line in input_file:
                if re.findall(state_regex, line): 
                    count += 1 
                    total += 1
        print(file + " contains " + str(count) + " states")
    print("Scenario " + scenario_name + " contains " + str(total) + " states." )
    return total

def count_models():
    total = 0
    state_regex = re.compile(r'^\s*(state|theme):\s+([^,#]*).*$', re.M)
    model_regex = re.compile(r'.*fromState\s*=\s*(.*[^\s#])\s*$', re.M)
    indent_regex = re.compile(r'^(\s*).*$', re.M)
    models = {} 
    statelist = {} 
    for file in input_files_name:
        with open(file, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                #Ignore commented lines:
                if line.lstrip().startswith('#'):
                    continue 
                if re.findall(state_regex, line):
                    indent = re.sub(indent_regex, r'\1', line)
                    indent_key = str(len(indent))
                    state = re.sub(state_regex, r'\2', line)
                    #уборка мусора (\т) :
                    state = state.rstrip('\n')
                    statelist[indent_key] = state
                if re.findall(model_regex, line): 
                    modelpath = re.sub(model_regex, r'\1', line)
                    model = re.sub(r'.*/(.*)', r'\1', modelpath)
                    if model == '':
                        model = '/'
                    if model == '..':
                        if (len(indent)-4) >= 0:
#                            print("текущий стейт - " + state)
                            parent_key = str(len(indent)-4)
#                            print("родительский стейт = " + statelist[parent_key])
                            model = statelist[parent_key]
                        else: 
                            print("Warning: Incorrect fromState in line:\n " + line)

                    if model not in models:
                        models[model] = {}
                        models[model]['patterns'] = 1
                        models[model]['depended_states'] = []
                        models[model]['depended_states'].append(state)
                    else:
                        models[model]['patterns'] +=1
                        if state not in models[model]['depended_states']:    
                            models[model]['depended_states'].append(state)
    return(models)

def count_patterns_by_state():
    state_regex = re.compile(r'^\s*(state|theme):\s+([^,#]*[a-zA-Zа-яА-Я0-9]).*$', re.M)
    model_regex = re.compile(r'.*fromState\s*=\s*(.*[^\s])\s*$', re.M)
    indent_regex = re.compile(r'^(\s*).*$', re.M)
    statelist = {} 
    patterns_by_state = {}
    for file in input_files_name:
        with open(file, 'r', encoding='utf-8') as input_file:
            for line in input_file:
                #Ignore commented lines:
                if line.lstrip().startswith('#'):
                    continue 
                if re.findall(state_regex, line):
                    modelpath = '/'
                    state = re.sub(state_regex, r'\2', line)
                    state = state.rstrip('\n')
                    indent = re.sub(indent_regex, r'\1', line)
                    indent = indent.rstrip('\n')
                    indent_key = str(len(indent))
                    statelist[indent_key] = state
#                    print(statelist[indent_key] + " : " + indent_key + " indents")
                if re.findall(model_regex, line): 
                    modelpath = re.sub(model_regex, r'\1', line)
                    model = re.sub(r'.*/(.*)', r'\1', modelpath)
                    if model == '':
                        model = '/'
                    #Достаем родительский стейт из цепочки стейтов statelist, запрашивая последний стейт на один отступ выше:
                    if model == '..':
                        if (len(indent)-4) >= 0:
                            current_state = statelist[indent_key]
#                            print("текущий стейт - " + current_state + " = " + state)
                            parent_key = str(len(indent)-4)
#                            print("родительский стейт = " + statelist[parent_key])
                            model = statelist[parent_key]
                        else: 
                            print("Warning: Incorrect fromState in line:\n " + line)

                    #Calculate root and non-root patterns by state:
                    if state not in patterns_by_state.keys():
                        patterns_by_state[state] = {}
                        patterns_by_state[state]['root_patterns'] = 0
                        patterns_by_state[state]['nonroot_patterns'] = 0
                    if model == '/':
                        patterns_by_state[state]['root_patterns'] += 1
                    if model != '/':
                        patterns_by_state[state]['nonroot_patterns'] += 1

    print("patterns by state:")
    print(patterns_by_state)
    return patterns_by_state

def calc_stats_by_model():

    #Массив сумм зависимых стейтов на нерутовую модель:
    depended_states_per_nonroot_model_sums = []

    models = count_models() 

    #Сумма зависимых стейтов для рутовой модели
    depended_states_per_root_model_sum = len(models['/']['depended_states'])
    
    for state in models.keys():
        if state != '/':
            depended_states_per_nonroot_model_sums.append(len(models[state]['depended_states']))
    #print(depended_states_per_nonroot_model_sums)
    #print(depended_states_per_root_model_sum)

    models_stats = {}
    models_stats['root'] = depended_states_per_root_model_sum
    models_stats['nonroot'] = {} 
    models_stats['nonroot']['mean'] = round(mean(depended_states_per_nonroot_model_sums), 1)
    models_stats['nonroot']['min'] = min(depended_states_per_nonroot_model_sums)
    models_stats['nonroot']['max'] = max(depended_states_per_nonroot_model_sums)
    models_stats['nonroot']['median'] = median(depended_states_per_nonroot_model_sums)
    return(models_stats)


def calc_stats_by_pattern():
    #Массив сумм нерутовых паттернов на стейт:
    nonroot_patterns_per_state_sums = []

    #Массив сумм рутовых паттернов на стейт 
    root_patterns_per_state_sums = []
    
    patterns_by_state = count_patterns_by_state()

    for state in patterns_by_state.keys():
        nonroot_patterns_per_state_sums.append(patterns_by_state[state]['nonroot_patterns'])
        root_patterns_per_state_sums.append(patterns_by_state[state]['root_patterns'])

    #Запись статистики паттернов на стейт в словарь
    stats_patterns_per_state = {}

    stats_patterns_per_state['root'] = {}
    stats_patterns_per_state['root']['mean'] = round(mean(root_patterns_per_state_sums), 1)
    stats_patterns_per_state['root']['min'] = min(root_patterns_per_state_sums)
    stats_patterns_per_state['root']['max'] = max(root_patterns_per_state_sums)
    stats_patterns_per_state['root']['median'] = int(median(root_patterns_per_state_sums))
    
    stats_patterns_per_state['nonroot'] = {}
    stats_patterns_per_state['nonroot']['mean'] = round(mean(nonroot_patterns_per_state_sums), 1)
    stats_patterns_per_state['nonroot']['min'] = min(nonroot_patterns_per_state_sums)
    stats_patterns_per_state['nonroot']['max'] = max(nonroot_patterns_per_state_sums)
    stats_patterns_per_state['nonroot']['median'] = int(median(nonroot_patterns_per_state_sums))

    return stats_patterns_per_state

#calc_stats_by_pattern()


def get_metrics():

    #Число стейтов
    total_states = calc_states()

    models = count_models()

    print("Статистика по моделям")
    print(models)
    print("models sum = " + str(len(models)))
    print("root states sum = " + str(len(models['/']['depended_states'])))
    
    #Число моделей
    total_models = len(models)

    models_stats = calc_stats_by_model()

    #Число рутовых моделей
    root_states = models_stats['root']
   
    #Число нерутовых моделей: среднее, min, max и медиана
    nonroot_states_mean = models_stats['nonroot']['mean']
    nonroot_states_min = models_stats['nonroot']['min']
    nonroot_states_max = models_stats['nonroot']['max']
    nonroot_states_median = models_stats['nonroot']['median']

    stats_patterns_per_state = calc_stats_by_pattern()

    #Число рутовых паттернов на стейт: среднее, min, max и медиана
    mean_root_patterns_per_state = stats_patterns_per_state['root']['mean'] 
    min_root_patterns_per_state = stats_patterns_per_state['root']['min'] 
    max_root_patterns_per_state = stats_patterns_per_state['root']['max'] 
    median_root_patterns_per_state = stats_patterns_per_state['root']['median'] 

    print("root patterns per state: mean, min, max, median = ")
    print(mean_root_patterns_per_state, min_root_patterns_per_state, max_root_patterns_per_state, median_root_patterns_per_state)

    #Число нерутовых паттернов на стейт: среднее, min, max и медиана
    mean_nonroot_patterns_per_state = stats_patterns_per_state['nonroot']['mean'] 
    min_nonroot_patterns_per_state = stats_patterns_per_state['nonroot']['min'] 
    max_nonroot_patterns_per_state = stats_patterns_per_state['nonroot']['max'] 
    median_nonroot_patterns_per_state = stats_patterns_per_state['nonroot']['median'] 

    print("nonroot patterns per state: mean, min, max, median = ")
    print(mean_nonroot_patterns_per_state, min_nonroot_patterns_per_state, max_nonroot_patterns_per_state, median_nonroot_patterns_per_state)


    with open (output_file_name, 'w', encoding = 'utf-8') as f:
        fnames = ['scenario_name', 'total_states', 'total_models', 'root_states', 'nonroot_states_mean', 'nonroot_states_min', 'nonroot_states_max', 'nonroot_states_median', 'mean_root_patterns_per_state', 'min_root_patterns_per_state', 'max_root_patterns_per_state', 'median_root_patterns_per_state', 'mean_nonroot_patterns_per_state', 'min_nonroot_patterns_per_state', 'max_nonroot_patterns_per_state', 'median_nonroot_patterns_per_state']
        print("Result:")
        print(fnames)
        print(scenario_name, total_states, total_models, root_states, nonroot_states_mean, nonroot_states_min, nonroot_states_max, nonroot_states_median, mean_root_patterns_per_state, min_root_patterns_per_state, max_root_patterns_per_state, median_root_patterns_per_state, mean_nonroot_patterns_per_state, min_nonroot_patterns_per_state, max_nonroot_patterns_per_state, median_nonroot_patterns_per_state)
        writer = csv.DictWriter(f, fieldnames=fnames, delimiter = ';')  
        writer.writeheader()
        writer.writerow({'scenario_name' : scenario_name, 'total_states' : total_states, 'total_models' : total_models, 'root_states' : root_states, 'nonroot_states_mean' : nonroot_states_mean, 'nonroot_states_min' : nonroot_states_min, 'nonroot_states_max' : nonroot_states_max, 'nonroot_states_median' : nonroot_states_median, 'mean_root_patterns_per_state' : mean_root_patterns_per_state, 'min_root_patterns_per_state' : min_root_patterns_per_state, 'max_root_patterns_per_state' : max_root_patterns_per_state, 'median_root_patterns_per_state' : median_root_patterns_per_state, 'mean_nonroot_patterns_per_state' : mean_nonroot_patterns_per_state, 'min_nonroot_patterns_per_state' : min_nonroot_patterns_per_state, 'max_nonroot_patterns_per_state' : max_nonroot_patterns_per_state, 'median_nonroot_patterns_per_state' : median_nonroot_patterns_per_state})

get_metrics()
