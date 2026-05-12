"""
HTML5 Exporter for Yandex Games
Экспортирует проект в готовую HTML5-игру для Яндекс.Игр
"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional
from ..core.models import Project


class HTML5Exporter:
    """Экспортёр проекта в HTML5 формат для Яндекс.Игр"""
    
    def __init__(self, project: Project, project_path: Path):
        self.project = project
        self.project_path = project_path
        self.template_dir = Path(__file__).parent / "templates"
    
    def export(self, output_dir: str) -> Path:
        """
        Экспортирует проект в папку build/yandex_games/
        Возвращает путь к созданной директории
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Копируем шаблоны
        self._copy_templates(output_path)
        
        # Копируем project.json
        self._export_project_json(output_path)
        
        # Копируем ассеты
        self._copy_assets(output_path)
        
        return output_path
    
    def _copy_templates(self, output_path: Path) -> None:
        """Копирует HTML/CSS/JS шаблоны в выходную директорию"""
        templates = {
            "index.html": output_path / "index.html",
            "game.js": output_path / "game.js",
            "style.css": output_path / "style.css"
        }
        
        for template_name, dest_path in templates.items():
            src_path = self.template_dir / template_name
            if src_path.exists():
                shutil.copy2(src_path, dest_path)
            else:
                raise FileNotFoundError(f"Шаблон не найден: {src_path}")
    
    def _export_project_json(self, output_path: Path) -> None:
        """Сохраняет project.json в выходную директорию"""
        dest_path = output_path / "project.json"
        self.project.save_to_json(str(dest_path))
    
    def _copy_assets(self, output_path: Path) -> None:
        """Копирует все ассеты проекта в выходную директорию"""
        assets_src = self.project_path / self.project.assets_folder
        assets_dest = output_path / self.project.assets_folder
        
        if assets_src.exists():
            shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)
        else:
            assets_dest.mkdir(parents=True, exist_ok=True)


def generate_templates(template_dir: Path) -> None:
    """Генерирует файлы шаблонов если они не существуют"""
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # index.html
    index_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Novel</title>
    <link rel="stylesheet" href="style.css">
    <!-- Yandex Games SDK -->
    <script src="https://yandex.ru/games/sdk/v2"></script>
</head>
<body>
    <div id="game-container">
        <canvas id="game-canvas"></canvas>
        <div id="ui-layer">
            <div id="dialogue-box" class="hidden">
                <div id="character-name"></div>
                <div id="dialogue-text"></div>
            </div>
            <div id="choices-container" class="hidden"></div>
            <div id="click-overlay"></div>
        </div>
        <audio id="bgm-player" loop></audio>
        <audio id="sfx-player"></audio>
    </div>
    <script src="game.js"></script>
