from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

"""
Настройки pandas
"""
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.options.display.max_colwidth = 50


"""
Сохранение веб страницы
"""
link = 'https://fallout.fandom.com/ru/wiki/%D0%A1%D1%83%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0_Fallout_4'
r = requests.get(link)
soup = BeautifulSoup(r.content, 'html.parser')

df = pd.DataFrame(columns = ['Вид',"Название", "Ссылка"])

"""
Логика кода по поиску типов существ и ссылок на их разновидности
"""
main_block = soup.find('div', id = 'mw-content-text')
h2 = main_block.find_all('h2')
h3 = main_block.find_all('h3')
h2 = h2[3:]
H = h3 + h2

type_creature = [] # вид существа
name_creature = [] # имя существа
href = [] # ссылка

for i in range(len(H)):
    name_href_creature = H[i].find_next_sibling()
    [type_creature.append(H[i].text.replace('[]','')) for _ in range(len(name_href_creature.find_all("a")))]
    [name_creature.append(name_href_creature.find_all("a")[i].text) for i in range(len(name_href_creature.find_all("a")))]
    [href.append(str("https://fallout.fandom.com") + name_href_creature.find_all("a")[i].get("href")) for i in range(len(name_href_creature.find_all("a")))]


"""
Создание DataFrame c ссылками на разновидности существ
"""
df["Вид"] = type_creature
df["Название"] = name_creature
df["Ссылка"] = href
df.loc[(df.Название == ''), 'Название'] = np.nan
df = df.drop(index = [21,26], axis = 0)
df = df.dropna()
df = df.reset_index()
df['index'] = df.index
df = df.drop(["Название"], axis = 1)

"""
Создание DataFrame c характеристиками существ
"""
df_ = pd.DataFrame(columns = ['Название', "Уровень", "Здоровье", "Восприятие","Очки_Опыта",
                    "Сопротивление_ФизУрон", "Сопротивление_ЭнергоУрон", "Сопротивление_РадУрон", "Сопротивление_ЯдУрону",
                    "Агрессия","Уверенность","Помощь", 'index'])

"""
Логика кода по сбору характеристик для каждого существа
"""
index = 0
for _, row in df['Ссылка'].iteritems():
    r = requests.get(row)
    soup = BeautifulSoup(r.content, 'html.parser')

    main_block = soup.find('div', class_ = 'mw-parser-output')

    name_creature = main_block.find_all('td', class_ = 'va-stats-creature-name')
    parameters = main_block.find_all('table', class_ = 'va-stats-creature-icontable va-stats-creature-layout-4')
    behavior = main_block.find_all('table', class_ = 'va-stats-creature-icontable va-stats-creature-layout-1')

    name_creature_array = [] # названия существ
    parameters_array = [] # параметры существ
    behavior_array = [] # поведения существ

    all_creatures_list = [] # собираем всю информацию в одном списке

    [name_creature_array.append([name_creature[i].find("b").text]) for i in range(len(name_creature))]

    for i in range(len(parameters)):
        parameters_between = []
        feature_parameters = parameters[i].find_all('div', class_ = "va-stats-creature-item")
        [parameters_between.append(feature_parameters[i].text.split(')')[1]) for i in range(len(feature_parameters))]
        parameters_array.append(list(map(str.strip, parameters_between)))

    for i in range(len(behavior)):
        behavior_between = []
        feature_behavior = behavior[i].find_all("div", class_ = "va-stats-creature-item")
        [behavior_between.append(len(feature_behavior[k].find_all("img", alt = "Icon required.png"))) for k in range(len(feature_behavior))]
        behavior_array.append(behavior_between)

    for i in range(len(name_creature_array)):
        all_creatures_list.append(name_creature_array[i])
        [all_creatures_list[i].append(parameters_array[i][k]) for k in range(len(parameters_array[i]))]
        [all_creatures_list[i].append(behavior_array[i][k]) for k in range(len(behavior_array[i]))]
        all_creatures_list[i].append(index)
        df_.loc[len(df_)] = all_creatures_list[i]

    index += 1

"Сохранение DataFrame с характеристиками существ"
creatures = df.merge(df_, how = 'left', on = 'index')
creatures = creatures.drop(["Ссылка",'index'], axis = 1)
creatures = creatures.dropna()
creatures = creatures.reset_index()
creatures = creatures.drop(["index"], axis = 1)
#print(creatures)
creatures.to_csv('creatures.csv', index = True)
