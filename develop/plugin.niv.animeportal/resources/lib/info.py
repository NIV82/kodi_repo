# -*- coding: utf-8 -*-

animeportal_plot = {
    'anidub':'Ресурс, на котором контент создаётся, а не "заимствуется". Мы работаем, чтобы вы отдыхали. ©',
    'anilibria':'Заходите и оставайтесь! Улыбнитесь, ведь вы нашли то место, где вам будет хорошо. ©',
    'animedia':'Наш проект занимается озвучиванием и адаптацией иностранной мультипликации на русский язык... ©',
    'anistar':'Наши переводы самые быстрые и качественные в Рунете! У нас приятная и привычная многим озвучка... ©',
    'shizaproject': 'Мы — безумный коллектив, занимающийся адаптацией зарубежной анимации для русскоязычной публики... ©'
    }

#========================#========================#========================#========================#========================#

anilibria_data = '[sett]\n\
[COLOR blue]Авторизация:[/COLOR]\n\
- Пользоваться данным ресурсом возможно [COLOR blue]Без Авторизации[/COLOR]\n\
- [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR] получают пройдя регистрацию на сайте [COLOR=gold]anilibria.tv[/COLOR]\n\
- [COLOR blue]Авторизация[/COLOR] позволяет использовать, добавлять, удалять аниме в списке [COLOR blue]Избранного[/COLOR] с [COLOR gold]сайта[/COLOR]\n\
- Пункт [COLOR blue]Избранное[/COLOR] появляется после [COLOR blue]авторизации[/COLOR] и перезапуска плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Сохранять обложки:[/COLOR]\n\
- Рекомендуется если у вас возникают проблемы с кэшем или регулярной подгрузкой из интернета\n\
- Подгрузка файлов происходит во время первого обращения к аниме\n\
- После сохранения [COLOR blue]обложка[/COLOR] будет загружаться с вашего устройства, без запросов в интернет\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Разблокировка:[/COLOR]\n\
- Рекомендуется если ваш провайдер блокирует доступ к ресурсу\n\
- Способы блокировок различаются и у некоторых может не работать\n\
[/sett]\n\
[play]\n\
[COLOR blue]Смотреть онлайн:[/COLOR]\n\
- Использует встроенный в [COLOR gold]KODI[/COLOR] проигрыватель. Дополнительные настройки не требуются\n\
- Просмотр зависит от скорости вашего интернета в данный момент, нагрузки на сайт и общей нагрузки на сеть интернет\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- Требует дополнительной настройки. В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок (или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок)\n\
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR] и торрент движки нужно устанавливать отдельно, часть движков устанавливается из [COLOR gold]TAM[/COLOR]\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.0.0[/COLOR]\n\
- Модификация версии 1.1.9 под интерфейс "портала"\n\
- Мелкие правки, фиксы, улучшения\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/news]\n\
[comp]\n\
Обозначения: [COLOR blue]Работает[/COLOR] | [COLOR gray]Не проверено[/COLOR] | [COLOR red]Не работает[/COLOR]\n\
Остальные движки, на данный момент , не проверены\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]T2HTTP[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR blue]Linux[/COLOR] | [COLOR blue]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]Elementum[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR blue]Linux[/COLOR] | [COLOR blue]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]TorrServer[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR blue]Linux[/COLOR] | [COLOR blue]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/comp]\n\
\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка при попытке добавить аниме в Базу Данных\n\
Рекомендуется сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 102[/COLOR][/B]\n\
Ошибка в модуле очистки Истории Поиска\n\
Рекомендуется сообщить автору плагина название аниме\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 103[/COLOR][/B]\n\
Ошибка в модуле обработки Избранного с Сайта\n\
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

anilibria_genre = (
    "","экшен","фэнтези","комедия","приключения","романтика","сёнен","драма","школа","сверхъестественное","фантастика","сейнен",
    "магия","этти","детектив","повседневность","ужасы","супер сила","психологическое","исторический","меха","мистика","демоны",
    "игры","сёдзе","триллер","вампиры","спорт","боевые искусства","музыка"
    )
anilibria_year = ("", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012",
                  "2011", "2010", "2009", "2008", "2007", "2006", "2005", "2004", "2003", "2001", "1998", "1996")
anilibria_season = ("","зима", "весна", "лето", "осень")
anilibria_status = {"Все релизы":"1", "Завершенные релизы":"2"}
anilibria_sort = {"Новое":'1', "Популярное":"2"}
anilibria_week = ('Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье')

#========================#========================#========================#========================#========================#

