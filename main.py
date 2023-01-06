import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
import re
import pprint

HOST = 'https://spb.hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&text=python'

def get_headers():
    gh = Headers(browser = 'chrome', os = 'win').generate()
    return gh

def find_words(text):
    pattern = r"(.*django.*flask.*)|(.*flask.*django.*)"
    fw = re.findall(pattern, text, flags = re.I)
    return fw

hh_main_html = requests.get(HOST, headers = get_headers()).text
soup = BeautifulSoup(hh_main_html, features = 'lxml')
vacancy_tag_list = soup.find(class_ = "vacancy-serp-content")
id="a11y-main-content"
vacancies_tags = vacancy_tag_list.find_all('div', class_ = "serp-item")
result_list = []
result_list.clear()

for vacancy in vacancies_tags:
    # ссылка на вакансию
    link_tag = vacancy.find('a', class_ = "serp-item__title")
    link_relative = link_tag['href']
    link = f'https://spb.hh.ru/{link_relative}'
    
    # отбор по словам "Django" и "Flask"
    description = vacancy.find('div', class_ = "g-user-content").text
    if len(find_words(description)) > 0:
        # название вакансии
        title_tag = vacancy.find('a', class_ = "serp-item__title")
        title = title_tag.text
 
        # зарплата
        salary_tag = vacancy.find_next(attrs={'data-qa': 'vacancy-serp__vacancy-compensation', 'class': 'bloko-header-section-3'})
        salary = salary_tag.text
        if salary is None:
            print("Не указано")   
    
        # компания
        company_tag = vacancy.find('div', class_ = "bloko-v-spacing-container bloko-v-spacing-container_base-2")
        company = company_tag.text
    
        # город
        city_tag = vacancy.select_one('.bloko-text[data-qa=vacancy-serp__vacancy-address]')
        city = city_tag.text
    
        result_list.append({
                        'City': city,
                        'Company': company.replace(u"\xa0", " "),
                        'Name': title, 
                        'Salary' : salary.replace('\u202f', " "),
                        'Link': link
                        })    
pprint.pprint(result_list)


with open(r"result_list.json", 'w', encoding='utf-8') as f:
    json.dump(result_list, f, ensure_ascii=False,  indent=2)
    
