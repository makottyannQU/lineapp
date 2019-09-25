import datetime
import settings


def dateseparate(date):  # date=20190911
    yobi = ["月", "火", "水", "木", "金", "土", "日"]
    date = datetime.datetime.strptime(str(date), '%Y%m%d')
    year = int(date.strftime('%Y'))
    month = int(date.strftime('%m'))
    day = int(date.strftime('%d'))
    week = date.weekday()
    return {'year': year, 'month': month, 'day': day, 'week': yobi[week]}


def date2str(date):
    ds = dateseparate(date)
    return f'{ds["month"]:2d}月{ds["day"]:2d}日({ds["week"]}) '


def text(t):
    json = {
        "type": "text",
        "text": t
    }
    return json


def danger(date):
    json = {
        "type": "text",
        "text": f'※{date2str(date)}のメニューです'
    }
    return json


def order(info):
    columns = []
    for i in info:
        if i['l_stock'] > 0:
            l_text = f'{i["l_price"]}円'
        else:
            l_text = 'なし'
        if i['m_stock'] > 0:
            m_text = f'{i["m_price"]}円'
        else:
            m_text = 'なし'
        if i['s_stock'] > 0:
            s_text = f'{i["s_price"]}円'
        else:
            s_text = 'なし'
        bento_info = {
            "thumbnailImageUrl": i['image_path'],
            "title": i['meal_name'],
            "text": date2str(i['date']),
            "actions": [
                {
                    "type": "postback",
                    "data": "{'action':'order', 'meal_id':'" + i['meal_id'] + "','size': 2,'date':" + str(
                        i['date']) + "}",
                    "label": f"大 {l_text}",
                    # "text": f"『{i['meal_name']}』を注文しました。"
                },
                {
                    "type": "postback",
                    "data": "{'action':'order', 'meal_id':'" + i['meal_id'] + "','size': 1,'date':" + str(
                        i['date']) + "}",
                    "label": f"中 {m_text}",
                    # "text": f"『{i['meal_name']}』を注文しました。"
                },
                {
                    "type": "postback",
                    "data": "{'action':'order', 'meal_id':'" + i['meal_id'] + "','size': 0,'date':" + str(
                        i['date']) + "}",
                    "label": f"小 {s_text}",
                    # "text": f"『{i['meal_name']}』を注文しました。"
                }

            ]
        }
        columns.append(bento_info)

    json = {
        "type": "template",
        "altText": "注文するお弁当の種類とサイズを選んでください。",
        "template": {
            "type": "carousel",
            "actions": [],
            "columns": columns
        }
    }
    return json


def cancel_confirm(cancel_dict):
    if cancel_dict['size'] == 0:
        size = "小"
    elif cancel_dict['size'] == 1:
        size = "中"
    elif cancel_dict['size'] == 2:
        size = "大"
    json = {
        "type": "template",
        "altText": "キャンセル確認",
        "template": {
            "type": "confirm",
            "actions": [
                {
                    "type": "postback",
                    "data": "{'action':'cancelyes', 'date':" + str(cancel_dict['date']) + ", 'meal_id':'" + cancel_dict[
                        'meal_id'] + "', 'size':" + str(cancel_dict['size']) + "}",
                    "label": "はい",
                    "text": "はい"
                },
                {
                    "type": "postback",
                    "data": "{'action':'cancelno'}",
                    "label": "いいえ",
                    "text": "いいえ"
                }
            ],
            "text": f"{date2str(cancel_dict['date'])} の『{cancel_dict['meal_name']}　{size}』をキャンセルしてよろしいですか？"
        }
    }
    return json


def check_order(check_dict):
    if check_dict['size'] == 0:
        size = "小"
    elif check_dict['size'] == 1:
        size = "中"
    elif check_dict['size'] == 2:
        size = "大"
    json = {
        "type": "text",
        "text": f"{date2str(check_dict['date'])} 『{check_dict['meal_name']} {size}』の注文があります。"
    }
    return json


def menu_info(menu_dict):
    menu_list = []
    for day in menu_dict:
        menu_text = date2str(day['date']) + '\n'
        for i in day['meals']:
            menu_text += f'「{i}」'
        menu_list.append(menu_text)

    json = {
        "type": "text",
        "text": '\n'.join(menu_list)
    }
    return json


def enquete_message():
    json = {
        "type": "text",
        "text": '''まこっちゃん弁当では、お客さまとのコミュニケーション向上を図るため簡単なアンケートを実施しております。
回答していただくと、まこっちゃん弁当100円引きクーポンをプレゼントします！

※ご入力いただいた情報は九州大学の個人情報保護規約に基づき、厳重に取り扱います。
https://www.kyushu-u.ac.jp/ja/university/disclosure/privacy/'''
    }
    return json


def enquete_confirm():
    json = {
        "type": "template",
        "altText": "アンケート同意確認",
        "template": {
            "type": "confirm",
            "actions": [
                {
                    "type": "postback",
                    "data": "{'action':'enquete_agree'}",
                    "label": "はい",
                    "text": "はい"
                },
                {
                    "type": "postback",
                    "data": "{'action':'enquete_disagree'}",
                    "label": "いいえ",
                    "text": "いいえ"
                }
            ],
            "text": f"アンケートに答えますか？"
        }
    }
    return json


def enquete2_confirm():
    json = {
        "type": "template",
        "altText": "アンケート再表示確認",
        "template": {
            "type": "confirm",
            "actions": [
                {
                    "type": "postback",
                    "data": "{'action':'enquete2_agree'}",
                    "label": "はい",
                    "text": "はい"
                },
                {
                    "type": "postback",
                    "data": "{'action':'enquete2_disagree'}",
                    "label": "いいえ",
                    "text": "いいえ"
                }
            ],
            "text": f"今後、このアンケートを表示させませんか？"
        }
    }
    return json


def enquete_grade():
    tmp = []
    for k, v in settings.grade.items():
        a = {
            "type": "action",
            "action": {
                "type": "postback",
                "label": k,
                "data": "{'action':'enquete_grade', 'value':" + str(v) + "}",
                # "text": k
            }
        }
        tmp.append(a)

    json = {
        "type": "text",
        "text": "学年を選択してください",
        "quickReply": {
            "items": tmp
        }
    }

    return json


def enquete_department():
    tmp = []
    for k, v in settings.department.items():
        a = {
            "type": "action",
            "action": {
                "type": "postback",
                "label": k,
                "data": "{'action':'enquete_department', 'value':'" + k + "'}",
                # "text": k
            }
        }
        tmp.append(a)

    json = {
        "type": "text",
        "text": "学部を選択してください",
        "quickReply": {
            "items": tmp
        }
    }

    return json


def enquete_course(courselist):
    if 'その他' not in courselist:
        courselist.append('その他')
    tmp = []
    for v in courselist:
        a = {
            "type": "action",
            "action": {
                "type": "postback",
                "label": v,
                "data": "{'action':'enquete_course', 'value':'" + v + "'}",
                # "text": v
            }
        }
        tmp.append(a)

    json = {
        "type": "text",
        "text": "学科を選択してください",
        "quickReply": {
            "items": tmp
        }
    }

    return json


def coupon():
    json = {
        "type": "template",
        "altText": "クーポン",
        "template": {
            "type": "buttons",
            "actions": [
                {
                    "type": "uri",
                    "label": "クーポン",
                    "uri": settings.coupon_uri,
                }
            ],
            "title": "100円引きクーポン",
            "text": "お支払い時にご利用ください"
        }
    }
    return json


if __name__ == '__main__':
    print(order({'id': 'aaa'}))
