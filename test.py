import requests
from bs4 import BeautifulSoup
from tkinter import *
import pyshorteners
from PIL import Image, ImageTk
from io import BytesIO
from tkinter import ttk

s = pyshorteners.Shortener()

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}


class Dotabuffparser():
    def __init__(self, master):
        self.master = master
        self.id = ''
        self.link = ''

        # tab1
        self.nick = ''
        self.rank = ''
        self.winrate = ''
        self.last_game = ''
        self.wins = ''
        self.losses = ''
        self.abandons = ''
        self.all_matches = ''
        self.avatar_url = ''
        # tab2
        self.print_hero = ''
        self.top_heroes_list = []

        self.create_widgets()

    def create_widgets(self):
        # Вкладки
        self.notebook = ttk.Notebook(root) # Создаем Notebook
        self.notebook.pack(fill='both', expand=True)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Основная информация')
        self.notebook.add(self.tab2, text='Список героев')
        # Лейблы
        self.label_input = Label(root, text='Введите айди аккаунта из доты')
        self.label_input.pack()
        # Поле ввода ссылки
        self.input_link = Entry()
        self.input_link.config(width=30)
        self.input_link.pack()
        # Кнопка для получения информации об аккаунте
        self.get_button = Button(self.master, text='Получить информацию', command=self.get_account)
        self.get_button.pack()
        # Лейблы для tab1
        self.nickname_label = Label(self.tab1, text='')
        self.rank_label = Label(self.tab1, text='')
        self.winrate_label = Label(self.tab1, text='')
        self.lastgame_label = Label(self.tab1, text='')
        self.wins_label = Label(self.tab1, text='')
        self.losses_label = Label(self.tab1, text='')
        self.abandons_label = Label(self.tab1, text='')
        self.matches_label = Label(self.tab1, text='')
        self.avatar_label = Label(self.tab1, text='')

    def get_account(self):
        self.link = self.input_link.get()  # Получаем ссылку из поля ввода
        try:
            player_profile_url = 'https://www.dotabuff.com/players/' + self.link
            # Отправляем запрос на сайт
            response = requests.get(player_profile_url, headers=header)

            # Используем BeautifulSoup для парсинга HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            profile_table1 = soup.find('div', class_='header-content-secondary')
            rows = profile_table1.find_all('dl')

            # ник
            self.nick = soup.find('div', class_='header-content-title').get_text()
            if "Overview" in self.nick:
                self.nick = self.nick.replace('Overview', '').strip()

            # ранг
            self.rank = soup.find('div', class_='rank-tier-wrapper')['title'].split(': ')[1]

            for row in rows:
                cols = profile_table1.find_all('dd')
                self.last_game = cols[0].text.strip()  # последняя игра
                self.stats = cols[1].text.split(
                    '-')  # победы-поражения-покинуты. Собираем в список и раскидываем по переменным
                self.winrate = cols[2].text.strip()  # винрейт аккаунта

                self.wins = self.stats[0].strip()  # победы
                self.losses = self.stats[1].strip()  # поражения
                self.abandons = self.stats[2].strip()  # покинуты

            # общее кол-во матчей
            self.all_matches = int(self.wins) + int(self.losses) + int(self.abandons)

            # аватарка аккаунта
            avatar_element = soup.find('div', class_='header-content-avatar')
            self.avatar_url = avatar_element.find("img")["src"]
            self.avatar_url = s.tinyurl.short(self.avatar_url)

            # Вывод результата
            self.nickname_label.config(text=f'Никнейм: {self.nick}')
            self.nickname_label.pack()
            self.rank_label.config(text=f'Ранг: {self.rank}')
            self.rank_label.pack()
            self.winrate_label.config(text=f'Винрейт: {self.winrate}')
            self.wins_label.pack()
            self.lastgame_label.config(text=f'Последняя игра: {self.last_game}')
            self.lastgame_label.pack()
            self.wins_label.config(text=f'Победы: {self.wins}')
            self.wins_label.pack()
            self.losses_label.config(text=f'Поражения: {self.losses}')
            self.losses_label.pack()
            self.abandons_label.config(text=f'Покинуты: {self.abandons}')
            self.abandons_label.pack()
            self.matches_label.config(text=f'Количество матчей: {self.all_matches}')
            self.matches_label.pack()
            self.avatar_label.config(text=f'Аватарка: {self.avatar_url}')
            self.avatar_label.pack()
            # Загрузить изображение
            self.load_image(self.avatar_url)


            heroes_profile_url = 'https://www.dotabuff.com/players/' + self.link + '/heroes'
            # Отправляем запрос на сайт
            response = requests.get(heroes_profile_url, headers=header)
            # Проверяем успешность запроса
            if response.status_code == 200:
                # Используем BeautifulSoup для парсинга HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Находим таблицу со статистикой героев игрока
                heroes_table = soup.find('table', class_='sortable')

                heroes = []
                # Находим строки таблицы со статистикой героев
                rows = heroes_table.find_all('tr')
                # Проходим по каждой строке и выводим информацию о герое
                i = 0
                for row in rows[1:]:  # Пропускаем первую строку с заголовками
                    if i == 5:
                        break
                    cols = row.find_all('td')
                    self.hero_name = cols[1].text.strip()
                    self.matches_played = cols[2].text.strip()
                    self.winrate = cols[3].text.strip()
                    heroes.append({'hero': self.hero_name, 'winrate': self.winrate, 'matches': self.matches_played})
                    i += 1
                self.top_heroes_list = [f"{hero['hero']} - {hero['matches']} - {hero['winrate']}" for hero in heroes]

            for i, hero_info in enumerate(self.top_heroes_list):
                label = Label(self.tab2, text=hero_info)
                label.grid(row=i, column=0)



        except:
            print('Ошибочка')

    def load_image(self, url):
        response = requests.get(url)
        img_data = response.content
        image = Image.open(BytesIO(img_data))  # Открываем изображение из байтов
        image = image.resize((100, 100))  # Изменяем размер изображения (при необходимости)
        self.img_tk = ImageTk.PhotoImage(image)  # Конвертируем в PhotoImage
        self.avatar_label.config(image=self.img_tk)  # Обновляем метку
        self.avatar_label.image = self.img_tk  # Удерживаем ссылку на изображение


root = Tk()
root.title('DotabuffParser')
root.geometry('300x400')
menu = Dotabuffparser(root)
root.mainloop()
