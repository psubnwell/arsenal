import re
import csv
import pymongo

import get_weibo

def get_reposts_network(id):
    client = pymongo.MongoClient()
    db = client['weibo']
    collection = db['reposts']

    edges = []

    # info = get_weibo.get_info_by_id(id)
    # source_user = '@' + info['user']['screen_name']
    source_user = '@法制日报'

    for document in collection.find():
        target_user = '@' + document['user']['screen_name']
        raw_text = document['raw_text']
        intermediate_users = re.findall(r'//(@.*?)[:：]', raw_text)
        users = [target_user] + intermediate_users + [source_user]
        for i in range(len(users) - 1):
            # 去除自己转发自己的情形
            if users[i] != users[i+1]:
                edges.append(users[i:i+2][::-1])
            else:
                pass

    with open('test.csv', 'w') as f:
        f_csv = csv.writer(f)
        f_csv.writerows(edges)

if __name__ == '__main__':
    get_reposts_network(4313825890573521)
