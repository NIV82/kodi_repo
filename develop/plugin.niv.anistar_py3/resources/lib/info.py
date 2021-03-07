# -*- coding: utf-8 -*-

data = '[sett]\n\
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
[COLOR blue]version 0.5.0[/COLOR]\n\
- Py3 test\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]version 0.4.1[/COLOR]\n\
- Добавлена функция обновления Актуального адреса (раздел информация) в тестовом-ручном режиме.\n\
- Разработка основного функционала плагина завершена\n\
\n\
- Начата унификация кода под Py2(Kodi 18)-Py3(Kodi 19)\n\
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

categories=[
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

years = [
    '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011',
    '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000',
    '1999', '1998', '1997', '1996', '1995', '1994', '1993', '1992', '1991', '1990', '1989',
    '1988', '1987', '1986', '1985', '1984', '1983', '1982', '1981', '1980', '1979', '1978',
    '1976', '1975', '1972', '1969', '1968']

ignor_list = ['7013','6930','6917','6974','6974','4106','1704','1229','1207','1939','1954',
              '2282','4263','4284','4288','4352','4362','4422','4931','5129','5130','5154',
              '5155','6917','6928','6930','6932','6936','6968','6994','7013','7055','3999',
              '4270','4282','4296','4300','4314','4348','4349','4364','4365','4366','4367',
              '4368','4369','4374','4377','4480','4493','4556','6036','3218','3943','3974',
              '4000','4091']