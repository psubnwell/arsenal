import os
import sys
import re
import json
import langid
import opencc
import pandas as pd

def convert_chinese(foo, config='zht2zhs.ini'):
    """Conevrt traditional chinese characters to simplified chinese characters.

    Example
    In [1]: convert_chinese('漢字')  # string.
    Out[1]: '汉字'
    In [2]: convert_chinese(['哈爾濱', '工業', '大學'])  # list, tuple, etc.
    Out[2]: ['哈尔滨', '工业', '大学']
    In [3]: convert_chinese('~/Documents/文本.txt', config='zhs2zht.ini')
    Out[3]: 
    (A file named `文本_cht.txt` has been saved under ~/Documents. Notice the `cht` flag behind the file name.)
    """
    if os.path.isfile(foo):  # Foo is a file.
        foo = os.path.expanduser(foo)
        file_name, file_extension = os.path.splitext(foo)  # Split extension.
        dest_lang = config.rstrip('.ini').split('2')[1]
        output_file = file_name + '_' + dest_lang + file_extension

        fin = open(foo, errors='ignore').read()
        with open(output_file, 'w') as fout:
            fout.write(opencc.convert(fin, config=config))
    elif type(foo) == 'str':  # Foo is a string.
        return opencc.convert(foo, config=config)
    else:  # Foo is other data structure, such as list, tuple.
        tmp = json.dumps(foo, ensure_ascii=False)
        tmp = opencc.convert(tmp, config=config)
        return json.loads(tmp)

def extract_language(langlinks_sql, language_code):
    item = re.findall(r'\((\d+),\'(' + language_code + r')\',\'(.*?)\'\)', langlinks_sql)

    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)

    if language_code == 'zh':
        item_nonempty = convert_chinese(item_nonempty)
    return item_nonempty

def extract_id(langlinks_sql, page_id):
    item = re.findall(r'\((' + str(page_id) + r'),\'(.+?)\',\'(.*?)\'\)', langlinks_sql)

    item_nonempty = []
    for i in item:
        if i[2] != '':
            item_nonempty.append(i)

    for i in range(len(item)):
        if item[i][1] == 'zh':
            item[i] = convert_chinese(item[i])
    return item

def extract_title(langlinks_sql, page_title, language_code=None):
    if language_code == None:
        language_code = langid.classify(page_title)[0]
    if language_code == 'zh':
        page_title = convert_chinese(page_title)

    item = extract_language(langlinks_sql, language_code)
    return [i for i in item if i[2] == page_title]

def translate_title(langlinks_sql, title, target_language_code='all'):
    # import langid
    # language_code = langid.classify(title)[0]
    page_id = extract_title(langlinks_sql, title)[0][0]
    item = extract_id(langlinks_sql, page_id)
    if target_language_code == 'all':
        return item
    else:
        return [i for i in item if i[1] == target_language_code]

def id2title(pages_articles_multistream_index_txt, page_id):
    item = re.findall(r'\d+:' + str(page_id) + r':(.*)', 
        pages_articles_multistream_index_txt)
    return item[0]

def title2id(pages_articles_multistream_index_txt, page_title):
    language_code = langid.classify(page_title)[0]
    if language_code == 'zh':
        page_title_zhs = opencc.convert(page_title, config='zht2zhs.ini')
        page_title_zht = opencc.convert(page_title, config='zht2zhs.ini')
        item = re.findall(r'\d+:(\d+):({0}|{1})\n'.format(page_title_zhs, page_title_zht), 
            pages_articles_multistream_index_txt)
    else:
        item = re.findall(r'\d+:(\d+):({0})'.format(page_title), 
            pages_articles_multistream_index_txt)
    return item

def read_wiki(file_path):
    f = open(file_path, errors='ignore').read()
        # The wiki file is not pure UTF-8, so it's better to ignore the error.
    if file_path.split('/')[-1].startswith('zh'):  # Chinese wiki needs convertion.
        f = opencc.convert(f, config='zht2zhs.ini')
    return f


