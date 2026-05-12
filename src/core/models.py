"""
Core models for Visual Novel Editor
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json


@dataclass
class Sprite:
    """Представляет спрайт на сцене"""
    id: str
    image_path: str
    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    visible: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_path": self.image_path,
            "x": self.x,
            "y": self.y,
            "scale": self.scale,
            "rotation": self.rotation,
            "visible": self.visible
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Sprite":
        return cls(**data)


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
class Scene:
    """Представляет сцену визуальной новеллы"""
    id: str
    name: str
    background: Optional[str] = None
    sprites: List[Sprite] = field(default_factory=list)
    dialogues: List[Dialogue] = field(default_factory=list)
    next_scene: Optional[str] = None
    choices: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "background": self.background,
            "sprites": [s.to_dict() for s in self.sprites],
            "dialogues": [d.to_dict() for d in self.dialogues],
            "next_scene": self.next_scene,
            "choices": self.choices
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        sprites = [Sprite.from_dict(s) for s in data.get("sprites", [])]
        dialogues = [Dialogue.from_dict(d) for d in data.get("dialogues", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            background=data.get("background"),
            sprites=sprites,
            dialogues=dialogues,
            next_scene=data.get("next_scene"),
            choices=data.get("choices", [])
        )


@dataclass
class Project:
    """Представляет проект визуальной новеллы"""
    name: str
    version: str = "1.0"
    scenes: List[Scene] = field(default_factory=list)
    start_scene: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "scenes": [s.to_dict() for s in self.scenes],
            "start_scene": self.start_scene
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        scenes = [Scene.from_dict(s) for s in data.get("scenes", [])]
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            scenes=scenes,
            start_scene=data.get("start_scene")
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
