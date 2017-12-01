import requests

import xml.etree.ElementTree as ET
import csv
import re
import os


TSA_URL = 'https://www.tsa.gov/travel/security-screening/' \
          'whatcanibring/items.xml'


def fetch_data(url):
    if not os.path.isfile('tsa-items.xml'):
        r = requests.get(TSA_URL)

        with open('tsa-items.xml', 'w') as f:
            for block in r.iter_content(1024):
                f.write(block)


repl = ('<p>', ''), ('</p>', ''), ('\n', ''), ('\r', ''), ('<br>', '')


def handle_none(t):
    if t:
        for r in repl:
            t = t.replace(*r).strip()
        return t
    else:
        return ''


def parse_xml(tsa_xml):

    tree = ET.parse(tsa_xml)
    root = tree.getroot()

    pattern = r'<span.*?>(.+?)</span>'

    with open('tsa.csv', 'w') as f:

        headers = ['name', 'category', 'carryon', 'checked', 'description',
                   'keywords']

        writer = csv.DictWriter(f, fieldnames=headers)

        writer.writeheader()

        for thing in root:
            name = thing.find('Item-Name').text
            category = thing.find('Item-Categories').text
            carryon = re.search(pattern, thing.find('Carry-On-Bags').text).group(1)
            checked = re.search(pattern, thing.find('Checked-Bags').text).group(1)
            description = handle_none(thing.find('Description').text)
            keywords = handle_none(thing.find('Item-Keywords').text)

            if name:
                writer.writerow({
                    'name': name,
                    'category': category,
                    'carryon': carryon,
                    'checked': checked,
                    'description': description,
                    'keywords': keywords
                })


if __name__ == '__main__':
    fetch_data(TSA_URL)
    parse_xml('tsa-items.xml')
