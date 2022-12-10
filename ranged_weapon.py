from bs4 import BeautifulSoup
import requests
import pandas as pd

"""
Сохранение веб страницы
"""
link = 'https://fallout.fandom.com/ru/wiki/%D0%9E%D1%80%D1%83%D0%B6%D0%B8%D0%B5_Fallout_4#^'
r = requests.get(link)
soup = BeautifulSoup(r.content, 'html.parser')
web_page = soup.find_all('table', class_='va-table va-table-center va-table-full sortable')

"""
Переменные
"""
type_weapon = [] # Тип оружия - сохраненный список
[type_weapon.append(type.text) for type in soup.find_all('li', class_ = "wds-tabs__tab")[:-1]]

all_table = []

"""
Поиск параметров для оружия (дальний бой)
"""
for i in range(2,6):
    items = web_page[i].find_all("tr")
    k = 1
    while k != len(items):
        item = items[k].find_all("td")
        line_weapon = []
        [line_weapon.append(item[i].text.rstrip()) for i in range(len(item))]
        line_weapon.pop(0)
        line_weapon.insert(1, type_weapon[i])
        line_weapon.pop()
        all_table.append(line_weapon)
        k += 1

df = pd.DataFrame(data =all_table,columns = ["Название","Тип_Оружия",'Патроны',"Урон", "Урон_Секунду",'Дальность','Точность', "Магазин_Патронов", "Вес", "Цена"])
df.to_csv('ranged_weapon.csv', index = True)