anidub_data = '[sett]\n\
[COLOR blue]Авторизация:[/COLOR]\n\
- Пользоваться данным ресурсом возможно только пройдя [COLOR blue]авторизацию[/COLOR]\n\
- [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR] получают пройдя регистрацию на сайте [COLOR=gold]tr.anidub.com[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Сохранять обложки:[/COLOR]\n\
- Рекомендуется если у вас возникают проблемы с кэшем или регулярной подгрузкой из интернета\n\
- Подгрузка файлов происходит во время первого обращения к аниме\n\
- После сохранения [COLOR blue]обложка[/COLOR] будет загружаться с вашего устройства, без запросов в интернет\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Разблокировка:[/COLOR]\n\
- На данный момент не требуется, добавлена на будущее\n\
[/sett]\n\
[play]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- Требует дополнительной настройки. В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок (или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок)\n\
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR], [COLOR blue]ELEMENTUM[/COLOR] нужно устанавливать отдельно\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Онлайн просмотр:[/COLOR]\n\
- На данный момент функция отсутствует в связи с замороченностью ссылок на файлы в плеере сайта\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.1.0[/COLOR]\n\
- Унификация кода для версий Kodi-18 и Kodi-19\n\
- Исправление и модификация пунктов Контекстного меню\n\
    * Раздел Поиск - пункт контекстного меню "Очистить Историю"\n\
    * Раздел Информация - пункт контекстного меню "Обновить Базу"\n\
    * Остальные разделы - пункты Добавить и "Удалить Избранное"\n\
- Изменение структуры основного меню (Раздел аниме с содержимым)\n\
- Обновление Базы Аниме в репозитории\n\
- Мелкие исправления и дополнения в коде\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/news]\n\
[comp]\n\
Обозначения: [COLOR blue]Работает[/COLOR] | [COLOR gray]Не проверено[/COLOR] | [COLOR red]Не работает[/COLOR]\n\
Остальные движки, на данный момент , не проверены\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]T2HTTP[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]Elementum[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]TorrServer[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/comp]\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка в парсере, при попытке добавить аниме в Базу Данных\n\
Рекомендуется сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=========================================================================[/COLOR]\n\
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

anidub_genres = ('сёнэн', 'романтика', 'драма', 'комедия', 'этти', 'меха', 'фантастика',
          'фэнтези', 'повседневность', 'школа', 'война', 'сёдзё', 'детектив', 'ужасы',
          'история', 'триллер', 'приключения', 'киберпанк', 'мистика', 'музыкальный',
          'спорт', 'пародия', 'для детей', 'махо-сёдзё', 'сказка', 'сёдзё-ай', 'сёнэн-ай',
          'боевые искусства', 'самурайский боевик')

anidub_years = ('1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979', '1980',
         '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991',
         '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002',
         '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013',
         '2014', '2015', '2016', '2017', '2018', '2019', '2020')

