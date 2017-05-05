import os
import re

def extract_specific_language(langlinks, language):
    item = re.findall(r'\((\d+),\'(' + language + r')\',\'(.*?)\'\)', langlinks)
    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)
    return item_nonempty[:10]

def extract_specific_identity(langlinks, identity):
    item = re.findall(r'\((' + str(identity) + r'),\'(.+?)\',\'(.*?)\'\)', langlinks)
    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)
    return item_nonempty[:10]

if __name__ == '__main__':
    langlinks = open('./zhwiki-20170501-langlinks.sql', errors='ignore').read()
        # The langlinks file is not pure UTF-8, so it's better to ignore the error.
    print(extract_specific_language(langlinks=langlinks, language='en')[:10])
    print(extract_specific_identity(langlinks=langlinks, identity=7662)[:10])