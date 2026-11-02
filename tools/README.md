# Инструменты каталога исходной игры

Инструменты читают локальную установку Space Rangers HD; игру и её сценарии не запускают. Нужны Python 3.10+ и два отдельных checkout существующих библиотек. Их исходники не копируются в этот проект:

- [ranger-tools](https://github.com/denballakh/ranger-tools), commit `b3c0ce20d1cf61b030f3c33482d09b91500b75c6`;
- [rangers-utils](https://github.com/murgesku/rangers-utils), commit `c37e2f292cb335400d244eaba82b6c32dc19b281`.

Второй reader обслуживает STRG-конфигурации RTS и запускается отдельным процессом: обе библиотеки используют имя пакета `rangers`. Адаптер SCR 5/6 добавляет недостающие старые поля к существующей схеме; проверяется обратной сериализацией без изменения байтов. Имена внутри старых PKG декодируются как CP1251.

## Извлечение

Пути ниже заменяются путями собственной установки и исследовательских каталогов. Каталог private должен находиться **вне репозитория**, отдельно от export и установленной игры. Для нового контрольного среза используйте новые выходные каталоги.

```sh
python3 tools/catalog_game_content.py \
  --install /path/to/SpaceRangersHD \
  --ranger-tools /path/to/ranger-tools \
  --rangers-utils /path/to/rangers-utils \
  --private-out /path/to/private-research \
  --export-out /path/to/catalog-export

python3 tools/catalog_manual.py \
  --game-dir /path/to/SpaceRangersHD \
  --output-dir /path/to/private-research/manual
```

`catalog_game_content.py` записывает расшифрованные оригиналы только в private; export содержит справочные определения и индексы. Это исследовательская выгрузка: перед публикацией нужно выбрать предназначенные для неё файлы и проверить поля. Нельзя автоматически публиковать весь private или считать все подписи словарём игровых предметов.

`catalog_manual.py` создаёт полный текст руководства в `manual-pages.private.json` и отдельный `manual-index.json` без текста. Только второй используется в опубликованном каталоге.

## Проверка

```sh
python3 tools/catalog_manual.py --self-test
python3 tools/test_content_catalog.py
python3 tools/verify_content_catalog.py \
  --install /path/to/SpaceRangersHD \
  --ranger-tools /path/to/ranger-tools \
  --private-out /path/to/private-research \
  --export-out /path/to/catalog-export
```

Проверяющий инструмент сопоставляет реальный состав DAT/PKG с манифестом, сверяет сценарные payload с архивным индексом и локальными файлами, проверяет QMM-графы, усечённые SCR, старую сериализацию, кириллическое имя PKG и хеши исходников. Пустой или неполный набор не должен считаться успехом. Результат сохраняется как `resource-verification.json`.

Проверки подтверждают корректность исследовательского извлечения, а не игровой баланс или работоспособность Linux-порта. Изображения, модели и аудио перечислены в индексах; их содержимое этим инструментом не интерпретируется.

## Каталог в репозитории

[Энциклопедия и JSON/CSV](../docs/encyclopedia/README.md) содержат подготовленный срез. Большие индексы сжаты стандартным gzip и хранятся через Git LFS. Полные оригинальные игровые тексты и сохранения отсутствуют.
