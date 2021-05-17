# -*- coding: utf-8 -*-

animeportal_plot = {
    'anidub':'Ресурс, на котором контент создаётся, а не "заимствуется". Мы работаем, чтобы вы отдыхали. ©',
    'anilibria':'Заходите и оставайтесь! Улыбнитесь, ведь вы нашли то место, где вам будет хорошо. ©',
    'animedia':'Наш проект занимается озвучиванием и адаптацией иностранной мультипликации на русский язык... ©',
    'anistar':'Наши переводы самые быстрые и качественные в Рунете! У нас приятная и привычная многим озвучка... ©'
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

