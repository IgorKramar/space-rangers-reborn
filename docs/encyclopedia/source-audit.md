# Аудит существующего мира по исходникам

Автор: Igor Kramar. Дата: 2 ноября 2026. Исследован `SpaceRangersHD_FPC`, ревизия `1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5`; рабочее дерево на момент чтения чистое. Код и ресурсы игры не изменялись; игровая партия не запускалась.

Установленный `Rangers.exe`: версия файла **2.1.2500.0**, Steam build **20648864**, SHA-256 `83300344af802bc51e64389c58f047e5afdf195c133048098be3881fae29ed98`. Версия извлечена из единственного кандидата VS_FIXEDFILEINFO без запуска; запись — `executable-version.json`. Эти номера не равны версии сохранения 167 в FPC и сами по себе не доказывают соответствие коду.

## Граница достоверности

Это проверяемая карта реализации, а не новый официальный справочник разработчика. FPC-проект прямо называет себя неофициальным портом реконструированного кода и включает исправления, поддержку модификаций и собственные дополнения. Поэтому `VERIFIED_SOURCE` означает «прочитано в указанном коде», а не «автор игры подтвердил это как замысел». Состав установленного Steam-релиза и его хеши фиксируются в соседнем манифесте извлечения; совпадение поведения с этим source HEAD не проверено. [S01](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/NOTICE.md#L1), [S55](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L103)

Числа и внутренние enum не считаются количеством авторских сюжетов. Каталог допустимых имён, набор шаблонов, конкретные объекты сохранения и утверждения лора ведутся отдельно. Полные оригинальные тексты остаются в приватном извлечении; в этот документ включены наблюдения и ссылки на реализацию.

## Три разные степени изученности

- **Декодировано**: бинарный формат разобран в структурированные данные. Корректный разбор всех 40SCR ещё не означает чтение всех их диалогов или понимание всех исходов.
- **Проиндексировано**: сохранены пути, id, имена, хеши и связи. Для изображений, звука и карт это может быть только каталог файлов, без анализа изображённого или исполняемого содержания.
- **Прочитано по смыслу**: сформулировано проверяемое утверждение со ссылкой на конкретный фрагмент. В этом аудите так проверены 56 утверждений по исходникам; это не эквивалент энциклопедического прочтения всего сюжетного корпуса.

Динамическая проверка прохождением — отдельная четвёртая ось. Успех декодера и отсутствие остаточных байтов не доказывают достижимость сцены, объективность реплики персонажа, правильность всех чисел или работу механики в установленной игре.

## География: что постоянно, а что формируется в партии

| Слой | Что подтверждено | Что нельзя из этого заключать |
|---|---|---|
| Галактика | По умолчанию создаются 73 звезды; координаты определяются генератором и seed. | Все соседи, расстояния и границы канонически фиксированы. |
| Имена систем | Берутся из упорядоченного блока Star. В установленном русском блоке 72 числовых ключа 00–71 плюс Terron. | Все 73 строки в точности равны 73 итоговым уникальным именам партии. |
| Особые звёзды | Первые пять и индексы 70/71 имеют особые параметры; последней звезде после генерации копируется имя выбранной особой звезды. | `Star.Terron` автоматически остаётся названием последнего видимого объекта в любой партии. |
| Планеты | Обычные названия выбираются из расовых пулов без повторения; есть специальные солнечные и пиратские правила. | Каждое имя закреплено за одной звездой, расой и политическим строем во всех партиях. |
| Станции | Пулы имён привязаны к типу; новые станции получают свободное имя или суффикс. | Каждая станция из каталога одновременно существует в игре или занимает постоянную орбиту. |
| Квестовые места | Текстовые квесты назначаются подходящим планетам и подставляют текущие имена. | Упомянутая в прохождении планета является неизменным адресом этого приключения. |

Источник правил: [S02](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L2314), [S03](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L6837), [S04](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L4753), [S05](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L4803), [S07](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L362), [S09](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L313), [S10](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aRuins.pas#L325), [S44](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L9086).

Установленный русский каталог содержит первые системы Тарон, Пхедок, Солнце, Атлан, Краа, а ключи 70/71 — Тортугац и Нифигац. В `PlanetName.PirateClan` находятся Роджерия, Моновар, Шхуна, Жемчужина, Фале-де-Фей и Гаалеон. Это проверка извлечённых данных (`CFG/Rus/Lang.dat`, ключи `Star`, `PlanetName.PirateClan`); механизм фактической привязки проверен отдельно в коде. Точные полные пулы экспортирует каталог контента.

Особенно важна Солнечная система: в данных есть девять имён — Меркурий, Венера, Земля, Марс, Юпитер, Сатурн, Нептун, Уран, Плутон; исследованный генератор создаёт **семь** планет и берёт имена по порядку. Он задаёт Земле Луну и особые характеристики отдельным орбитам. Нельзя исправлять «астрономическую неточность» или приписывать все девять объектов каждой партии, не сверив установленную игру и авторские допущения. [S05](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L4803), [S06](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L367)

На старте создаются шесть обычных станций относительно системы игрока. Далее мир проходит 300 прогревочных ходов: итоговый состав уже зависит от симуляции. Поэтому полный перечень объектов **конкретной** партии требует снимка сохранения: id, имя, родительская система, координаты, тип, владелец, контроль, день, seed. Каталог ресурсов отвечает на другой вопрос — какие имена и шаблоны вообще доступны. [S11](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L679), [S12](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L12), [S13](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L702)

## Таксономия мира и контента

Пять рас Коалиции — малоки, пеленги, люди, фэяне и гаальцы. В `TOwnerId` рядом с ними присутствуют доминаторы, необитаемость и пиратская принадлежность. Эти восемь технических значений нельзя пересказывать как восемь рас. Контроль системы (`TStarFaction`), раса пилота (`PilotRace`) и владелец планеты/корабля (`OwnerId`) — разные понятия. [S14](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L474), [S16](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L354), [S31](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aShip.pas#L107)

Доминаторы имеют три серии — Блазера, Келлера и Террона. Отдельно задаются типы: центральный босс, эквентор, ургант, смерш, менок, штип, бертор, клиг. В установленном `ShipType.Dominator` написано «Смерш». Внутренняя таксономия не объясняет происхождение машин и не делает все серии одной личностью. [S15](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L300)

Стандартные станционные названия в установленном `ShipType.TypeName`: центр рейнджеров(RC), пиратская база(PB), военная база(WB), научная база(SB), бизнес-центр(BK), медицинский центр(MC), Доминион(CB). В source также есть CustomStation/UB, но `RuinName.UB` в установленном русском каталоге отсутствует. Это реальный пример того, почему возможность движка нельзя автоматически переносить в канон игры. [S19](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L93)

| Внутренняя таксономия | Число значений | Источник |
| `TOwnerId` | 8 | [source/game/aGalaxyStruct.pas:474](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L474) |
| `TShipType` | 14 | [source/game/aGalaxyStruct.pas:93](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L93) |
| `THullType` | 11 | [source/game/aGalaxyStruct.pas:113](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L113) |
| `TKlingType` | 8 | [source/game/aGalaxyStruct.pas:300](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L300) |
| `TDominatorSeries` | 3 | [source/game/aGalaxyStruct.pas:303](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L303) |
| `TRangerCareer` | 3 | [source/game/aGalaxyStruct.pas:306](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L306) |
| `TPlanetInvention` | 20 | [source/game/aGalaxyStruct.pas:311](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L311) |
| `TPlanetEconomy` | 3 | [source/game/aGalaxyStruct.pas:341](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L341) |
| `TPlanetGovernment` | 5 | [source/game/aGalaxyStruct.pas:346](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L346) |
| `TStarFaction` | 3 | [source/game/aGalaxyStruct.pas:354](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L354) |
| `TPilotSkill` | 6 | [source/game/aGalaxyStruct.pas:245](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L245) |
| `TProgramIndex` | 12 | [source/game/aGalaxyStruct.pas:248](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L248) |
| `TCaptainHealthEffect` | 24 | [source/game/aGalaxyStruct.pas:61](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L61) |
| `TCoalitionProject` | 12 | [source/game/aGalaxyStruct.pas:218](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L218) |
| `TQuestType` | 5 | [source/game/aGalaxyStruct.pas:516](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L516) |
| `TGalaxyNewsKind` | 46 | [source/game/aGalaxyStruct.pas:570](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L570) |
| `TScriptActionType` | 62 | [source/game/aGalaxyStruct.pas:128](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L128) |
| `TItemType` | 76 | [source/game/aConst.pas:607](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L607) |

Все 321 значение этих 18 перечислений, включая числовые id, выгружены в `structural-facts.json`. Это выбранные основные классификаторы, не заявление об исчерпании всех enum движка.

`TItemType` содержит 8 торговых групп, 34 типа семейства артефактов, 8 основных классов корабельного оборудования, 18 пронумерованных типов оружия, CustomWeapon и прочие специальные категории. Отдельные корпуса, микромодули, модели оружия, карты RTS/гиперпространства, портреты, конфигурации и сценарии задаются данными, поэтому количество типов не равно количеству объектов каталога. [S18](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L607)

## Экономика и жизнь вне экрана игрока

Торговцы действительно перевозят и обменивают грузы: у них есть трюм, деньги, очередь достижимых планет, цены покупки и продажи. Выбор маршрута учитывает дальность и опасную принадлежность системы. Экономика уже живая в смысле поведения отдельных кораблей. [S22](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aTransport.pas#L471), [S23](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aTransport.pas#L405)

Одновременно складские количества восьми товарных групп самостоятельно изменяются по формуле целевого запаса. Цель и цены зависят от расы, правительства, аграрной/смешанной/индустриальной экономики, размера и событий дефицита/избытка. Поэтому существующую модель нельзя описывать как замкнутую межзвёздную экономику, где каждая единица создана из прослеживаемого сырья. Новая экономика с работниками, энергией, оплаченными заказами и снабжением заменяет это правило; это изменение дизайна, а не восстановление якобы уже имеющейся системы. [S17](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L341), [S20](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3346), [S21](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3409)

Правительства и кризисы уже меняются. Есть революция с изменением строя, отношений к рейнджерам и новостями; есть находки месторождений, дефициты и избытки товаров. В источнике не подтверждена единая модель партий, выборов, групп населения, миграции и наследования должностей. Не следует ни объявлять политику совершенно отсутствующей, ни выдавать предложенные новые механизмы за текущие. [S24](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3430), [S25](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3525)

Наука уже влияет на войну и оснащение: есть планетные направления изобретений, научные базы, потребление материалов для исследований доминаторов, специальные программы, ремонт и улучшение предметов. Бизнес-центры дают кредиты, принимают депозиты и финансируют коалиционные проекты. Новая производственная цепь, собственные лабораторные рецепты и персональное управление базой должны согласовываться с этими существующими функциями. [S26](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L311), [S27](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L10161), [S40](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aItem.pas#L141), [S41](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aItem.pas#L1344), [S47](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fRuinsTalk.pas#L2644)

Условия разрешения трёх серий доминаторов не сводятся к уничтожению кораблей: код учитывает отдельные состояния преобразования/ухода/исследования и особый исход Блазера. Расшифровывать их следует по соответствующим диалогам, сохраняя варианты решения. [S56](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L3034).

## Календарь, персонажи и память

Основной ход общий: галактика рассчитывает удалённые системы, военные группы и сценарии, затем продвигает CurrentTurn. В текстовом квесте AdvanceDays тоже запускает суточную симуляцию, а не локальное независимое время. Расчёты используют константу TurnsPerYear=365; календарные даты формируются отдельной функцией. Мгновенные диалоги и длительные действия надо проверять по обработчику; нельзя автоматически приписывать каждому текстовому выбору один день. [S12](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L12), [S28](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L2712), [S29](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/quests/fPlanetQuest.pas#L2627), [S30](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fPlanet.pas#L244)

Капитан ещё технически связан с TShip: имя, происхождение пилота, портрет, навыки, здоровье, деньги, отношения и партнёрство лежат в том же объекте. У рейнджера есть карьеры торговца, пирата и воина, прогресс и известность; у кораблей — враги, перемирия и напарники. Поэтому появление самостоятельного человека с несколькими последовательными должностями требует новой устойчивой идентичности, но должно сохранить уже существующие знакомства, карьеру, болезни и репутацию. [S31](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aShip.pas#L107), [S32](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aRanger.pas#L1358), [S33](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aShip.pas#L168), [S34](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L245), [S35](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L61)

Существуют два разных слоя записи событий. `PlanetNews` хранит тексты новостей с id, днём и типом; записи старше 30 ходов удаляются. `GalaxyEvents` хранит тип, день и числовые/текстовые параметры, сохраняется в сейв, но очищается после 1825 ходов и при достижении лимита 10000 элементов. Это реальные предшественники хроники, однако не постоянный причинный архив всей кампании. [S36](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L570), [S37](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L9223), [S38](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyEvent.pas#L17), [S39](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L11064)

## Приключения, бой и исследование

Уже есть пять типов правительственных поручений: письмо, уничтожение корабля, текстовый квест, защита системы и защита корабля. Есть исследование необитаемых планет спутниками, поиск поверхностной добычи, временные чёрные дыры и отдельные режимы приключений. Коалиция создаёт группы освобождения, а игрок может оплатить операцию с конкретными участниками, маршрутом и временем сборов. [S42](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fPlanetNO.pas#L75), [S43](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L516), [S44](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L9086), [S45](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fRuinsTalk.pas#L4180), [S46](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGroup.pas#L92), [S49](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L2905)

Сценарный движок поддерживает привязанные к миру звёзды, планеты, группы, предметы, места, состояния и диалоги; из него вызываются текстовые, аркадные и планетные бои. Это сильная авторская основа для новых мест, но список возможностей языка не является перечнем выпущенного контента. В частности, полноценный режиссёр причинных историй ещё нельзя объявлять существующим лишь потому, что есть сценарии с условиями. [S50](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/script/aScript.pas#L3105), [S51](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/script/aScript.pas#L28)

RTS запускается отдельным модулем, а вокруг вызова делается снимок мира. Ветка технической ошибки в реконструкции предлагает особый переход; она нуждается в отдельной поведенческой проверке до реализации новых гарантий повтора. Из этого кода нельзя вывести обещание «подготовка всегда оплачивается до боя, результат применяется ровно один раз». [S52](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGov.pas#L429)

## Границы проверки после инвентаризации

Структурный разбор завершён: **20 DAT, 32 PKG, 40 SCR и 320 языковых файлов QM/QMM**. Это 80 базовых текстовых приключений, а не 320 разных квестов. Проверка контейнеров и ссылок графов больше не является открытым пробелом. Отдельные разделы энциклопедии содержат реестр приключений, аннотации и разбор основных сюжетных ветвей; они дополняют, а не заменяют этот аудит кода.

1. **Снимок партии** нужен только для списка фактически существующих объектов выбранной кампании. Ресурсные пулы имён и правила генерации не являются готовой статичной картой мира.
2. **Все комбинации и достижимость ветвей** ещё не проверены. Декодирование каждого SCR/QM/QMM и первый смысловой проход не доказывают, что рассмотрены все активаторы, исключения, подстановки и взаимоисключающие исходы. У аннотаций сохранён уровень чтения.
3. **Происхождение лора** фиксируется точным первичным текстом, изданием и говорящим. Прочитаны ключевые объяснения происхождения доминаторов и основные развилки HD; легенды персонажей, реклама нанимателя и газетные версии не повышаются автоматически до объективного факта.
4. **Разделение версий** сохраняется: оригинальные КР, КР 2, дополнения и HD не объединяются молча; модификационные хуки порта и новая «Оттепель» помечены отдельно. Совпадение исходной реконструкции с установленным exe не объявляется доказанным.
5. **Поведенческая сверка** остаётся отдельной работой: воспроизводимая генерация, прохождение ветвей, торговля, финалы и сохранение в установленном релизе. Статический разбор не заменяет запуск игры и измерение производительности Deck.

Не найденное в этом обзоре не объявляется отсутствующим во всех историях игры. В матрице 38 направлений подтверждённые квестовые мотивы отмечены отдельно от общегалактических механизмов; статус «проверить» оставлен только там, где свидетельств ещё недостаточно.


## Реестр проверяемых утверждений

В машиночитаемом файле для каждого утверждения сохранены статус, ревизия, путь, строки, область действия и ограничения. Ниже его человекочитаемый указатель.

### S01. Репозиторий — неофициальный FPC-порт реконструированного Delphi-кода; авторство исходной игры и добавлений различается.

`VERIFIED_SOURCE` · Происхождение источника. [NOTICE.md:1](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/NOTICE.md#L1).

Ограничение: MIT распространяется на собственные изменения порта, не автоматически на исходную игру и её ресурсы.

### S02. Число звёзд по умолчанию — 73; возможно переопределение Constellations.GalaxyCountStars.

`VERIFIED_SOURCE` · Генератор новой игры. [source/game/aConst.pas:2314](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L2314).

Ограничение: 73 — настройка этого кода, а не универсальный размер каждой модифицированной галактики.

### S03. Положение звёзд и созвездий генерируется с использованием GenerationSeed.

`VERIFIED_SOURCE` · Генератор новой игры. [source/game/aGalaxy.pas:6837](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L6837).

Ограничение: Именной каталог не задаёт фиксированных координат или соседей.

### S04. Имя звезды берётся из Star по индексу объекта modulo число параметров; первая часть значения до запятой.

`VERIFIED_SOURCE` · Именование систем. [source/game/aGalaxy.pas:4753](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L4753).

Ограничение: Порядок параметров существенен; имена проходят последующие преобразования.

### S05. Система с индексом 2 получает 7 планет и специальный солнечный режим; первые пять систем кроме неё — 6 планет/3 населённых; 70 и 71 имеют специальные пиратские режимы.

`VERIFIED_SOURCE` · Структура начальной галактики. [source/game/aGalaxy.pas:4803](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L4803).

Ограничение: Поле Inhabited=0 в солнечной ветке — маркер режима, не число населённых миров.

### S06. Солнечные имена выбираются по порядку из PlanetName.Solar; Земле задаётся спутник Moon, отдельные параметры орбит и миров прописаны в коде.

`VERIFIED_SOURCE` · Солнечная система. [source/game/aPlanet.pas:367](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L367).

Ограничение: Обнаружение 9 имён в локализации не означает создание всех 9: цикл генератора задаёт 7.

### S07. Обычные имена планет выбираются без повторения из списка владельца; в первых пяти системах используется начало списка, затем случайный выбор; при исчерпании — имя звезды с номером.

`VERIFIED_SOURCE` · Именование планет. [source/screens/fGameSettings.pas:362](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L362).

Ограничение: Отдельные солнечные, пиратские и сценарные случаи обходят этот путь.

### S08. Пиратские имена планет получаются из PlanetName по внутреннему имени владельца; особый режим 10 берёт первый элемент.

`VERIFIED_SOURCE` · Пиратские миры. [source/game/aPlanet.pas:705](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L705).

Ограничение: В установленной локализации внутренний ключ называется PirateClan, а не Pirate.

### S09. После выбора особой удалённой звезды последняя звезда получает её имя; каталог Star не следует буквально считать списком финальных уникальных объектов партии.

`VERIFIED_SOURCE` · Особая система при генерации. [source/screens/fGameSettings.pas:313](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L313).

Ограничение: Смысл последующих сюжетных преобразований требует проверки сценариев и сохранения.

### S10. Станция выбирает имя из RuinName.<тип>, избегая занятых имён своего типа; при исчерпании добавляет числовой суффикс. ModRuinNameConfig имеет приоритет.

`VERIFIED_SOURCE` · Именование станций. [source/game/aRuins.pas:325](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aRuins.pas#L325).

Ограничение: Это пулы допустимых названий, не фиксированные места всех станций.

### S11. Стартовая генерация создаёт центры рейнджеров, науки и медицины в начальной системе и пиратскую, деловую и военную станции в соседних по дистанции системах.

`VERIFIED_SOURCE` · Начальные станции. [source/screens/fGameSettings.pas:679](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L679).

Ограничение: Сценарии, моды и последующая симуляция могут изменять состав.

### S12. Перед стартом выполняется 300 прогревочных ходов; год задан как 365 ходов.

`VERIFIED_SOURCE` · Календарные константы. [source/game/aGalaxyStruct.pas:12](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L12).

Ограничение: Число 200 здесь — базовые шаги движения на ход, не дни и не реальное время.

### S13. Генератор действительно выполняет GalaxyWarmupTurns циклов расчёта системы игрока и галактики.

`VERIFIED_SOURCE` · Стартовое состояние. [source/screens/fGameSettings.pas:702](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameSettings.pas#L702).

Ограничение: Начало видимой партии уже является результатом симуляции, а не только расстановки объектов.

### S14. TOwnerId различает пять рас Коалиции, доминаторов, необитаемость и пиратскую принадлежность.

`VERIFIED_SOURCE` · Таксономия владельцев. [source/game/aGalaxyStruct.pas:474](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L474).

Ограничение: oiPirate — политическая принадлежность, oiUninhabited — статус; нельзя выводить восемь биологических рас.

### S15. Доминаторы разделены на серии Блазера, Келлера, Террона; тип корпуса/корабля задаётся независимо восьмью TKlingType.

`VERIFIED_SOURCE` · Таксономия доминаторов. [source/game/aGalaxyStruct.pas:300](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L300).

Ограничение: Таблица реализации не заменяет историю происхождения серий.

### S16. Контроль систем имеет три базовые стороны: Коалиция, доминаторы, пираты.

`VERIFIED_SOURCE` · Фракции. [source/game/aGalaxyStruct.pas:354](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L354).

Ограничение: В коде также существуют модификационные custom-faction поля; это не доказательство четвёртой канонической стороны.

### S17. Планетные экономики: аграрная, смешанная, индустриальная; правительства: анархия, диктатура, монархия, республика, демократия.

`VERIFIED_SOURCE` · Таксономия планет. [source/game/aGalaxyStruct.pas:341](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L341).

Ограничение: Отдельная производственная специализация каждого предприятия здесь не описывается.

### S18. В TItemType — 76 идентификаторов, из них первые восемь — Food, Medicine, Technics, Luxury, Minerals, Alcohol, Arms, Narcotics.

`VERIFIED_SOURCE` · Таксономия вещей. [source/game/aConst.pas:607](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L607).

Ограничение: Это типы, а не число конкретных предметов/моделей; CustomWeapon и служебные типы требуют отличать от штатного контента.

### S19. TShipType включает 6 мобильных категорий и 8 станционных, включая CustomStation; THullType отдельно задаёт 11 классов.

`VERIFIED_SOURCE` · Корабли и станции. [source/game/aGalaxyStruct.pas:93](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L93).

Ограничение: Установленный каталог имён имеет 7 стандартных групп станций без UB: дополнительный enum нельзя автоматически объявлять официальным контентом.

### S20. На планете восемь рынков ежедневно ориентируются на целевые цены и запасы с поправками расы, правительства, экономики, размера, дефицита и избытка.

`VERIFIED_SOURCE` · Экономика. [source/game/aPlanet.pas:3346](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3346).

Ограничение: Эта формула описывает существующую абстрактную экономику, не физические производственные цепочки.

### S21. Количество товаров непосредственно изменяется случайными шагами к/от целевого запаса и ограничивается снизу нулём.

`VERIFIED_SOURCE` · Источники и стоки товаров. [source/game/aPlanet.pas:3409](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3409).

Ограничение: Прямое восстановление запаса несовместимо с новым требованием строгого материального баланса без изменения правил.

### S22. NPC-транспорт покупает и продаёт реальные количества рыночных товаров, проверяя деньги, свободный трюм и наличный запас.

`VERIFIED_SOURCE` · Торговые NPC. [source/game/aTransport.pas:471](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aTransport.pas#L471).

Ограничение: Движение грузов существует; это не подтверждает наличие многоступенчатых рецептов и бухгалтерского баланса всей галактики.

### S23. Транспорты строят очередь достижимых планет с учётом дальности, состояния корпуса и контроля систем, затем выбирают пункт торговли.

`VERIFIED_SOURCE` · Навигация торговли. [source/game/aTransport.pas:405](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aTransport.pas#L405).

Ограничение: Наличие физически летающих торговцев не делает их поток единственным источником снабжения.

### S24. Смена правительства уже реализована: выбирается иная форма, меняются отношения к рейнджерам, формируется новость.

`VERIFIED_SOURCE` · Политика. [source/game/aPlanet.pas:3430](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3430).

Ограничение: Не означает выборы, партии, наследование должности или персональную биографию губернатора.

### S25. Случайные экономические события включают революцию, месторождение/нехватку минералов, дефициты и избытки оружия, техники, пищи, медикаментов, роскоши и алкоголя.

`VERIFIED_SOURCE` · Кризисы. [source/game/aPlanet.pas:3525](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlanet.pas#L3525).

Ограничение: Обнаруженные события — рыночные модификаторы и новости; многоступенчатая демографическая модель не подтверждена.

### S26. Планеты развивают двадцать направлений изобретений; отдельные функции выбирают и продвигают текущее исследование.

`VERIFIED_SOURCE` · Технологии. [source/game/aGalaxyStruct.pas:311](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L311).

Ограничение: Список направлений не равен рецептам изготовления отдельных устройств.

### S27. Исследование доминаторских серий продвигается при наличии научных баз; материалы расходуются, завершение открывает соответствующие программы и публикует новость.

`VERIFIED_SOURCE` · Научная война. [source/game/aGalaxy.pas:10161](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L10161).

Ограничение: Базовая скорость остаётся ненулевой при минимальной эффективности; не переносить сюда новую модель только оплаченных заказов.

### S28. Галактика обновляет удалённые системы, группы освобождения, активные сценарии и затем увеличивает CurrentTurn.

`VERIFIED_SOURCE` · Суточная симуляция. [source/game/aGalaxy.pas:2712](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L2712).

Ограничение: Система игрока имеет отдельную фазу того же хода; это не два независимых календаря.

### S29. Текстовый квест при AdvanceDays экспортирует деньги/внешние параметры и для каждого дня запускает расчёты системы игрока и галактики.

`VERIFIED_SOURCE` · Время в квестах. [source/quests/fPlanetQuest.pas:2627](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/quests/fPlanetQuest.pas#L2627).

Ограничение: StandaloneQuestMode имеет особую ветку; не все переходы текста обязаны расходовать дни.

### S30. Планетный экран различает запуск текстового квеста и кнопку окончания хода; перед входом в квест создаёт автосохранение.

`VERIFIED_SOURCE` · Планетный интерфейс. [source/screens/fPlanet.pas:244](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fPlanet.pas#L244).

Ограничение: Для полного времени конкретного действия надо читать его обработчик и данные квеста.

### S31. Имя, раса пилота, портрет, навыки, здоровье, отношения, деньги и партнёрские связи находятся в TShip.

`VERIFIED_SOURCE` · Идентичность персонажей. [source/game/aShip.pas:107](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aShip.pas#L107).

Ограничение: Само наличие Id корабля не создаёт отдельной постоянной записи человека.

### S32. Три карьеры рейнджера — торговец, пират, воин; активность по карьерам и выдающиеся достижения обновляются отдельно.

`VERIFIED_SOURCE` · Прогрессия NPC. [source/game/aRanger.pas:1358](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aRanger.pas#L1358).

Ограничение: Пиратская карьера рейнджера не равна автоматическому созданию отдельного TPirate; полный жизненный цикл должностей не подтверждён.

### S33. У корабля есть EnemyShip, TruceShip, PartnerShip и срок партнёрства; существуют индивидуальные RangerRelations.

`VERIFIED_SOURCE` · Отношения и спутники. [source/game/aShip.pas:168](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aShip.pas#L168).

Ограничение: Не подтверждает полноценную систему заклятого врага или командной организации.

### S34. Шесть базовых навыков: меткость, манёвренность, техника, торговля, обаяние, лидерство.

`VERIFIED_SOURCE` · Навыки. [source/game/aGalaxyStruct.pas:245](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L245).

Ограничение: Русские названия здесь перевод внутренней семантики; точные подписи UI надо брать из Skills локализации.

### S35. Здоровье капитана различает 12 болезней и 12 стимуляторов с отдельным состоянием прогресса и сроков.

`VERIFIED_SOURCE` · Персонажные состояния. [source/game/aGalaxyStruct.pas:61](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L61).

Ограничение: Это состояния капитана, не медицинская симуляция планетного населения.

### S36. Новость имеет Id, Turn, NewsType, Text; типы включают революции, рынки, войны, рейнджеров, заключение, станции, исследования и операции.

`VERIFIED_SOURCE` · Новости. [source/game/aGalaxyStruct.pas:570](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L570).

Ограничение: 46 типов новостей не означают 46 единственных сюжетов.

### S37. Планетные новости удаляются, когда им больше 30 ходов.

`VERIFIED_SOURCE` · Хранение новостей. [source/game/aGalaxy.pas:9223](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L9223).

Ограничение: Нельзя называть этот список вечной историей партии.

### S38. TGalaxyEvent хранит тип, ход, числовые и текстовые данные и поддерживает сохранение/загрузку.

`VERIFIED_SOURCE` · События симуляции. [source/game/aGalaxyEvent.pas:17](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyEvent.pas#L17).

Ограничение: Полей typed participants/location/causes в этой структуре нет; смысл payload определяется производителем.

### S39. Журнал GalaxyEvents удаляет события старше 1825 ходов; добавление также ограничивает список размером менее 10000.

`VERIFIED_SOURCE` · Срок хранения событий. [source/game/aGalaxy.pas:11064](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L11064).

Ограничение: Второй предел реализован в aGalaxyEvent.pas:187–194; история ограничена и возрастом, и числом записей.

### S40. Улучшения и ремонт оборудования уже существуют: ConditionPercent, BrokenFlag, три уровня Improve и улучшение на научной базе.

`VERIFIED_SOURCE` · Состояние оборудования. [source/game/aItem.pas:141](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aItem.pas#L141).

Ограничение: Износ/поломка не тождественны новому набору частичных качественных неисправностей.

### S41. Ремонт восстанавливает ConditionPercent до 100 и снимает BrokenFlag; цена зависит от повреждений и вида предмета.

`VERIFIED_SOURCE` · Ремонт. [source/game/aItem.pas:1344](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aItem.pas#L1344).

Ограничение: Расход только денег в этой функции не равен доказательству полной стоимости всех сценарных ремонтов.

### S42. Необитаемые планеты имеют развёртываемые спутники, траектории и панель исследования; на планете хранится поверхностная добыча.

`VERIFIED_SOURCE` · Исследование необитаемых миров. [source/screens/fPlanetNO.pas:75](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fPlanetNO.pas#L75).

Ограничение: Механика поиска уже есть; многоэтапная научная программа с гипотезами — отдельное предлагаемое расширение.

### S43. Базовые правительственные задания имеют пять типов: письмо, уничтожение корабля, текстовый квест, защита системы, защита корабля.

`VERIFIED_SOURCE` · Задания. [source/game/aGalaxyStruct.pas:516](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxyStruct.pas#L516).

Ограничение: Это типы каркаса заданий, не полный список сценарных историй.

### S44. Текстовые квесты назначаются подходящим планетам при генерации по расе и условиям поверхности; планета получает TextQuestId.

`VERIFIED_SOURCE` · Привязка квестов. [source/game/aGalaxy.pas:9086](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L9086).

Ограничение: Нельзя объявлять любую планету из текста постоянным географическим местом без проверки подстановок.

### S45. Военная база позволяет оплатить создание группы освобождения с кораблями, пунктами маршрута и датой сборов.

`VERIFIED_SOURCE` · Совместные операции. [source/screens/fRuinsTalk.pas:4180](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fRuinsTalk.pas#L4180).

Ограничение: Это основа совместной войны, а не подтверждение логистического снабжения по рецептам.

### S46. Группы освобождения имеют сохранение, загрузку, маршрут, выбор цели, построение приказов и продвижение кораблей.

`VERIFIED_SOURCE` · Организация флота. [source/game/aGroup.pas:92](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGroup.pas#L92).

Ограничение: Наличие TGroup не означает пользовательскую корпорацию или постоянную командную иерархию.

### S47. Бизнес-центр предоставляет кредиты, депозиты и инвестиции; коалиционные проекты включают станции, субсидии и военную операцию.

`VERIFIED_SOURCE` · Финансовые услуги. [source/screens/fRuinsTalk.pas:2644](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fRuinsTalk.pas#L2644).

Ограничение: Инвестиция в станцию не доказывает личное владение и управление станцией игроком.

### S48. В Доминионе покупается или продлевается пиратская лицензия на TurnsPerYear.

`VERIFIED_SOURCE` · Пиратская ветка. [source/screens/fRuinsTalk.pas:8035](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fRuinsTalk.pas#L8035).

Ограничение: Нельзя переименовать это в каперский патент правительства против заданной державы без проверки текста и последствий.

### S49. Чёрные дыры создаются и закрываются в общей симуляции, хранят две звезды и CreatedTurn; обычная временная дыра закрывается после 200 ходов при допустимых условиях.

`VERIFIED_SOURCE` · Аномалии переходов. [source/game/aGalaxy.pas:2905](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L2905).

Ограничение: Это не доказательство движущихся штормов, временных облаков или научной экспедиции из нового плана.

### S50. Сценарный загрузчик поддерживает версии 5–8 и отдельные ветки формата до 7.

`VERIFIED_SOURCE` · Формат SCR. [source/script/aScript.pas:3105](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/script/aScript.pas#L3105).

Ограничение: Установленные SCRv6 нельзя читать схемойv7 без адаптации и проверки полного потребления файла.

### S51. Сценарии описывают места, звёзды, планеты, группы, предметы, состояния, диалоги и запросы текстового/аркадного/планетного боя.

`VERIFIED_SOURCE` · Инструментарий авторских историй. [source/script/aScript.pas:28](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/script/aScript.pas#L28).

Ограничение: Возможности языка сами по себе не доказывают, что конкретная история поставляется в игре.

### S52. RTS подключён как отдельный модуль с Run и статистикой; правительственный экран сохраняет и восстанавливает снимок вокруг боя.

`VERIFIED_SOURCE` · Стыковка RTS с кампанией. [source/screens/fGov.pas:429](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGov.pas#L429).

Ограничение: Новые гарантии однократного результата, подготовки и технического повтора требуют отдельной проверки; наличие снимка их не доказывает.

### S53. После экрана завершения ContinueClicked освобождает Galaxy и переводит в результаты/титры; это не продолжение послевоенной симуляции.

`VERIFIED_SOURCE` · Одна ветка завершения. [source/screens/fGameEnd.pas:460](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/screens/fGameEnd.pas#L460).

Ограничение: Не является исчерпывающим анализом всех сюжетных условий победы и вариантов продолжения до этого экрана.

### S54. У игрока существует удалённое хранение через StorageEntries и записи LocationOwner/Item/SlotIndex.

`VERIFIED_SOURCE` · Склады игрока. [source/game/aPlayer.pas:29](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aPlayer.pas#L29).

Ограничение: Новая собственность на складах и поставки должны учитывать уже существующее хранение; общий реестр прав всех NPC не подтверждён.

### S55. Текущая версия формата сохранений в исследуемом коде —167.

`VERIFIED_SOURCE` · Сохранения. [source/game/aConst.pas:103](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aConst.pas#L103).

Ограничение: Это версия формата source-ветки, не номер установленной игры, Steambuild или обещание совместимости нового движка.


### S56. Разрешение каждой доминаторской серии имеет несколько условий: уничтожение центрального корабля и особые сюжетные состояния Террона, Келлера или Блазера.

`VERIFIED_SOURCE` · Условия завершения доминаторских веток. [source/game/aGalaxy.pas:3034](https://github.com/pakompom/SpaceRangersHD_FPC/blob/1d1835a1e6b3846ffdb76eb687c07e41f8aafcb5/source/game/aGalaxy.pas#L3034).

Ограничение: Точный смысл TerronToStarTurn, KellerLeaveTurn, KellerResearchTargetStarId, BlazerLandingPlanetId и условия их достижения устанавливаются по сценариям и диалогам; внутреннее имя не заменяет лор.
