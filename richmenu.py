# -*- coding: utf-8 -*-
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, PostbackAction

import settings

line_bot_api = LineBotApi(settings.access_token)

# #check rich menu
# richmenus=line_bot_api.get_rich_menu_list()
# print(richmenus)

# #set default rich menu
# url=f'https://api.line.me/v2/bot/user/all/richmenu/{non_id}'
# headers = {
#     'Authorization': 'Bearer ' + settings.access_token
# }
# res=requests.post(url, headers=headers)
# print(res)


# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="with cancel",
    chat_bar_text="メニューを開く・閉じる",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=625, height=843),
        action=PostbackAction(data="{'action':'rich_order'}")),
        RichMenuArea(
            bounds=RichMenuBounds(x=625, y=0, width=625, height=843),
            action=PostbackAction(data="{'action':'rich_cancel'}")),
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=625, height=843),
            action=PostbackAction(data="{'action':'rich_check'}")),
        RichMenuArea(
            bounds=RichMenuBounds(x=1875, y=0, width=625, height=843),
            action=PostbackAction(data="{'action':'rich_menu'}"))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('richmenu/withcancel.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'withcancel_richmenu_id = "{rich_menu_id}"')

# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name="without cancel",
    chat_bar_text="メニューを開く・閉じる",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=834, height=843),
        action=PostbackAction(data="{'action':'rich_order'}")),
        RichMenuArea(
            bounds=RichMenuBounds(x=834, y=0, width=834, height=843),
            action=PostbackAction(data="{'action':'rich_check'}")),
        RichMenuArea(
            bounds=RichMenuBounds(x=1667, y=0, width=834, height=843),
            action=PostbackAction(data="{'action':'rich_menu'}"))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('richmenu/withoutcancel.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'withoutcancel_richmenu_id = "{rich_menu_id}"')



# create richmenu
rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=False,
    name="none",
    chat_bar_text="受付時間外",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
        action=PostbackAction(data="{'action':'rich_none'}"))
    ]
)
rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

# upload image
with open('richmenu/none.png', 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', f)

print(f'none_richmenu_id = "{rich_menu_id}"')
