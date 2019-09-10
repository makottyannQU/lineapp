# -*- coding: utf-8 -*-
import requests
import settings

# python -c "import changerichmenu; changerichmenu.withcancel()"

def withcancel():
    url=f'https://api.line.me/v2/bot/user/all/richmenu/{settings.withcancel_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)

def withoutcancel():
    url=f'https://api.line.me/v2/bot/user/all/richmenu/{settings.withoutcancel_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)

def none():
    url=f'https://api.line.me/v2/bot/user/all/richmenu/{settings.none_richmenu_id}'
    headers = {
        'Authorization': 'Bearer ' + settings.access_token
    }
    requests.post(url, headers=headers)

if __name__ == '__main__':
    withcancel()