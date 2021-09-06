# -*- coding: utf-8 -*-

animeportal_plot = {
    'anidub':'Anidub Online - Где все делается с душой.Самая лучшая озвучка аниме. Самое новое аниме онлайн. ©',
    'anilibria':'Заходите и оставайтесь! Улыбнитесь, ведь вы нашли то место, где вам будет хорошо. ©',
    'animedia':'Наш проект занимается озвучиванием и адаптацией иностранной мультипликации на русский язык... ©',
    'anistar':'Наши переводы самые быстрые и качественные в Рунете! У нас приятная и привычная многим озвучка... ©',
    'shizaproject': 'Мы — безумный коллектив, занимающийся адаптацией зарубежной анимации для русскоязычной публики... ©'
    }

animeportal_data = '[play]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок\n\
- Просмотр зависит от наличия людей на раздаче искомого торрента файла\n\
- Вся необходимая информация по загрузке и установке Движков находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[COLOR gray]=====================================================[/COLOR]\n\
[COLOR blue]Онлайн просмотр:[/COLOR]\n\
- Использует [COLOR gold]KODI[/COLOR] проигрыватель. Дополнительные настройки не требуются\n\
- Просмотр зависит от скорости вашего интернета, нагрузки на сайт и общей нагрузки на сеть интернет\n\
[/play]\n\
[news]\n\
[B][COLOR=darkorange]Version 0.5.5[/COLOR][/B]\n\
    - Множественные мелкие исправления\n\
    - Оптимизация субплагинов\n\
    - Контекстное меню расширено и "раскрашено" для удобства\n\
    - Раздел каталог в Animedia (K18) исправлен\n\
[COLOR gray]=====================================================[/COLOR]\n\
[B][COLOR=darkorange]Version 0.4.3[/COLOR][/B]\n\
    - Унификация кода под версии Kodi-18, Kodi-19\n\
[COLOR gray]=====================================================[/COLOR]\n\
[/news]\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
[COLOR gray]=====================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=====================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка в парсере, при попытке добавить аниме в Базу Данных\n\
Рекомендуется сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=====================================================[/COLOR]\n\
[B][COLOR red]ERROR: 102[/COLOR][/B]\n\
Ошибка в модуле очистки Истории Поиска\n\
Рекомендуется сообщить автору плагина название аниме\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 103[/COLOR][/B]\n\
Ошибка в модуле обработки Избранного\n\
Рекомендуется сообщить автору плагина название аниме\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 404[/COLOR][/B]\n\
Типичная ошибка - Страница не найдена, удалена, перемещена\n\
Рекомендуется зайти на сайт и проверить страницу\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 403[/COLOR][/B]\n\
Типичная ошибка - Доступ запрещен, вам отказано в доступе к этой странице\n\
Рекомендуется зайти на сайт и узнать причину ограничения доступа\n\
[/bugs]'
#========================#========================#========================#========================#========================#
anidub_genres = ('сёнэн','романтика','драма','комедия','этти','меха','фантастика',
    'фэнтези','повседневность','школа','война','сёдзё','детектив','ужасы','история','триллер',
    'приключения','киберпанк','мистика','музыкальный','спорт','пародия','для детей','махо-сёдзё',
    'сказка','сёдзё-ай','сёнэн-ай','боевые искусства','самурайский боевик')

anidub_years = ('1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979', '1980',
         '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991',
         '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
         '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
         '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021')

anidub_alphabet = ('а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н',
            'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я')
#========================#========================#========================#========================#========================#
anilibria_genre = ("","экшен","фэнтези","комедия","приключения","романтика","сёнен","драма","школа","сверхъестественное","фантастика",
    "сейнен","магия","этти","детектив","повседневность","ужасы","супер сила","психологическое","исторический","меха","мистика","демоны",
    "игры","сёдзе","триллер","вампиры","спорт","боевые искусства","музыка")

anilibria_year = ("", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012",
                  "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2001", "1998", "1996")

anilibria_season = ("","зима", "весна", "лето", "осень")

anilibria_status = {"Все релизы":"1", "Завершенные релизы":"2"}

anilibria_sort = {"Новое":'1', "Популярное":"2"}

