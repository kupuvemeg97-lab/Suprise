"""
Core models for Visual Novel Editor
Чистые dataclass/JSON-модели без зависимости от PySide6
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class Sprite:
    """Представляет спрайт на сцене"""
    id: str
    image_path: str  # Относительный путь: assets/chapter_01/scene_001/sprites/hero.png
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    z_index: int = 0
    visible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "x": self.x,
            "y": self.y,
            "scale": self.scale,
            "rotation": self.rotation,
            "z_index": self.z_index,
            "visible": self.visible
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sprite":
        return cls(
            id=data["id"],
            image_path=data["image_path"],
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            scale=data.get("scale", 1.0),
            rotation=data.get("rotation", 0.0),
            z_index=data.get("z_index", 0),
            visible=data.get("visible", True)
        )


@dataclass
class Choice:
    """Представляет выбор игрока"""
    text: str
    target_scene: str  # ID сцены, куда перейти при выборе
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "target_scene": self.target_scene
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Choice":
        return cls(
            text=data["text"],
            target_scene=data["target_scene"]
        )


@dataclass
class Dialogue:
    """Представляет диалог в сцене"""
    character: str
    text: str
    background_color: str = "#FFFFFF"
    text_color: str = "#000000"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character": self.character,
            "text": self.text,
            "background_color": self.background_color,
            "text_color": self.text_color
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Dialogue":
        return cls(**data)


@dataclass
class Chapter:
    """Представляет главу (группа сцен)"""
    id: str
    name: str
    order: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chapter":
        return cls(
            id=data["id"],
            name=data["name"],
            order=data.get("order", 0)
        )


@dataclass
class Scene:
    """Представляет сцену визуальной новеллы"""
    id: str
    name: str
    chapter_id: Optional[str] = None  # Связь с главой
    background: Optional[str] = None  # Относительный путь: assets/chapter_01/scene_001/background.png
    sprites: List[Sprite] = field(default_factory=list)
    dialogues: List[Dialogue] = field(default_factory=list)
    next_scene: Optional[str] = None  # ID следующей сцены для перехода по клику
    choices: List[Choice] = field(default_factory=list)  # Выборы игрока
    music: Optional[str] = None  # Относительный путь: assets/chapter_01/scene_001/music/theme.mp3
    sound_effects: List[str] = field(default_factory=list)  # Список относительных путей к SFX
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "chapter_id": self.chapter_id,
            "background": self.background,
            "sprites": [s.to_dict() for s in self.sprites],
            "dialogues": [d.to_dict() for d in self.dialogues],
            "next_scene": self.next_scene,
            "choices": [c.to_dict() for c in self.choices],
            "music": self.music,
            "sound_effects": self.sound_effects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        sprites = [Sprite.from_dict(s) for s in data.get("sprites", [])]
        dialogues = [Dialogue.from_dict(d) for d in data.get("dialogues", [])]
        choices = [Choice.from_dict(c) for c in data.get("choices", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            chapter_id=data.get("chapter_id"),
            background=data.get("background"),
            sprites=sprites,
            dialogues=dialogues,
            next_scene=data.get("next_scene"),
            choices=choices,
            music=data.get("music"),
            sound_effects=data.get("sound_effects", [])
        )


@dataclass
class Project:
    """Представляет проект визуальной новеллы"""
    name: str
    version: str = "1.0"
    chapters: List[Chapter] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    start_scene: Optional[str] = None
    assets_folder: str = "assets"  # Имя папки для ассетов внутри проекта
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "chapters": [c.to_dict() for c in self.chapters],
            "scenes": [s.to_dict() for s in self.scenes],
            "start_scene": self.start_scene,
            "assets_folder": self.assets_folder
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        chapters = [Chapter.from_dict(c) for c in data.get("chapters", [])]
        scenes = [Scene.from_dict(s) for s in data.get("scenes", [])]
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            chapters=chapters,
            scenes=scenes,
            start_scene=data.get("start_scene"),
            assets_folder=data.get("assets_folder", "assets")
        )
    
    def save_to_json(self, filepath: str) -> None:
        """Сохраняет проект в JSON файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_json(cls, filepath: str) -> "Project":
        """Загружает проект из JSON файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def get_scene_by_id(self, scene_id: str) -> Optional[Scene]:
        """Получает сцену по ID"""
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None
    
    def get_chapter_by_id(self, chapter_id: str) -> Optional[Chapter]:
        """Получает главу по ID"""
        for chapter in self.chapters:
            if chapter.id == chapter_id:
                return chapter
        return None
    
    def add_scene(self, scene: Scene) -> None:
        """Добавляет сцену в проект"""
        self.scenes.append(scene)
    
    def remove_scene(self, scene_id: str) -> bool:
        """Удаляет сцену из проекта"""
        for i, scene in enumerate(self.scenes):
            if scene.id == scene_id:
                self.scenes.pop(i)
                return True
        return False
    
    def add_chapter(self, chapter: Chapter) -> None:
        """Добавляет главу в проект"""
        self.chapters.append(chapter)
    
    def remove_chapter(self, chapter_id: str) -> bool:
        """Удаляет главу из проекта"""
        for i, chapter in enumerate(self.chapters):
            if chapter.id == chapter_id:
                self.chapters.pop(i)
                return True
        return False
