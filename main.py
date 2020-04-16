import requests
from bs4 import BeautifulSoup
import re
import json
import os

def table_parser(html):
    data = list()
    soup = BeautifulSoup(html,'html.parser')
    tables = soup.find_all('table')

    for table in tables:
        thead = table.find('thead')
        heads = [head.text for head in thead.find_all('th')]

        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            table_data = dict()
            for idx, field in enumerate(row.find_all('td')):
                if heads[idx] == 'Name':
                    link = field.find('a', href=True)
                    if link:
                        link = 'https://attack.mitre.org' + link['href']
                    else:
                        link=''
                    table_data.update({'link' : link})

                table_data.update({heads[idx] : field.text.lstrip().rstrip().replace('\n','')})
            data.append(table_data)
            # print('\n')

    return {'related':data.copy()}


def content_parser(html):

    content = dict()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('div',{'class':'card-data'})

    for d in data:
        key = d.text[:d.text.find(':')]
        value = d.text[d.text.find(':')+1:].lstrip().rstrip()

        content.update({key:value})

    return content.copy()


def title_parser(html):

    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find('h1')

    title = data.text.replace('\n','').lstrip().rstrip().replace('/',' and ')

    description = soup.find('div', {'class': 'col-md-8 description-body'})
    # description.text


    return {'title':title, 'descrption': description.text}


def reference_parser(html):

    references = list()
    soup = BeautifulSoup(html, 'html.parser')
    data = soup.find_all('span', {'class':'scite-citation-text'})

    for idx, d in enumerate(data):
        external_link = d.find('a', href=True)

        references.append({'index':idx+1, 'title':d.text.lstrip().rstrip().replace('\n',''), 'external_link': external_link['href'] if external_link else ''})

    return {'references':references.copy()}

def make_json(url):
    apt_json = dict()
    res = requests.get(url)



    title = title_parser(res.text)
    content = content_parser(res.text)
    data = table_parser(res.text)
    references = reference_parser(res.text)

    apt_json.update(title)
    apt_json.update(content)
    apt_json.update(references)
    apt_json.update(data)

    return apt_json.copy()

if __name__=='__main__':


    apt_37 = 'https://attack.mitre.org/groups/G0067/'
    apt_38 = 'https://attack.mitre.org/groups/G0082/'

    links = [apt_37, apt_38]

    for link in links:
        apt_json = make_json(link)
        path = apt_json['title']

        if not os.path.exists(path):
            os.makedirs(path)

        with open('{1}/{0}.json'.format(apt_json['title'],path), 'w') as f:
            f.write(json.dumps(apt_json))



        related_path = path + '/related'
        if not os.path.exists(related_path):
            os.makedirs(related_path)

        for related in apt_json['related']:

            if related['link']:
                related_json = make_json(related['link'])
                with open('{1}/{0}.json'.format(related_json['title'],related_path), 'w') as f:
                    f.write(json.dumps(related_json))

