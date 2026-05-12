// Visual Novel Runtime for Yandex Games
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