def sql2csv(sql_file):
    """Convert .sql file to .csv file.
    
    Example:
    In [1]:sql2csv('~/Downloads/foo.sql')
    Out[1]:
    (The foo.csv has been saved under ~/Downloads.)
    """
    sys.path.append(os.path.abspath('.')+'/mysqldump-to-csv')
    from mysqldump_to_csv import is_insert, get_values, values_sanity_check, parse_values

    sql_file = os.path.expanduser(sql_file)  # Recoginize the home dir symbol.
    open(sql_file.replace('.sql', '.csv'), 'w')  # Create or empty the output file.

    try:
        for line in open(sql_file, errors='ignore').readlines():
            # Look for an INSERT statement and parse it.
            if is_insert(line):
                values = get_values(line)
                if values_sanity_check(values):
                    parse_values(values, open(sql_file.replace('.sql', '.csv'), 'a'))
    except KeyboardInterrupt:
        sys.exit(0)


def pami_txt2csv(pages_articles_multistream_index_txt_file):
    """Convert pages_articles_multistream_index.txt file to .csv file.
    
    Example:
    In [1]:pami_txt2csv('~/Downloads/zhwiki-20170501-pages-articles-multistream-index.txt')
    Out[1]:
    (The `zhwiki-20170501-pages-articles-multistream-index.csv` has been saved under ~/Downloads.)
    """
    pami_txt_file = os.path.expanduser(pages_articles_multistream_index_txt_file)
    output_buffer = ''
    for line in open(pami_txt_file, errors='ignore').readlines():
        output_buffer += line.replace(':', ',', 2)  # Only replace first two colons.
    with open(pami_txt_file.replace('.txt', '.csv'), 'w') as fout:
        fout.write(output_buffer.strip())


def multilingual_lexicon(lang_list):
    pass


# Convert .sql(SQL dump file) to .csv via MySQL.
# You need have MySQL installed in your system.
def sql2csv_mysql(sql_file, host, user, password, database):
    import os
    import mysql.connector
    import pandas as pd

    cnx = mysql.connector.connect(host=host,
                                  user=user,
                                  password=password,
                                  database=database)
    cur = cnx.cursor()

    os.system('mysql -h {0} -u {1} -p{2} -D {3} < {4}'.format(host, user, password, database, sql_file))
    print('')

    cur.execute('SHOW TABLES')
    table_name = cur.fetchall()[0]

    for table in table_name:
        csv_file = sql_file[:-4] + '_' + table + '.csv'  # Rename the output file suffix.
        df = pd.read_sql('SELECT * FROM {}'.format(table), cnx)
        for col in list(df.columns.values):
            try:
                df[col] = df[col].str.decode('utf-8')
            except:
                pass
        df.to_csv(csv_file)
        cur.execute('DROP TABLES {}'.format(table))


    cur.close()
    cnx.close()





if __name__ == '__main__':
    # pd.read_sql_table('langlinks', open('./zhwiki-20170501-langlinks.sql', errors='ignore'))
    # # The wiki file is not pure UTF-8, so it's better to ignore the error.
    # langlinks_zh = open('./zhwiki-20170501-langlinks.sql', errors='ignore').read()
    # index_zh = open('./zhwiki-20170501-pages-articles-multistream-index.txt', 
    #     errors='ignore').read()

    # langlinks_en = open('./enwiki-20170501-langlinks.sql', errors='ignore').read()

    # print(extract_language(langlinks_zh, 'en')[:10])
    # print(extract_id(langlinks_zh, 7662)[:10])
    # print(extract_title(langlinks_en, '哈尔滨工业大学'))
    # print(translate_title(langlinks_de, '国立交通大学'))
    # print(id2title(index_zh, 425))
    # print(title2id(index_zh, '浙江省'))

    # sql2csv('~/HDD/Datasets/Wikipedia/zhwiki/zhwiki-20170501-redirect.sql')
    # convert_chinese('./test.txt')
    pami_txt2csv('~/HDD/Datasets/Wikipedia/zhwiki/zhwiki-20170501-pages-articles-multistream-index.txt')