anilibria_week = ('Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье')
#========================#========================#========================#========================#========================#
animedia_genre = {'': '', 'Гарем': '98', 'Вампиры': '43', 'Боевые искусства': '7', 'Война': '9', 'Детектив': '11', 'Дзёсэй': '12', 'Дорамы': '48',
                  'Драма': '13', 'Исторический': '14', 'История': '49', 'Киберпанк': '15', 'Комедия': '1', 'Криминал': '17', 'Лайв-экшн': '50', 
                  'Махо-сёдзё': '18', 'Медицина': '19', 'Меха': '21', 'Мистика': '4', 'Музыка': '23', 'Пародия': '25', 'По игре': '26', 
                  'Повседневность': '27', 'Подкасты': '47', 'Постапокалиптика': '29', 'Приключения': '5', 'Психология': '30', 'Романтика': '31', 
                  'Самурайский боевик': '32', 'Сверхъестественное': '53', 'Спорт': '37', 'Сэйнэн': '38', 'Сёдзе': '33', 'Сёдзё-ай': '51', 
                  'Сёнэн': '34', 'Сёнэн-ай': '35', 'Триллер': '39', 'Трэш': '40', 'Ужасы': '41', 'Фантастика': '6', 'Фэнтези': '42', 'Школа': '3', 
                  'Экшен': '52', 'Этти': '2'
}

animedia_year = {"":"","2020": "2020", "2019": "2019", "2018": "2018", "2017": "2017", "2016": "2016", "2015": "2015", "2012-2014": "2012|2013|2014", 
                 "2008-2012": "2008|2009|2010|2011|2012", "2000-2007": "2000|2001|2002|2003|2004|2005|2006|2007", "1990е годы": "199", "1980е годы": "198"}

animedia_form = {"":"","ТВ-сериал": "ТВ","Полнометражные": "Полнометражный","Короткометражные": "Короткометражный","OVA, ONA, Special": "OVA","Дорама": "Дорама"}

animedia_status = {"":"", "Сейчас выходит": "&search:ongoing=0", "Вышедшие": "&search:ongoing=1", "Анонсировано": "&search:relize_plan=1"}

animedia_sort = {"Дате добавления":"&orderby_sort=entry_date|desc", "Популярности":"&orderby_sort=view_count_one|desc",
              "Алфавиту":"&orderby_sort=title","Комментариям":"&orderby_sort=comment_total|desc"}

animedia_studio = ("","8bit","A-1 Pictures","A.C.G.T","ACTAS, Inc.","AIC","AIC A.S.T.A.","AIC A.S.T.A.","AIC PLUS","Ajia-do","AKOM","Animac","ANIMATE",
                  "Aniplex","ARMS","Artland","ARTMIC Studios","Asahi Production","asread","Ashi Productions","Aubeck","Bandai Visual","Barnum Studio",
                  "Bee Train","BeSTACK","Bones","Brain's Base","EMT²","Chaos Project","Cherry Lips","CLAMP","CoMix Wave Inc.","CJ Entertainment",
                  "Cinema Citrus","Daume","David Production","Dax International","Digital Frontier","Digital Works","Diomedea","DLE","Dogakobo",
                  "Dong Woo Animation","Doumu","DR Movie","Easyfilm","Eiken","EMation","Feel","Five Ways","Foursome","Fuji TV / KTV","FUNimation Entertainment",
                  "Frontier Works","G&G Entertainment","Gainax","Gallop","GANSIS","Gathering","Geneon Universal Entertainment","GoHands","Gonzino","Gonzo Digimation",
                  "Green Bunny","Group TAC","Hal Film Maker","Hangar-18","Hoods Entertainment","Idea Factory","Imagin","J.C.Staff","Jinni`s Animation Studios",
                  "Kaname Production","Khara","Kitty Films","Knack","Kokusai Eigasha","KSS","Kids Station","Kyoto Animation","Lemon Heart","Madhouse","Manpuku Jinja",
                  "Magic Bus","Magic Capsule","Manglobe","Mappa","Media Factory","MediaNet","Milky","Minamimachi Bugyosho","Mook Animation","Moonrock","MOVIC",
                  "Mystery","Nickelodeon","Mushi Production","Nippon Animation","Nippon Animedia","Nippon Columbia","Nomad","NAZ","NUT","Lantis","Lerche","Liden Films",
                  "OB Planning","Office AO","Oh! Production","OLM, Inc.","Ordet","Oriental Light and Magic","P Production","P.A. Works","Palm Studio","Pastel",
                  "Phoenix Entertainment","Picture Magic","Pink Pineapple","Planet","Plum","Production I.G","Production Reed","Project No.9","Primastea","Pony Canyon",
                  "Polygon Pictures","Rising Force","Radix","Rikuentai","Robot","Rooster Teeth","FUNimation Entertainment","Satelight","Sanzigen","Seven Arcs","SHAFT",
                  "Shirogumi Inc.","Shin-Ei Animation","Shogakukan Music & Digital Entertainment","Soft Garage","Soft on Demand","Starchild Records","Studio 4°C",
                  "Studio Rikka","Studio APPP","Studio Blanc","Studio Comet","Studio DEEN","Studio Fantasia","Studio Flag","Studio Gallop","Studio Ghibli","Studio Guts",
                  "Studio Hibari","Studio Junio","Studio Live","Studio Pierrot","Studio Gokumi","Studio Barcelona","Sunrise","Silver Link","SynergySP","Tatsunoko Productions",
                  "Telecom Animation Film","Tezuka Productions","TMS Entertainment","TNK","The Answer Studio","The Klock Worx","Toei Animation","TV Tokyo","Tokyo Kids",
                  "Tokyo Broadcasting System","Tokyo Movie Shinsha","Top Craft","Transarts","Triangle Staff","Trinet Entertainment","Trigger","TYO Animations","UFO Table",
                  "Victor Entertainment","Viewworks","White Fox","Wonder Farm","Wit Studio","Xebec","XEBEC-M2","Zexcs","Zuiyo","Hoods Drifters Studio")

