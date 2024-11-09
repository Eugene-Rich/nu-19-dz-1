# Анализ вакансий
import requests

def getvkans(namevak, gorod):

    url = 'https://api.hh.ru/vacancies'

    sh_params = {'text': 'NAME:(' + namevak + ') AND ' + gorod}

    params = sh_params
    params['page'] = 1
    result = requests.get(url, params=params).json()

    msna = {}

    for itms in result['items']:
        emp = itms['employer']
        rabotod = emp['name']
        if 'salary' in itms:
            sal = itms['salary']
            if sal != None:
                zrp = sal['from']
            else:
                zrp = 0
        else:
            zrp = 0

        if zrp != 0 and zrp != None :
            msna[rabotod] = zrp

    sorted_msna = sorted(msna.items(), key=lambda item: item[1])

    return sorted_msna

if __name__ == '__main__':

    lstvak = getvkans('Программист 1С', 'Иркутск')

    print(lstvak)