anidub_alphabet = ('а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н',
            'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'э', 'ю', 'я')

#========================#========================#========================#========================#========================#

anistar_data = '[sett]\n\
[COLOR blue]Авторизация:[/COLOR]\n\
- Пользоваться данным ресурсом возможно [COLOR blue]Без Авторизации[/COLOR]\n\
- [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR] получают пройдя регистрацию на сайте [COLOR=gold]anistar.org[/COLOR]\n\
- [COLOR blue]Авторизация[/COLOR] позволяет использовать, добавлять, удалять аниме в списке [COLOR blue]Избранного[/COLOR] с [COLOR gold]сайта[/COLOR]\n\
- Пункт [COLOR blue]Избранное[/COLOR] появляется после [COLOR blue]авторизации[/COLOR] и перезапуска плагина\n\
- Не включайте [COLOR blue]авторизацию[/COLOR] если не пользуетесь [COLOR blue]Избранным[/COLOR] с [COLOR gold]сайта[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Сохранять обложки:[/COLOR]\n\
- Рекомендуется если у вас возникают проблемы с кэшем или регулярной подгрузкой из интернета\n\
- Подгрузка файлов происходит во время первого обращения к аниме\n\
- После сохранения [COLOR blue]обложка[/COLOR] будет загружаться с вашего устройства, без запросов в интернет\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Разблокировка:[/COLOR]\n\
- Рекомендуется если ваш провайдер блокирует доступ к ресурсу\n\
- Способы блокировок различаются и у некоторых может не работать\n\
[/sett]\n\
[play]\n\
[COLOR blue]Смотреть онлайн:[/COLOR]\n\
- Использует [COLOR gold]KODI[/COLOR] проигрыватель. Дополнительные настройки не требуются\n\
- Просмотр зависит от скорости вашего интернета, нагрузки на сайт и общей нагрузки на сеть интернет\n\
- Включение этого пункта автоматически отключает возможность использовать торрент-движки. После включения или отключения необходимо перезайти в плагин\n\
- Не все доступно к онайн-просмотру. Часть мертвые ссылки, часть замороченные ссылки на файл\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- Требует дополнительной настройки. В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок (или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок)\n\
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR], [COLOR blue]ELEMENTUM[/COLOR] нужно устанавливать отдельно\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.1.0[/COLOR]\n\
- Унификация кода для версий Kodi-18 и Kodi-19\n\
- Исправление и модификация пунктов Контекстного меню\n\
    * Раздел Поиск - пункт контекстного меню "Очистить Историю"\n\
    * Раздел Информация - пункт контекстного меню "Обновить Базу"\n\
    * Раздел Информация - пункт контекстного меню "Обновить Актуальный Адрес"\n\
    * Остальные разделы - пункты Добавить и "Удалить Избранное"\n\
- Мелкие исправления и дополнения в коде\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/news]\n\
[comp]\n\
Обозначения: [COLOR blue]Работает[/COLOR] | [COLOR gray]Не проверено[/COLOR] | [COLOR red]Не работает[/COLOR]\n\
Остальные движки, на данный момент , не проверены\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]T2HTTP[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]Elementum[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR blue]Linux[/COLOR] | [COLOR blue]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]TorrServer[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/comp]\n\
\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка при попытке добавить аниме в Базу Данных\n\
Рекомендуется сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 102[/COLOR][/B]\n\
Ошибка в модуле очистки Истории Поиска\n\
Рекомендуется сообщить автору плагина название аниме\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 103[/COLOR][/B]\n\
Ошибка в модуле обработки Избранного с Сайта\n\
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

anistar_categories=[
    ('thriller/','Боевик'),
    ('vampires/','Вампиры'),
    ('ani-garem/','Гарем'),
    ('detective/','Детектив'),
    ('drama/','Драма'),
    ('history/','История'),
    ('cyberpunk/','Киберпанк'),
    ('comedy/','Комедия'),
    ('maho-shoujo/','Махо-седзе'),
    ('fur/','Меха'),
    ('parodies/','Пародии'),
    ('senen/','Сёнен'),
    ('sports/','Спорт'),
    ('mysticism/','Мистика'),
    ('music/','Музыкальное'),
    ('everyday-life/','Повседневность'),
    ('adventures/','Приключения'),
    ('romance/','Романтика'),
    ('shoujo/','Сёдзе'),
    ('senen-ay/','Сёнен-ай'),
    ('horror/','Триллер'),
    ('horor/','Ужасы'),
    ('fantasy/','Фантастика'),
    ('fentezi/','Фэнтези'),
    ('school/','Школа'),
    ('echchi-erotic/','Эччи'),
    ('action/','Экшен'),
    ('metty/','Этти'),
    ('seinen/','Сейнен'),
    ('demons/','Демоны'),
    ('magic/','Магия'),
    ('super-power/','Супер сила'),
    ('military/','Военное'),
    ('kids/','Детское'),
    ('supernatural/','Сверхъестественное'),
    ('psychological/','Психологическое'),
    ('historical/','Исторический'),
    ('samurai/','Самураи'),
    ('martial-arts/','Боевые искусства'),
    ('police/','Полиция'),
    ('space/','Космос'),
    ('game/','Игры'),
    ('josei/','Дзёсэй'),
    ('shoujo-ai/','Сёдзе Ай')
    ]

anistar_years = [
    '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011',
    '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000',
    '1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990', '1989',
    '1988', '1987', '1986', '1985', '1984', '1983', '1982', '1981', '1980', '1979', '1978',
    '1976', '1975', '1972', '1969', '1968']

anistar_ignor_list = ['7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954',
              '2282','4263','4284','4288','4352','4362','4422','4931','5129','5130','5154',
              '5155','6917','6928','6930','6932','6936','6968','6994','7013','7055','3999',
              '4270','4282','4296','4300','4314','4348','4349','4364','4365','4366','4367',
              '4368','4369','4374','4377','4480','4493','4556','6036','3218','3943','3974',
              '4000','4091']

#========================#========================#========================#========================#========================#

animedia_data = '[sett]\n\
[COLOR blue]Сохранять обложки:[/COLOR]\n\
- Рекомендуется если у вас возникают проблемы с кэшем или регулярной подгрузкой из интернета\n\
- Подгрузка файлов происходит во время первого обращения к аниме\n\
- После сохранения [COLOR blue]обложка[/COLOR] будет загружаться с вашего устройства, без запросов в интернет\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Разблокировка:[/COLOR]\n\
- Рекомендуется если ваш провайдер блокирует доступ к ресурсу\n\
- Способы блокировок различаются и у некоторых может не работать\n\
[/sett]\n\
[play]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- Требует дополнительной настройки. В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок (или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок)\n\
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR], [COLOR blue]ELEMENTUM[/COLOR] нужно устанавливать отдельно\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.1.0[/COLOR]\n\
- Унификация кода для версий Kodi-18 и Kodi-19\n\
- Исправление и модификация пунктов Контекстного меню\n\
    * Раздел Поиск - пункт контекстного меню "Очистить Историю"\n\
    * Раздел Информация - пункт контекстного меню "Обновить Базу"\n\
- Обновление Базы Аниме в репозитории\n\
- Мелкие исправления и дополнения в коде\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/news]\n\
[comp]\n\
Обозначения: [COLOR blue]Работает[/COLOR] | [COLOR gray]Не проверено[/COLOR] | [COLOR red]Не работает[/COLOR]\n\
Остальные движки, на данный момент , не проверены\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]T2HTTP[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]Elementum[/COLOR] | [COLOR blue]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]TorrServer[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] | [COLOR gray]MacOS[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/comp]\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка в парсере, при попытке добавить аниме в Базу Данных\n\
Рекомендуется сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=========================================================================[/COLOR]\n\
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

animedia_genre = {
    "":"",
    "Комедия":"1",
    "Этти":"2",
    "Школа":"3",
    "Мистика":"4",
    "Приключения":"5",
    "Фантастика":"6",
    "Боевые искусства":"7",
    "Война":"9",
    "Детектив":"11",
    "Дзёсэй":"12",
    "Драма":"13",
    "Исторический":"14",
    "Киберпанк":"15",
    "Криминал":"17",
    "Махо-сёдзё":"18",
    "Медицина":"19",
    "Меха":"21",
    "Музыка":"23",
    "Пародия":"25",
    "По игре":"26",
    "Повседневность":"27",
    "Постапокалиптика":"29",
    "Психология":"30",
    "Романтика":"31",
    "Самурайский боевик":"32",
    "Сёдзе":"33",
    "Сёнэн":"34",
    "Сёнэн-ай":"35",
    "Спорт":"37",
    "Сэйнэн":"38",
    "Триллер":"39",
    "Трэш":"40",
    "Ужасы":"41",
    "Фэнтези":"42",
    "Вампиры":"43",
    "Подкасты":"47",
    "Дорамы":"48",
    "История":"49",
    "Лайв-экшн":"50",
    "Сёдзё-ай":"51",
    "Экшен":"52",
    "Сверхъестественное":"53",
    "Гарем":"98"
    }

animedia_year = {
    "":"",
    "2020":"2020",
    "2019":"2019",
    "2018":"2018",
    "2017":"2017",
    "2016":"2016",
    "2015":"2015",
    "2014":"2014",
    "2013":"2013",
    "2012":"2012",
    "2011":"2011",
    "2010":"2010",
    "2009":"2009",
    "2008":"2008",
    "2007":"2007",
    "2006":"2006",
    "2005":"2005",
    "2004":"2004",
    "2003":"2003",
    "2002":"2002",
    "2001":"2001",
    "2000":"2000",
    "1990-e":"199",
    "1980-e":"198"
    }
				
animedia_form={
    "":"",
    "ТВ-сериал":"ТВ",
    "Фильмы":"Полнометражный",
    "OVA, ONA, Special":"OVA",
    "Дорама":"Дорама"
    }

animedia_status={
    "":"",
    "Сейчас выходит":"0",
    "Вышедшие":"1"
    }

animedia_sort={
    "Популярности":"view_count_one|desc",
    "Дате добавления":"entry_date|desc"
    }

animedia_studio = (
    "","8bit","A-1 Pictures","A.C.G.T","ACTAS"," Inc.","AIC","AIC A.S.T.A.","AIC PLUS","Ajia-do",
    "AKOM","Animac","ANIMATE","Aniplex","ARMS","Artland","ARTMIC Studios","Asahi Production",
    "asread","Ashi Productions","Aubeck","Bandai Visual","Barnum Studio","Bee Train","BeSTACK",
    "Bones","Brain's Base","EMT²","Chaos Project","Cherry Lips","CLAMP","CoMix Wave Inc.",
    "CJ Entertainment","Cinema Citrus","Daume","David Production","Dax International","Digital Frontier",
    "Digital Works","Diomedea","DLE","Dogakobo","Dong Woo Animation","Doumu","DR Movie","Easyfilm",
    "Eiken","EMation","Feel","Five Ways","Foursome","Fuji TV / KTV","FUNimation Entertainment",
    "Frontier Works","G&G Entertainment","Gainax","Gallop","GANSIS","Gathering","Geneon Universal Entertainment",
    "GoHands","Gonzino","Gonzo Digimation","Green Bunny","Group TAC","Hal Film Maker","Hangar-18",
    "Hoods Entertainment","Idea Factory","Imagin","J.C.Staff","Jinni`s Animation Studios",
    "Kaname Production","Khara","Kitty Films","Knack","Kokusai Eigasha","KSS","Kids Station",
    "Kyoto Animation","Lemon Heart","Madhouse","Manpuku Jinja","Magic Bus","Magic Capsule",
    "Manglobe","Mappa","Media Factory","MediaNet","Milky","Minamimachi Bugyosho","Mook Animation",
    "Moonrock","MOVIC","Mystery","Nickelodeon","Mushi Production","Nippon Animation","Nippon Animedia",
    "Nippon Columbia","Nomad","NAZ","NUT","Lantis","Lerche","Liden Films","OB Planning","Office AO",
    "Oh! Production","OLM"," Inc.","Ordet","Oriental Light and Magic","P Production","P.A. Works",
    "Palm Studio","Pastel","Phoenix Entertainment","Picture Magic","Pink Pineapple","Planet","Plum",
    "Production I.G","Production Reed","Project No.9","Primastea","Pony Canyon","Polygon Pictures",
    "Rising Force","Radix","Rikuentai","Robot","Rooster Teeth","FUNimation Entertainment","Satelight",
    "Sanzigen","Seven Arcs","SHAFT","Shirogumi Inc.","Shin-Ei Animation","Shogakukan Music & Digital Entertainment",
    "Soft Garage","Soft on Demand","Starchild Records","Studio 4°C","Studio Rikka","Studio APPP",
    "Studio Blanc","Studio Comet","Studio DEEN","Studio Fantasia","Studio Flag","Studio Gallop",
    "Studio Ghibli","Studio Guts","Studio Hibari","Studio Junio","Studio Live","Studio Pierrot",
    "Studio Gokumi","Studio Barcelona","Sunrise","Silver Link","SynergySP","Tatsunoko Productions",
    "Telecom Animation Film","Tezuka Productions","TMS Entertainment","TNK","The Answer Studio",
    "The Klock Worx","Toei Animation","TV Tokyo","Tokyo Kids","Tokyo Broadcasting System","Tokyo Movie Shinsha",
    "Top Craft","Transarts","Triangle Staff","Trinet Entertainment","Trigger","TYO Animations",
    "UFO Table","Victor Entertainment","Viewworks","White Fox","Wonder Farm","Wit Studio","Xebec",
    "XEBEC-M2","Zexcs","Zuiyo","Hoods Drifters Studio"
    )
    

animedia_voice = (
    "","Amails","Agzy","4a4i","Matorian","aZon","ArtLight","BlackVlastelin","Demetra","Derenn",
    "DEMIKS","Rikku","ABSURD95","AMELIA","ANGEL","ANIMAN","Andry B","AriannaFray","AXLt",
    "BLACK_VLASTELIN","ELADIEL","ENEMY","ENILOU","ERINANT","EneerGy","Egoist","Eugene","FaSt",
    "FREYA","FRUKT","FUEGOALMA","FUUROU","GFT","GKONKOV","GOMER","GREH","HHANZO","HUNTER26","ITLM",
    "JAM","JEPT","JULIABLACK","KovarnyBober","KIARA_LAINE","Kleo Rin","KUCLIA","KASHI","Kansai",
    "Kobayashi","Kona-chan","LISEK","LINOKK","L'Roy","LUNIFERA","LUPIN","LeXar","Lyxor","MACHAON",
    "MEISEI","MIRIKU","MisterX","MIRONA","MOONY","MULYA","MUNYA","MUSTADIO","MyDuck","MezIdA",
    "NAZEL","NASTR","NEAR","N_O_I_R","NIKIRI","Nuriko","Neonoir","Kabrok","Komuro","LolAlice",
    "ORIKO","OZIRIST","PERSONA99","Phoenix","RYC99","RUBY","REZAN","Riddle","Reewayvs","Railgun",
    "Revi_Kim","Rizz_Fisher","SAHAWK","SAJURI","SANDEL","SAY","SCREAM","SHACHIBURI","SHALU",
    "SILV","STEFAN","Soer","TDUBOVIC","TINDA","TicTac","TRAY","TRINAD","TROUBLE","Televizor",
    "TSUMI","VIKI","VINS","YUKIO","ZACK_FAIR","ZART","ZENDOS","VULPES VUPLES","Wicked_Wayfarer",
    "Григорий Коньков","NRG Film Distribution","Tina","ВИКТОР БОЛГОВ","Mega Anime","Пифагор",
    "Реанимедия","Ruscico","MC Entertainment","Симбад","Ruri","Odissey","Акварелька","Garison",
    "zaShunina","Sad_Kit","Milirina","Leo Tail","Satsuki","SilverTatsu","Sabadaher","Morin",
    "KingMaster","Каркас"
    )

#========================#========================#========================#========================#========================#

shiza_years = (
    '1970', '1971', '1972', '1973', '1974', '1975', '1976', '1977', '1978', '1979', '1980', 
    '1981', '1982', '1983', '1984', '1985', '1986', '1987', '1988', '1989', '1990', '1991', 
    '1992', '1993', '1994', '1995', '1996', '1997', '1998', '1999', '2000', '2001', '2002', 
    '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', 
    '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021')

shiza_direction = {
    'По Убыванию':'DESC',
    'По Возрастанию':'ASC'
    }

shiza_sort = {
    'По Дате публикации':'PUBLISHED_AT',
    'По Дате обновление':'UPDATED_AT',
    'По Просмотрам':'VIEW_COUNT',
    'По названию [A-Z]':'ORIGINAL_NAME',
    'По названию [А-Я]':'NAME',
    'По рейтингу':'SCORE'
    }

shiza_form = {
    'ТВ':'TV',
    'ТВ-спешл':'TV_SPECIAL',
    'Остальное':'OTHER',
    'Фильм':'MOVIE',
    'Короткий Фильм':'SHORT_MOVIE',
    'OVA':'OVA',
    'ONA':'ONA',
    'Музыкальный':'MUSIC'
    }

shiza_status = {
    'Анонс':'ANNOUNCE',
    'Онгоинг':'ONGOING',
    'Выпущено':'RELEASED',
    'Приостановлено':'SUSPENDED'
    }

shiza_activity = {
    'Хочучка':'WISH',
    'Заморожено':'FROZEN',
    'В работе':'WORK_IN_PROGRESS',
    'Звершено':'COMPLETED',
    'Брошено':'DROPPED'
    }

shiza_rating = (
    'G','PG','PG_13','R','R_PLUS','RX'
    )
    
shiza_season = {
    'Весна':'SPRING',
    'Лето':'SUMMER',
    'Осень':'FALL',
    'Зима':'WINTER'
    }

shiza_genres = {
    'экшен':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzM=',
    'комедия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzQ=',
    'романтика':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODc=',
    'фэнтези':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzk=',
    'фантастика':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDE=',
    'драма':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njg=',
    'школа':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODg=',
    'сверхъестественное':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTk=',
    'сёнен':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODk=',
    'приключения':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzE=',
    'повседневность':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTY=',
    'сейнен':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMTA=',
    'детектив':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDU=',
    'этти':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzg=',
    'магия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODM=',
    'меха':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODQ=',
    'гарем':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTQ=',
    'военное':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDQ=',
    'космос':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzc=',
    'триллер':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDA=',
    'игры':'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njk=',
    'музыка':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzI=',
    'супер сила':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDM=',
    'психологическое':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzA=',
    'демоны':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzU=',
    'ужасы':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODI=',
    'сёдзё':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDI=',
    'исторический':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODE=',
    'спорт':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTA=',
    'вампиры':'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTE=',
    'пародия':'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODU=',
    'боевые искусства':'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDg=',
    'полиция':'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzY='
    }

shiza_categories = {
    'Аниме':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzE=',
    'Дорамы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzI=',
    'Мультфильмы':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzM=',
    'Разное':'Q2F0ZWdvcnk6NDU4OTE0MTQ4Njg4ODU1MzQ='
    }

shiza_tags = {
    'Дружба':'VGFnOjQ1ODkxNDE0ODg1NjYyNzI0',
    'Повседневность':'VGFnOjQ1ODkxNDE0ODg1NjYyODA3',
    'Кровь':'VGFnOjQ1ODkxNDE0ODg1NjYyODk2',
    'Будущее':'VGFnOjQ1ODkxNDE0ODg5ODU3MDI5',
    'bdrip':'VGFnOjQ1ODkxNDE0ODgxNDY4NDE4',
    'webrip':'VGFnOjQ1ODkxNDE0ODg1NjYyODAw',
    'Школа':'VGFnOjQ1ODkxNDE0ODg1NjYyNzM2',
    'Олдскул':'VGFnOjQ1ODkxNDE0ODg1NjYyNzY1',
    'Магия':'VGFnOjQ1ODkxNDE0ODg1NjYyNzk5',
    'hdtvrip':'VGFnOjQ1ODkxNDE0ODg5ODU3MDM0',
    'Демоны':'VGFnOjQ1ODkxNDE0ODg1NjYyNzQ5',
    'Война':'VGFnOjQ1ODkxNDE0ODg1NjYyODAy',
    'Роботы':'VGFnOjQ1ODkxNDE0ODg1NjYyNzcz',
    'Космос':'VGFnOjQ1ODkxNDE0ODg1NjYyNzI4',
    'Любовь':'VGFnOjQ1ODkxNDE0ODg1NjYyODU0',
    'Вампиры':'VGFnOjQ1ODkxNDE0ODg1NjYyNzMy',
    'Оружие':'VGFnOjQ1ODkxNDE0ODg1NjYyNzMz'
    }

shiza_genres2 = {
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzM=': 'экшен',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzQ=': 'комедия',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODc=': 'романтика',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzk=': 'фэнтези',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDE=': 'фантастика',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njg=': 'драма',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODg=': 'школа',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTk=': 'сверхъестественное',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODk=': 'сёнен',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzE=': 'приключения',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTY=': 'повседневность',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMTA=': 'сейнен',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDU=': 'детектив',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzg=': 'этти',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODM=': 'магия',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODQ=': 'меха',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTQ=': 'гарем',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDQ=': 'военное',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5Nzc=': 'космос',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDA=': 'триллер',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5Njk=': 'игры',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzI=': 'музыка',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDM=': 'супер сила',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzA=': 'психологическое',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzU=': 'демоны',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODI=': 'ужасы',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDI=': 'сёдзё',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODE=': 'исторический',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTA=': 'спорт',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5OTE=': 'вампиры',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5ODU=': 'пародия',
    'R2VucmU6NDU4OTE0MjEzMzIzMDgwMDg=': 'боевые искусства',
    'R2VucmU6NDU4OTE0MjEzMzIzMDc5NzY=': 'полиция'
    }

studios = {
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczNzk5': 'A-1 Pictures',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzQ5': 'Bridge',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMzEx': 'Bakken Record',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjk1': 'J.C.Staff',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTYw': 'Revoroot',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjE3': 'Doga Kobo',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ0': 'MAPPA',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTE4': 'Nomad',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTU5': 'Millepensee',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTQx': "Brain's Base",
    'U3R1ZGlvOjQ1ODkxNDIxMzMyMzA4MDE0': 'Bones',
    'U3R1ZGlvOjQ1ODkxNDIxMzc0MjUxMDEw': 'Telecom Animation Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjQx': 'Asread',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMzA1': 'Okuruto Noboru',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODAz': 'SILVER LINK.',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk1': 'Studio Deen',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjcz': 'Toei',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTQ4': '8bit',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTU2': 'C-Station',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODcx': 'Platinum Vision',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjky': 'Team TillDawn',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTQ3': 'Orange',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjc4': 'Bibury Animation',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTMw': 'White Fox',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2Njcy': 'TMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjk4': 'Production I.G',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjky': 'TNK',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDg5': 'Science SARU',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzcw': 'Geno',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzMw': 'Hoods',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODUz': 'Colorido',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDIw': 'David',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTIz': 'feel.',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTI0': 'P.A. Works',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTA0': 'Seven Arcs',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDU2': 'Zero-G',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDE0': 'Lerche',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTE4': 'Gokumi',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMzAx': 'Hokiboshi',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5NzU5': 'Bandai Namco Pictures',
    'U3R1ZGlvOjQ2MjUxNDcwNTc5ODI2Njg4': 'Studio Comet',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjc2': 'Marvy Jack',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5NzY0': 'CloverWorks',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQz': 'Tezuka',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTU4': 'Kyoto',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTYx': 'Tear',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTY4': 'Imagineer',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzI1': 'Shaft',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjg5': 'Arvo',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzA3': 'Shin-Ei',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTM2': 'Pine Jam',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzI1': 'Project No.9',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjAy': 'Ajia-Do',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjM5': 'TROYCA',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MTkw': 'Magic Bus',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTY5': 'PuYUKAI',
    'U3R1ZGlvOjQ1ODkxNDIxMzc0MjUxMDQz': 'Trigger',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTY4': 'Imagineer',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjg0': 'DMM.futureworks',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg0': 'Satelight',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjc1': 'HORNETS',
    'U3R1ZGlvOjQ1ODkxNDIxNDE2MTk0MDU0': 'Ezόla',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODQ3': 'Nexus',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjA5': 'CoMix Wave Films',
    'U3R1ZGlvOjQ1ODkxNDIxMzMyMzA4MDE2': 'Pierrot',
    'U3R1ZGlvOjQ1ODkxNDIxNDE2MTk0MDQ4': 'Lapin Track',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzQ2': 'Wit',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTM5': 'EMT Squared',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ2': 'LandQ',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MTk5': 'ufotable',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQx': 'Kinema Citrus',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTk5': 'Yokohama Animation Lab',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzAx': 'Madhouse',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTMw': 'White Fox',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzQ1': 'Seven Arcs Pictures',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5NzY0': 'CloverWorks',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjgx': 'DRAWIZ',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjE3': 'Encourage Films',
    'U3R1ZGlvOjQ4MjEyMjg3MDM4Njg1MTg0': 'Platinumvision',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjI5': 'A.C.G.T.',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTYy': 'Lay-duce',
    'U3R1ZGlvOjQ1ODkxNDIxNDMyOTcxMjcx': 'Maho Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTEx': 'AIC Build',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ0': 'MAPPA',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjQ5': '3Hz',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTUz': 'Diomedéa',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjQ0': 'Connect',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzk4': 'Sola Digital Arts',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTQ0': 'Pierrot Plus',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2Njc4': 'Xebec',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQ5': 'Seven',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTYx': 'Tear',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTYy': 'Lay-duce',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzc5': 'production doA',
    'U3R1ZGlvOjQ1ODkxNDIxNDI4Nzc2OTYz': 'Stingray',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTQy': 'NAZ',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjYw': 'Passione',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzAx': 'Madhouse',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTc5': 'Production GoodBook',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzkz': 'Gaina',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5NzY0': 'CloverWorks',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDU2': 'Zero-G',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5ODAx': 'Lings',
    'U3R1ZGlvOjQ4MTgxNjI4NDkyNTc4ODE2': 'Yamato Works',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjQ0': 'Connect',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTc5': 'Chizu',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODgz': 'M.S.C',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTU2': 'B.CMAY PICTURES',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjE1': 'Gonzo',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTUx': 'Creators in Pack',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzg3': 'The Answer',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODQ3': 'Nexus',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzI2': 'Blanc',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTc4': 'Signal.MD',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzg3': 'The Answer',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzA3': 'Shin-Ei',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczNzk5': 'A-1 Pictures',
    'U3R1ZGlvOjQ2MTQ2NTM0Mjc3OTA2NDMy': 'Hal Film Maker',
    'U3R1ZGlvOjQ1ODkxNDIxMzMyMzA4MDEx': 'Sunrise',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ0': 'Production Reed',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjQ5': '3Hz',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDcz': 'Haoliners Animation League',
    'U3R1ZGlvOjQ1ODkxNDIxNDExOTk5Nzgy': 'CygamesPictures',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTA1': 'Hibari',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTU5': 'Millepensee',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTY0': 'Nut',
    'U3R1ZGlvOjQ1ODkxNDIxMzc0MjUxMDE2': 'TYO Animations',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTc4': 'Signal.MD',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzUy': 'Production IMS',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTYw': 'GEMBA',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTUy': 'C2C',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDcx': 'A-Real',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjQ3': 'Shuka',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDQ0': 'AXsiZ',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzA3': 'Fantasia',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDUy': 'M2',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTQx': 'Sega',
    'U3R1ZGlvOjQ1ODkxNDIxNDA3ODA1NDY2': 'Typhoon Graphics',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODIx': 'Manglobe',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODU1': 'Actas',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQ1': 'SANZIGEN',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NDk0': 'Khara',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5Njc0': 'Polygon Pictures',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODc2': 'Hoods Drifters',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTk3': 'Namu',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODQ5': 'GoHands',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjQ5': 'Do',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODMy': 'Ordet',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTM5': 'EMT Squared',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODcx': 'Platinum Vision',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjg5': 'AIC',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxNDAzNjExMTYw': 'GEMBA',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NDg4': 'Zexcs',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTQ3': 'Orange',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTI4': 'Arms',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjIx': 'Tatsunoko',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjA4': 'Gainax',
    'U3R1ZGlvOjQ1ODkxNDIxMzk1MjIyNTQ5': 'Moriken',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODM5': 'VOLN',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzQ2': 'Wit',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2Njgx': 'Daume',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjQ5': '3Hz',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQ1': 'SANZIGEN',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjQ0': 'Connect',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzEw': 'Comet',
    'U3R1ZGlvOjQ1ODkxNDIxMzk5NDE2ODM5': 'VOLN',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTMw': 'White Fox',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzQ5': 'Bridge',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NDg4': 'Zexcs',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjQx': 'Asread',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTI0': 'LIDENFILMS',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzIy': 'Artland',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjM5': 'TROYCA',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTg1': 'Graphinica',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjU3': 'teamKG',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTA1': 'Hibari',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjE3': 'Encourage Films',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjIz': 'Felix Film',
    'U3R1ZGlvOjQ2MjQ4NDEzMDI4Njc5Njgw': 'Harmony Gold',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODMy': 'Ordet',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzkxMDI4MjM5': 'TROYCA',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTc2': 'OLM',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzU3': 'Ghibli',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1Mzcw': 'I.Gzwei',
    'U3R1ZGlvOjQ4MTkxNjIyNzU5ODQxNzky': 'Studio 4°C',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjEw': '4C',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjg5': 'AIC',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTQ3': 'Orange',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjI3': 'Agent 21',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTI1': 'Primastea',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTMz': 'Kaname',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjQ0': 'Connect',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5Njgx': 'Yaoyorozu',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzI1': 'Project No.9',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjIx': 'Tatsunoko',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTkx': 'Vega',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjYy': 'Group TAC',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjU4': 'Darts',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ2': 'animate Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTUy': 'C2C',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTcw': 'Toshiba',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjY5': 'Tokyo Movie Shinsha',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjM3': 'WAO World',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2Njg2': 'Idea Factory',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTIw': 'Hakk',
    'U3R1ZGlvOjQ4MTg5Mzg5MTcxMzI2OTc2': 'Nakamura Production',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjcz': 'Toei',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTcz': 'DAX',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjU1': 'Media Blasters',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjM5': 'Mushi',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ0': 'MAPPA',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTQ3': 'Oh!',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTMy': 'Remic',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTIz': 'feel.',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjYw': 'D.A.S.T.',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTQx': 'AIC PLUS+',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTIz': 'feel.',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODUy': 'Tama',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTQw': 'Signal',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ0': 'MAPPA',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzM5': 'Rikka',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODMy': 'Ordet',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzM3': 'Junio',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ2': 'animate Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjU1': 'Media Blasters',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwODgz': 'March',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTYy': 'Lay-duce',
    'U3R1ZGlvOjQ1ODkxNDIxMzg2ODMzOTMw': 'Opera House',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDM5': 'Lilix',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTM3': 'Nippon',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjA5': 'CoMix Wave Films',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQx': 'Kinema Citrus',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTIy': 'Gallop',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzE5': 'Ashi',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwODkw': 'Filmlink International',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTE0': 'Aubec',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQw': 'Purple Cow Studio Japan',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDE2': 'MooGoo',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwODk5': 'Triangle Staff',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODQ0': 'AIC ASTA',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzAx': 'Madhouse',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjg5': 'AIC',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczNzk0': 'BeSTACK',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzYxNjY4MTM1': 'AIC Takarazuka',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTQw': 'Nippon Columbia',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjUz': 'Kadokawa Shoten',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTI2': 'Sony Music',
    'U3R1ZGlvOjQ1ODkxNDIxMzgyNjM5NjU2': 'Victor',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjA2': 'Mook',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2Njg2': 'Idea Factory',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTE1': 'Kyuuma',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjAz': 'Bandai Visual',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjMy': 'KSS',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ5': 'Tokyo Kids',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTUw': 'SME Visual Works',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NDg4': 'Zexcs',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjg5': 'AIC',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjM4': 'Hiro Media',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ2': 'animate Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTAz': 'Phoenix',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ2': 'animate Film',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NTk5': 'Artmic',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ5': 'PrimeTime',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjg5': 'AIC',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTQ4': '8bit',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTQ4': '8bit',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDI4': 'Bandai',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjMy': 'Think Corporation',
    'U3R1ZGlvOjQ1ODkxNDIxMzU3NDczODQw': 'Bee Train',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTMw': 'Minami Machi Bugyousho',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDE3': 'Jinnis Animation',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTUz': 'Digital Frontier',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjY1': 'Azeta Pictures',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzQ2': 'LandQ',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzM0': 'Radix',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTQ4': '8bit',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzA4': 'Oxybot',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTA5': 'REALTHING',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MjM3': 'Unicorn',
    'U3R1ZGlvOjQ1ODkxNDIxMzQwNjk2NjQ0': 'Production Reed',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NTE1': 'Nikkatsu',
    'U3R1ZGlvOjQ1ODkxNDIxMzc4NDQ1MzI2': 'Blanc',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ5MDg1MTg3': 'Trans Arts',
    'U3R1ZGlvOjQ1ODkxNDIxMzY1ODYyNDQ1': 'SANZIGEN',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMzM1': 'Marine',
    'U3R1ZGlvOjQ1ODkxNDIxMzUzMjc5NDg4': 'Zexcs',
    'U3R1ZGlvOjQ1ODkxNDIxMzM2NTAyMjcz': 'Toei',
    'U3R1ZGlvOjQ1ODkxNDIxMzQ0ODkwOTI4': 'Soeishinsha',
    'U3R1ZGlvOjQ1ODkxNDIxMzcwMDU2NzUy': 'Production IMS'
    }