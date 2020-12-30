import requests
import time


aki_Key = '809ff396-e26b-411b-bd3a-a7ab1e6d4216'
instance_url = 'https://rest.iad-03.braze.com/messages/send'
external_user_ids = ["james1230@neuqa.com"]
platforms = ["android_push", "apple_push"]
# Style 1
level1 = ['type', 'section', 'section_id']
level2 = ['id', 'content_id']

# Predefined first level page name which should be same as web deeplink
main_pages = ['rapidreplay', 'games', 'videos', 'standings', 'latest', 'NBATVLIVE', 'signin', 'createaccount', 'packages']

# Predefined detail info
video_seoname = 'channels/highlights/7127b96f-9ec7-4e09-b0de-74a4135bc247.nba'
news_id = '2353015'
game_seoname = '20200108/SASBOS'

# Style 3
details = ['news?newsid=2336760', 'video/channels/highlights/7127b96f-9ec7-4e09-b0de-74a4135bc247.nba', 'game/20180118/PHIBOS?gt=8']


def send_request(message, args):
    for platform in platforms:
        params = {"api_key": aki_Key, "external_user_ids": external_user_ids,
                  "messages": {platform: {"alert": message, "extra": args}}}
        res = requests.post(instance_url, json=params)
        print(res.text)


def send_push_notification(key1, value1, key2=None, value2=None, key3=None, value3=None):

    if key1 and key2 and key3:
        args = {key1: value1, key2: value2, key3: value3}
        message = 'Braze-' + key1 + ': ' + value1 + '\n' + key2 + ':' + value2 + ' - ' + key3 + ':' + value3
        send_request(message, args)
        print(message + ' will send.')
    elif key1 and key2 and not key3:
        args = {key1: value1, key2: value2}
        message = 'Braze-' + key1 + ': ' + value1 + '\n' + key2 + ':' + value2
        send_request(message, args)
        print(message + ' will send.')
    elif key1 and not key2 and not key3:
        args = {key1: value1}
        message = 'Braze-' + key1 + ': ' + value1
        send_request(message, args)
        print(message + ' will send.')
    else:
        return 'Sending wrong test values'

    time.sleep(1)


def push_all_main_pages():
    for key1 in level1:
        for key2 in main_pages:
            send_push_notification(key1, key2)


def push_detail_page(detail_name, detail_content):
    # For news detail, it must user newsid as second level key.
    if detail_name == 'news':
        for key1 in level1:
            send_push_notification(key1, detail_name, 'newsid', detail_content)
    else:
        for key1 in level1:
            for key2 in level2:
                send_push_notification(key1, detail_name, key2, detail_content)


def style1():
    # Send deeplink to all mainpage:
    push_all_main_pages()
    # Send deeplink to detail pages(news, game, video):
    push_detail_page('video', video_seoname)
    push_detail_page('game', game_seoname)
    push_detail_page('news', news_id)


def style2():
    # Send deeplink using PUSH_TYPE
    # If using PUSH_TYPE, GAME_ID=id in detail
    send_push_notification('PUSH_TYPE', 'GAMES', 'GAME_DATE', '04/03/2018', 'GAME_ID', '0021701156')
    send_push_notification('PUSH_TYPE', 'NEWS', 'NEWS_ID', news_id)
    send_push_notification('PUSH_TYPE', 'VIDEOS', 'VIDEO_ID', video_seoname)
    send_push_notification('PUSH_TYPE', 'PACKAGES')
    send_push_notification('PUSH_TYPE', 'RAPIDREPLAY')


def style3():
    # Send deeplink using deeplink
    # main pages
    for item in main_pages:
        send_push_notification('deeplink', 'gametime://' + item)
    # detail pages
    for item in details:
        send_push_notification('deeplink', 'gametime://' + item)

def style4():
	send_push_notification('deeplink', 'gametime://account')


if __name__ == '__main__':
    print('Braze Push Notification Starting')
    style4()


