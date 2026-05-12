# Visual Novel Editor for Yandex Games

Приложение для создания визуальных новелл для Яндекс.Игр с удобным управлением, масштабированием спрайтов и навигацией по сценам.

## Архитектура (3 слоя)

1. **Editor** — Windows GUI на PySide6
2. **Project Model** — Чистые dataclass/JSON-модели без зависимости от PySide6
3. **Web Exporter** — Модуль экспорта в HTML5 для Яндекс.Игр

## Структура проекта

```
workspace/
├── main.py                     # Точка входа приложения
├── requirements.txt            # Зависимости (PySide6)
├── README.md                   # Документация
├── data/                       # JSON файлы проектов
├── assets/                     # Ресурсы по умолчанию
└── src/
    ├── __init__.py             # Инициализация приложения (GUI)
    ├── core/
    │   ├── __init__.py
    │   ├── models.py           # Dataclass модели (Sprite, Dialogue, Choice, Chapter, Scene, Project)
    │   ├── project_io.py       # Операции ввода-вывода проекта
    │   └── asset_manager.py    # Управление ассетами
    ├── gui/
    │   ├── __init__.py
    │   ├── main_window.py      # Главное окно приложения
    │   ├── scene_editor.py     # Редактор сцен
    │   ├── dialogue_editor.py  # Редактор диалогов
    │   └── asset_panel.py      # Панель ассетов
    └── exporter/
        ├── __init__.py
        ├── html5_exporter.py   # Экспортёр в HTML5
        └── templates/
            ├── index.html      # HTML шаблон игры
            ├── style.css       # CSS стили
            └── game.js         # Runtime визуальной новеллы
```

## Формат проекта

Проект поддерживает:
- ✅ Главы (Chapter)
- ✅ Сцены (Scene)
- ✅ Фон сцены (background)
- ✅ Список спрайтов с x/y/scale/rotation/z_index/visible
- ✅ Диалоги (Dialogue)
- ✅ Выборы игрока (Choice)
- ✅ Переход к следующей сцене (next_scene)
- ✅ Музыка сцены (music)
- ✅ Звуковые эффекты (sound_effects)
- ✅ Папка assets внутри проекта
- ✅ Относительные пути (не абсолютные пути Windows)

### Пример структуры путей:
```
assets/chapter_01/scene_001/backgrounds/bg_school.png
assets/chapter_01/scene_001/sprites/hero_normal.png
assets/chapter_01/scene_001/music/theme.mp3
```

## Установка

```bash
pip install -r requirements.txt
python main.py
```

## Экспорт в Яндекс.Игры

Экспортёр создаёт папку `build/yandex_games/` со структурой:
```
build/yandex_games/
├── index.html          # Главная страница
├── game.js             # Runtime визуальной новеллы
├── style.css           # Стили
├── project.json        # Данные проекта
└── assets/             # Копия всех ассетов
```

### Возможности runtime:
- Загрузка project.json
- Показ фона
- Показ спрайтов с масштабированием и вращением
- Вывод текста диалогов
- Переход по клику
- Выборы игрока (choices)
- Переключение сцен
- Фоновая музыка
- Звуковые эффекты
- Пауза звука при потере фокуса страницы
- Место для подключения Yandex Games SDK

## Модели данных

### Sprite
```python
id: str
image_path: str  # Относительный путь
x: float
y: float
scale: float
rotation: float
z_index: int
visible: bool
```

### Dialogue
```python
character: str
text: str
background_color: str
text_color: str
```

### Choice
```python
text: str
target_scene: str
```

### Chapter
```python
id: str
name: str
order: int
```

### Scene
```python
id: str
name: str
chapter_id: str
background: str
sprites: List[Sprite]
dialogues: List[Dialogue]
next_scene: str
choices: List[Choice]
music: str
sound_effects: List[str]
```

### Project
```python
name: str
version: str
chapters: List[Chapter]
scenes: List[Scene]
start_scene: str
assets_folder: str
```