animedia_voice = ("","Amails", "Agzy", "4a4i", "Matorian", "aZon", "ArtLight", "BlackVlastelin", "Beany", "Demetra", "Derenn", "DEMIKS", "Demi4", "Rikku", "ABSURD95", 
                  "AMELIA", "ANGEL", "ANIMAN", "Andry B", "AriannaFray", "AXLt", "BLACK_VLASTELIN", "ELADIEL", "ENEMY", "ENILOU", "ERINANT", "EneerGy", "Egoist", 
                  "Eugene", "Esmeralda", "GAR", "FaSt", "FREYA", "FRUKT", "FUEGOALMA", "FUUROU", "GFT", "GKONKOV", "GOMER", "GREH", "HHANZO", "HUNTER26", "ITLM", "JAM", 
                  "JEPT", "JULIABLACK", "KovarnyBober", "KIARA_LAINE", "Kleo Rin", "KUCLIA", "KASHI", "Kansai", "Kobayashi", "Kona-chan", "LISEK", "LINOKK", "L'Roy", 
                  "LUNIFERA", "LUPIN", "LeXar", "Lyxor", "MACHAON", "MEISEI", "MIRIKU", "MisterX", "MIRONA", "Meona", "MOONY", "MULYA", "MUNYA", "MUSTADIO", "MyDuck", 
                  "MezIdA", "NAZEL", "NASTR", "NEAR", "N_O_I_R", "NIKIRI", "Nuriko", "Neonoir", "Kabrok", "Komuro", "LolAlice", "ORIKO", "OZIRIST", "PERSONA99", "Phoenix", 
                  "RYC99", "RUBY", "REZAN", "Riddle", "Reewayvs", "Railgun", "Revi_Kim", "Rizz_Fisher", "SAHAWK", "SAJURI", "SANDEL", "SAY", "SCREAM", "SHACHIBURI", "SHALU", 
                  "SILV", "STEFAN", "Seven", "Soer", "Seeker", "TDUBOVIC", "TINDA", "TicTac", "TRAY", "TRINAD", "TROUBLE", "Televizor", "TSUMI", "VIKI", "VINS", "YUKIO", 
                  "ZACK_FAIR", "ZART", "ZENDOS", "VULPES VUPLES", "Wicked_Wayfarer", "Григорий Коньков", "NRG Film Distribution", "Tina", "ВИКТОР БОЛГОВ", "Mega Anime", 
                  "Пифагор", "Реанимедия", "Ruscico", "MC Entertainment", "Симбад", "Ruri", "Odissey", "Акварелька", "Garison", "zaShunina", "Sad_Kit", "Milirina", "Leo Tail", 
                  "Satsuki", "SilverTatsu", "Sabadaher", "Sitri", "Morin", "KingMaster", "Каркас", "GreenTalker", "Трина Дубовицкая", 
                  )
#========================#========================#========================#========================#========================#