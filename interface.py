# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from data_store import Tools, engine

class BotInterface():

    def __init__(self,comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token)
        self.longpoll = VkLongPoll(self.interface)
        self.params = None
        self.offset = 0
        self.Tools = Tools()
        self.users = []


    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()
                                }
                                )
        
    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()

                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}, я бот Василий, введите "поиск" и я начну искать Вам пару')
                    #проверка города
                elif self.params['city'] is None:
                    self.message_send(event.user_id, 'Введите название вашего города:')
                    while True:
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['city'] = event.text
                    # проверка возраста
                if self.params['bdate'] is None:
                    self.message_send(event.user_id, 'Введите дату вашего рождения в формате ДД.ММ.ГГГГ:')
                    while True:
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['bdate'] = event.text
                    # Проверка пола
                elif self.params['sex'] is None:
                    self.message_send(event.user_id, 'Введите Ваш пол, где 1 - Женcкий, 2 - Мужской (написать только цифру)')
                    while True:
                        for event in self.longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                self.params['sex'] = event.text
                elif command == 'поиск':
                    users = self.api.search_users(self.params)
                    user = self.users.pop()
                    # проверка анкеты в бд
                    while self.Tools.user_check(event.user_id, user['id']) is True:
                        user = self.users.pop()
                    # добавление анкеты в бд
                    if self.Tools.user_check(event.user_id, user['id']) is False:
                        self.Tools.add_bd_user(event.user_id, user['id'])

                    photos_user = self.api.get_photos(user['id'])                  
                    
                    attachment = ''
                    for num, photo in enumerate(photos_user):
                        attachment += f'photo{photo["owner_id"]}_{photo["id"]}'
                        if num == 2:
                            break
                    self.message_send(event.user_id,
                                      f'Встречайте {user["name"]}',
                                      attachment=attachment
                                      ) 
                elif command == 'пока':
                    self.message_send(event.user_id, 'пока')
                else:
                    self.message_send(event.user_id, 'Я знаю только команды - привет, поиск и пока')



if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()

            

