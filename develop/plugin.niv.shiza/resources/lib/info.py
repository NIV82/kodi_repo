# -*- coding: utf-8 -*-

data = '[sett]\n\
[COLOR blue]Авторизация:[/COLOR]\n\
- Пользоваться данным ресурсом возможно только пройдя [COLOR blue]авторизацию[/COLOR]\n\
- [COLOR=gold]Логин[/COLOR] и [COLOR=gold]Пароль[/COLOR] получают пройдя регистрацию на сайте [COLOR=gold]shiza-project.com[/COLOR]\n\
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
- Рекомендуется [COLOR blue]ELEMENTUM[/COLOR], [COLOR blue]T2HTTP[/COLOR], [COLOR blue]TorrServer[/COLOR]. Остальные движки, на данный момент, еще не проверены\n\
- [COLOR=red]Внимание:[/COLOR] [COLOR gold]TAM[/COLOR], [COLOR blue]ELEMENTUM[/COLOR], [COLOR blue]T2HTTP[/COLOR] или [COLOR blue]TorrServer[/COLOR] нужно устанавливать отдельно\n\
- Вся необходимая информация по загрузке и установке этих плагинов находится на форуме [COLOR gold]xbmc.ru[/COLOR]\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR blue]Онлайн просмотр:[/COLOR]\n\
- На данный момент функция отсутствует\n\
[/play]\n\
[news]\n\
[COLOR blue]version 1.0.0[/COLOR]\n\
- Release\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/news]\n\
[comp]\n\
Обозначения: [COLOR blue]Работает[/COLOR] | [COLOR gray]Не проверено[/COLOR] | [COLOR red]Не работает[/COLOR]\n\
Остальные движки, на данный момент , не проверены\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]T2HTTP[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] |\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]Elementum[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] |\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[COLOR orange]TorrServer[/COLOR] | [COLOR gray]Win10[/COLOR] | [COLOR gray]Linux[/COLOR] | [COLOR gray]Android[/COLOR] |\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[/comp]\n\
[bugs]\n\
[COLOR blue]Список ошибок не полный и будет постепенно дополняться.[/COLOR]\n\
\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 100[/COLOR][/B]\n\
Ошибка при попытке скачать Базу Данных Аниме с репозитория\n\
Ошибка не критична. Плагин создаст новую и начнет заполнять ее с нуля, но с готовой БД быстрее и удобнее\n\
Рекомендуется сообщить об ошибке автору плагина\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 101[/COLOR][/B]\n\
Ошибка в парсере, при попытке добавить аниме в Базу Данных\n\
Сама не исправляется, необходимо сообщить автору плагина ID аниме (не обязательно целиком)\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 102[/COLOR][/B]\n\
Ошибка в модуле очистки Истории Поиска\n\
Возникает если плагин не может удалить историю\n\
Сама не исправляется, необходимо сообщить автору плагина название аниме\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 404[/COLOR][/B]\n\
Типичная ошибка - Страница не найдена, удалена, перемещена\n\
Рекомендуется зайти на сайт и проверить страницу\n\
[COLOR gray]=========================================================================[/COLOR]\n\
[B][COLOR red]ERROR: 403[/COLOR][/B]\n\
Типичная ошибка - Доступ запрещен, вам отказано в доступе к этой странице\n\
Рекомендуется зайти на сайт и узнать причину ограничения доступа\n\
[/bugs]'

tags = ('комедия','приключения','bdrip','драма','фантастика','романтика','фэнтези','экшен','webrip',
        'повседневность','мистика','школа','этти','сверхъестественное','меха','олдскул','магия',
        'Sunrise','ужасы','J.C. Staff','сёнэн','A-1 Pictures Inc.','детектив','Madhouse Studios',
        'спорт','демоны','hdtvrip','война','Production I.G','Studio Pierrot','пародия','гарем',
        'BONES','космос','Studio DEEN','роботы','музыка','любовь','триллер','вампиры','Silver Link',
        'Toei Animation','Xebec','оружие','игры','будущее','боевые искусства','кровь','MAPPA','SHAFT',
        'дружба','TMS Entertainment','Brain\'s Base','сёдзё','сэйнэн','Satelight','клуб','Doga Kobo','AIC',
        'история','друзья','White Fox','Lerche','девушка','dvdrip','Feel','смерть','боги','Gonzo',
        'Studio Barcelona','Wit Studio','музыкальный','Ufotable','P.A. Works','Kyoto Animation',
        'психологическое','монстры','Seven Arcs','сражения','8bit','школьники','Seven','самураи',
        'игра','судьба','супер сила','ZEXCS','Studio Gokumi','исторический','GoHands','полиция',
        'Trigger','семья','зомби','Hoods Entertainment','Manglobe Inc.','мечи','эротика','Zero-G',
        'Production IMS','Artland','Tatsunoko','сестра','брат','юри','принцесса','духи','лоли',
        'пришельцы','парень','военное','школьницы','сестры','технологии','Rooster Teeth','девочки',
        'ARMS','войны','деревня','убийства','работа','Liden Films','Project No.9','TNK','маги',
        'психология','Diomedea','загадки','катастрофа','махо-сёдзё','академия','бог','Magic Bus',
        'битвы','ниндзя','люди','душа','мясо','карты','asread','ILCA','Millepensee','пираты','экшн',
        'человечество','дворецкий','призраки','группа','герой','Studio 4°C','сражение','TYO Animations',
        'сокровища','месть','жизнь','мечты','GAINAX','ANIMATE','Shin-Ei Animation','David Production',
        'ученые','мелодрама','бандиты','киберпанк','япония','флот','апокалипсис','AIC PLUS','монстр',
        'Cinema Citrus','принц','трагедия','королевство','суперсила','проблемы','NAZ','извращенец',
        'старшеклассники','Passione','Asia-Do','панцу','Creators in Pack','ангелы','Pierrot Plus','планета',
        'сёдзе-ай','мечта','сила','Polygon Puctures','Lay-duce','корабли','Tezuka Productions',
        'Liden Films, Sanzigen','сёнэн-ай','герои','драконы','бейсбол','отаку','ведьмы','подземелье','демон')