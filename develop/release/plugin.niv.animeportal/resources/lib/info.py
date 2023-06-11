# -*- coding: utf-8 -*-

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
anistar_genres=[
    ('thriller','Боевик'),('vampires','Вампиры'),('ani-garem','Гарем'),('detective','Детектив'),('drama','Драма'),('history','История'),
    ('cyberpunk','Киберпанк'), ('comedy','Комедия'),('maho-shoujo','Махо-седзе'),('fur','Меха'),('parodies','Пародии'),('senen','Сёнен'),
    ('sports','Спорт'),('mysticism','Мистика'),('music','Музыкальное'), ('everyday-life','Повседневность'),('adventures','Приключения'),
    ('romance','Романтика'),('shoujo','Сёдзе'),('senen-ay','Сёнен-ай'),('horror','Триллер'),('horor','Ужасы'), ('fantasy','Фантастика'),
    ('fentezi','Фэнтези'),('school','Школа'),('echchi-erotic','Эччи'),('action','Экшен'),('metty','Этти'),('seinen','Сейнен'),('demons','Демоны'),
    ('magic','Магия'),('super-power','Супер сила'),('military','Военное'),('kids','Детское'),('supernatural','Сверхъестественное'),
    ('psychological','Психологическое'), ('historical','Исторический'),('samurai','Самураи'),('martial-arts','Боевые искусства'),('police','Полиция'),
    ('space','Космос'),('game','Игры'),('josei','Дзёсэй'), ('shoujo-ai','Сёдзе Ай')]

anistar_ignor_list = [
    '7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954','2282','4263','4284','4288','4352','4362','4422','4931','5129','5130',
    '5154','5155','6917','6928', '6930','6932','6936','6968','6994','7013','7055','3999','4270','4282','4296','4300','4314','4348','4349','4364','4365',
    '4366','4367','4368','4369','4374','4377','4480','4493', '4556','6036','3218','3943','3974','4000','4091','8892','8747','8913','8917']

anistar_years = [
    '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', 
    '2003', '2002', '2001', '2000', '1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990', '1989', '1988', '1987', '1986', '1985', 
    '1984', '1983', '1982', '1981', '1980', '1979', '1978', '1976', '1975', '1972', '1969', '1968']