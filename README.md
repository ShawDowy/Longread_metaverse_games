# Метавселенная уже здесь — лонгрид

Статический мультимедиа-лонгрид по материалам реферата «Основные направления развития современных интернет-технологий: метавселенные и гейм-индустрия».

## Что внутри

- `index.html` — единственная страница лонгрида;
- `assets/css/style.css` — оформление, адаптив, анимации;
- `assets/js/main.js` — меню, прогресс чтения, счётчики, табы, фильтры, аудиоплеер;
- `assets/img/` — фотографии и постер видео;
- `assets/fonts/` — локальные шрифты Manrope и Unbounded;
- `assets/audio/ambient.ogg` и `ambient.mp3` — авторский атмосферный аудиоландшафт (OGG + MP3 fallback);
- `assets/video/web3-game.webm` — анимационный ролик «Путь актива в Web3-игре»;
- `generate_audio.py`, `generate_video.py` — скрипты генерации медиа (для повторной сборки).

Сайт не требует сборки, Node.js, npm или внешних библиотек. Все ресурсы локальные.

## Как опубликовать на GitHub Pages

1. Создайте репозиторий на GitHub, например `metaverse-longread`.
2. Загрузите **содержимое папки `longread`** в корень репозитория. В корне должен оказаться `index.html`, рядом — папка `assets`.
3. Выполните:

```bash
git init
git add .
git commit -m "Add metaverse longread"
git branch -M main
git remote add origin https://github.com/USERNAME/metaverse-longread.git
git push -u origin main
```

4. В репозитории откройте **Settings → Pages**.
5. В разделе **Build and deployment** выберите:
   - Source: **Deploy from a branch**;
   - Branch: **main**, folder: **/ (root)**.
6. Сохраните настройки и подождите 1–2 минуты.
7. Ссылка будет вида:

```text
https://USERNAME.github.io/metaverse-longread/
```

Если назвать репозиторий `USERNAME.github.io`, сайт откроется по адресу `https://USERNAME.github.io/`.

## Как проверить локально

Из папки `longread`:

```bash
python3.11 -m http.server 8000
```

Откройте `http://127.0.0.1:8000/`.

## Медиа и лицензии

Фотографии взяты с Wikimedia Commons:

- InclusiveGameLab — CC BY-SA 4.0;
- Chongkian — CC BY-SA 4.0;
- NEXT Conference — CC BY 2.0;
- nakashi — CC BY-SA 2.0;
- O.sediqi93 — CC0;
- U.S. Department of Defense — общественное достояние.

Изображения кадрированы и тонированы для оформления. Схемы, анимация и аудио созданы автором лонгрида.

## Источники

Полный список с ссылками — в разделе «Источники и материалы» на самой странице. Основные материалы: ITU, WEF, NIST, OECD, Newzoo, ESA, MDPI, IEEE, EUR-Lex и официальные сайты кейсов.