</body>
</html>
'''
    
    # style.css
    style_css = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    overflow: hidden;
    background-color: #000;
    font-family: Arial, sans-serif;
}

#game-container {
    position: relative;
    width: 100vw;
    height: 100vh;
}

#game-canvas {
    display: block;
    width: 100%;
    height: 100%;
}

#ui-layer {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

#dialogue-box {
    position: absolute;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 800px;
    padding: 20px;
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 10px;
    pointer-events: auto;
}

#character-name {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 10px;
}

#dialogue-text {
    font-size: 16px;
    line-height: 1.5;
}

#choices-container {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    gap: 10px;
    pointer-events: auto;
}

.choice-button {
    padding: 15px 30px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    border: 2px solid white;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}

.choice-button:hover {
    background-color: rgba(0, 0, 0, 0.9);
}

#click-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: auto;
    cursor: pointer;
}

.hidden {
    display: none !important;
}
'''
    
    # game.js
    game_js = '''// Visual Novel Runtime for Yandex Games
class VisualNovelGame {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.dialogueBox = document.getElementById('dialogue-box');
        this.characterNameEl = document.getElementById('character-name');
        this.dialogueTextEl = document.getElementById('dialogue-text');
        this.choicesContainer = document.getElementById('choices-container');
        this.clickOverlay = document.getElementById('click-overlay');
        this.bgmPlayer = document.getElementById('bgm-player');
        this.sfxPlayer = document.getElementById('sfx-player');
        
        this.project = null;
        this.currentScene = null;
        this.currentDialogueIndex = 0;
        this.images = {};
        this.audio = {};
        
        this.init();
    }
    
    async init() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Загрузка проекта
        await this.loadProject();
        
        // Обработчики событий
        this.clickOverlay.addEventListener('click', () => this.handleClick());
        
        // Пауза аудио при потере фокуса
        window.addEventListener('blur', () => this.pauseAudio());
        window.addEventListener('focus', () => this.resumeAudio());
        
        // Инициализация Yandex Games SDK (место для подключения)
        this.initYandexSDK();
        
        // Запуск игры
        this.startGame();
    }
    
    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    async loadProject() {
        const response = await fetch('project.json');
        this.project = await response.json();
    }
    
    initYandexSDK() {
        // Место для подключения Yandex Games SDK
        // YaGames.init().then(ysdk => {
        //     console.log('Yandex SDK initialized');
        //     // Здесь можно добавить рекламу, сохранения и т.д.
        // });
    }
    
    async startGame() {
        const startSceneId = this.project.start_scene || this.project.scenes[0].id;
        await this.loadScene(startSceneId);
    }
    
    async loadScene(sceneId) {
        this.currentScene = this.project.scenes.find(s => s.id === sceneId);
        if (!this.currentScene) {
            console.error('Scene not found:', sceneId);
            return;
        }
        
        this.currentDialogueIndex = 0;
        
        // Загрузка фона
        if (this.currentScene.background) {
            await this.loadImage(this.currentScene.background);
        }
        
        // Загрузка спрайтов
        for (const sprite of this.currentScene.sprites) {
            await this.loadImage(sprite.image_path);
        }
        
        // Загрузка музыки
        if (this.currentScene.music) {
            this.bgmPlayer.src = this.currentScene.music;
            this.bgmPlayer.play().catch(e => console.log('Audio play failed:', e));
        }
        
        // Загрузка звуковых эффектов
        for (const sfx of this.currentScene.sound_effects) {
            await this.loadAudio(sfx);
        }
        
        this.renderScene();
        this.showDialogue();
    }
    
    loadImage(path) {
        return new Promise((resolve, reject) => {
            if (this.images[path]) {
                resolve(this.images[path]);
                return;
            }
            
            const img = new Image();
            img.onload = () => {
                this.images[path] = img;
                resolve(img);
            };
            img.onerror = reject;
            img.src = path;
        });
    }
    
    loadAudio(path) {
        return new Promise((resolve, reject) => {
            if (this.audio[path]) {
                resolve(this.audio[path]);
                return;
            }
            
            const audio = new Audio(path);
            audio.addEventListener('canplaythrough', () => {
                this.audio[path] = audio;
                resolve(audio);
            });
            audio.addEventListener('error', reject);
        });
    }
    
    renderScene() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Рендер фона
        if (this.currentScene.background && this.images[this.currentScene.background]) {
            this.drawImageFit(this.images[this.currentScene.background]);
        }
        
        // Рендер спрайтов (сортировка по z_index)
        const sortedSprites = [...this.currentScene.sprites]
            .filter(s => s.visible)
            .sort((a, b) => a.z_index - b.z_index);
        
        for (const sprite of sortedSprites) {
            if (this.images[sprite.image_path]) {
                this.drawSprite(sprite);
            }
        }
    }
    
    drawImageFit(img) {
        const scale = Math.max(
            this.canvas.width / img.width,
            this.canvas.height / img.height
        );
        const width = img.width * scale;
        const height = img.height * scale;
        const x = (this.canvas.width - width) / 2;
        const y = (this.canvas.height - height) / 2;
        this.ctx.drawImage(img, x, y, width, height);
    }
    
    drawSprite(sprite) {
        const img = this.images[sprite.image_path];
        const imgWidth = img.width * sprite.scale;
        const imgHeight = img.height * sprite.scale;
        const x = sprite.x - imgWidth / 2;
        const y = sprite.y - imgHeight / 2;
        
        this.ctx.save();
        this.ctx.translate(sprite.x, sprite.y);
        this.ctx.rotate((sprite.rotation * Math.PI) / 180);
        this.ctx.drawImage(img, -imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight);
        this.ctx.restore();
    }
    
    showDialogue() {
        if (!this.currentScene.dialogues || this.currentDialogueIndex >= this.currentScene.dialogues.length) {
            this.dialogueBox.classList.add('hidden');
            if (this.currentScene.next_scene) {
                // Показываем индикатор перехода
                this.clickOverlay.style.cursor = 'pointer';
            }
            return;
        }
        
        const dialogue = this.currentScene.dialogues[this.currentDialogueIndex];
        this.characterNameEl.textContent = dialogue.character;
        this.dialogueTextEl.textContent = dialogue.text;
        this.dialogueBox.style.backgroundColor = dialogue.background_color;
        this.dialogueBox.style.color = dialogue.text_color;
        this.dialogueBox.classList.remove('hidden');
    }
    
    handleClick() {
        // Если есть выборы, игнорируем клик по оверлею
        if (!this.choicesContainer.classList.contains('hidden')) {
            return;
        }
        
        // Если есть диалоги, переходим к следующему
        if (this.currentScene.dialogues && 
            this.currentDialogueIndex < this.currentScene.dialogues.length) {
            this.currentDialogueIndex++;
            this.showDialogue();
            return;
        }
        
        // Если есть next_scene, переходим к следующей сцене
        if (this.currentScene.next_scene) {
            this.loadScene(this.currentScene.next_scene);
            return;
        }
        
        // Если есть выборы, показываем их
        if (this.currentScene.choices && this.currentScene.choices.length > 0) {
            this.showChoices();
        }
    }
    
    showChoices() {
        this.choicesContainer.innerHTML = '';
        this.choicesContainer.classList.remove('hidden');
        
        for (const choice of this.currentScene.choices) {
            const button = document.createElement('button');
            button.className = 'choice-button';
            button.textContent = choice.text;
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                this.choicesContainer.classList.add('hidden');
                this.loadScene(choice.target_scene);
            });
            this.choicesContainer.appendChild(button);
        }
    }
    
    pauseAudio() {
        this.bgmPlayer.pause();
    }
    
    resumeAudio() {
        if (!this.bgmPlayer.paused) {
            this.bgmPlayer.play().catch(e => console.log('Audio resume failed:', e));
        }
    }
}

// Запуск игры после загрузки страницы
window.addEventListener('load', () => {
    new VisualNovelGame();
});
'''
    
    # Запись файлов
    (template_dir / "index.html").write_text(index_html, encoding='utf-8')
    (template_dir / "style.css").write_text(style_css, encoding='utf-8')
    (template_dir / "game.js").write_text(game_js, encoding='utf-8')
