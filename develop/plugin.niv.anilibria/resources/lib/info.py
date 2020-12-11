# -*- coding: utf-8 -*-

data = '[sett]\n\
[COLOR blue]Авторизация:[/COLOR]\n\
- Пользоваться данным ресурсом возможно [COLOR blue]Без Авторизации[/COLOR]\n\
- [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR] получают пройдя регистрацию на сайте [COLOR=gold]anilibria.tv[/COLOR]\n\
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
- Использует встроенный в [COLOR gold]KODI[/COLOR] проигрыватель. Дополнительные настройки не требуются\n\
- Просмотр зависит от скорости вашего интернета в данный момент, нагрузки на сайт и общей нагрузки на сеть интернет\n\
- Включение этого пункта автоматически отключает возможность использовать торрент-движки. После включения или отключения необходимо перезайти в плагин\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Торрент просмотр:[/COLOR]\n\
- Не работает с включенным в настройках пунктом [COLOR blue]Смотреть онлайн[/COLOR]\n\
- Требует дополнительной настройки. В настройках плагина зайти в раздел [COLOR blue]P2P[/COLOR], выбрать торрент движок (или торрент Менеджер [COLOR gold]TAM[/COLOR] - выставив предпочитаемый движок)\n\
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR], [COLOR blue]ELEMENTUM[/COLOR] нужно устанавливать отдельно\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.0.3[/COLOR]\n\
- Смена парсера с darklibria на anilibria\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]version 1.0.2[/COLOR]\n\
- Исправлена ошибка авторизации\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]version 1.0.1[/COLOR]\n\
- Оптимизация системы авторизации\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]version 1.0.0[/COLOR]\n\
- Release\n\
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

genre = (
    "","экшен","фэнтези","комедия","приключения","романтика","сёнен","драма","школа","сверхъестественное","фантастика","сейнен",
    "магия","этти","детектив","повседневность","ужасы","супер сила","психологическое","исторический","меха","мистика","демоны",
    "игры","сёдзе","триллер","вампиры","спорт","боевые искусства","музыка"
    )

year = (
    "", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008", "2007", "2006", 
    "2005", "2004", "2003", "2001", "1998", "1996"
    )

season = ("","зима", "весна", "лето", "осень")

status = {"Все релизы":"1", "Завершенные релизы":"2"}

sort = {"Новое":'1', "Популярное":"2"}