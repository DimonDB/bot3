from datetime import datetime 
from pprint import pprint
import vk_api
from vk_api.exceptions import VkApiError

from config import acces_token



class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):
        try:
            info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation' 
                            }
                            )
        except VkApiError as e:
            info = {}
            print(f'error = {e}')
            return {
                'name': info['first_name'] + ' ' + info['last_name'],
                'id': info['id'],
                'bdate': info['bdate'] if 'bdate' in info else None,
                'sex': info('sex') if 'sex' in info else None,
                'city': info('city')['title'] if 'city' in info else None,
            }
    
    def search_users(self, params, offset):

        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5

        try:
            users = self.api.method('users.search',
                                {'count': 50,
                                 'offset': 30,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'has_photo': True,
                                }
                            )
        except VkApiError as e:
            users = []
            print(f'error = {e}')

        return [
            {
                'id': user['id'],
                'name': user['first_name'] + ' ' + user['last_name'],
            }
            for user in users
            if user['is_closed'] is False
        ]

    def get_photos(self, user_id):
        try:
            photos = self.api.method('photos.get',
                                 {'owner_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        except VkApiError as e:
            photos = {}
            print(f'error = {e}')

        result = []

        result.extend(
            {
                'owner_id': photo['owner_id'],
                'id': photo['id'],
                'likes': photo['likes']['count'],
                'comments': photo['comments']['count'],
            }
            for photo in photos
        )
        result.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return result[:3]


if __name__ == '__main__':
    bot = VkTools(acces_token)
   # params = bot.get_profile_info()
    #users = bot.serch_users(params)
    #pprint(bot.get_photos(users[2]['id']))
