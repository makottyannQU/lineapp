def order(info):
    json = {'id':info['id']}
    return json


if __name__ == '__main__':
    print(order({'id':'aaa'}))