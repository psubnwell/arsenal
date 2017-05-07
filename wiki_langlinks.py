import os
import re
import langid

def extract_language_code(langlinks, language_code):
    item = re.findall(r'\((\d+),\'(' + language_code + r')\',\'(.*?)\'\)', langlinks)
    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)
    return item_nonempty

def extract_page_id(langlinks, page_id):
    item = re.findall(r'\((' + str(page_id) + r'),\'(.+?)\',\'(.*?)\'\)', langlinks)
    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)
    return item_nonempty

def extract_title(langlinks, title):
    import langid
    language_code = langid.classify(title)[0]
    item = extract_language_code(langlinks, language_code)
    if language_code == 'zh':
        import opencc
        title_zhs = opencc.convert(title, config='zht2zhs.ini')
        title_zht = opencc.convert(title, config='zhs2zht.ini')
        return [i for i in item if (i[2] == title_zhs or i[2] == title_zht)]
    else:
        return [i for i in item if i[2] == title]

def translate_title(langlinks, title, target_language_code='all'):
    # import langid
    # language_code = langid.classify(title)[0]
    page_id = extract_title(langlinks, title)[0][0]
    item = extract_page_id(langlinks, page_id)
    if target_language_code == 'all':
        return item
    else:
        return [i for i in item if i[1] == target_language_code]

def id2title(pages_articles_multistream_index_txt, page_id):
    item = re.findall(r'\d+:' + str(page_id) + r':(.*)', 
        pages_articles_multistream_index_txt)
    return item[0]

def title2id(pages_articles_multistream_index_txt, page_title):
    import langid
    language_code = langid.classify(page_title)[0]
    if language_code == 'zh':
        import opencc
        page_title_zhs = opencc.convert(page_title, config='zht2zhs.ini')
        page_title_zht = opencc.convert(page_title, config='zht2zhs.ini')
        item = re.findall(r'\d+:(\d+):({0}|{1})\n'.format(page_title_zhs, page_title_zht), 
            pages_articles_multistream_index_txt)
    else:
        item = re.findall(r'\d+:(\d+):({0})'.format(page_title), 
            pages_articles_multistream_index_txt)
    return item

if __name__ == '__main__':
    langlinks_zh = open('./zhwiki-20170501-langlinks.sql', errors='ignore').read()
    langlinks_en = open('./enwiki-20170501-langlinks.sql', errors='ignore').read()
    index_zh = open('./zhwiki-20170501-pages-articles-multistream-index.txt', errors='ignore').read()
        # The langlinks fpipile is not pure UTF-8, so it's better to ignore the error.
    print(extract_language_code(langlinks_zh, 'en')[:10])
    print(extract_page_id(langlinks_zh, 7662)[:10])
    print(extract_title(langlinks_en, '哈尔滨工业大学'))
    print(translate_title(langlinks_de, '国立交通大学'))
    print(id2title(index_zh, 425))
    print(title2id(index_zh, '浙江省'))
