"""
Asset Manager
Управление ассетами проекта: валидация, кэширование, относительные пути
"""
from pathlib import Path
from typing import Optional, Dict, List
from .models import Project


class AssetManager:
    """Менеджер ассетов проекта"""
    
    def __init__(self, project: Project, project_path: Path):
        self.project = project
        self.project_path = project_path
        self.assets_cache: Dict[str, Path] = {}
    
    def get_full_path(self, relative_path: str) -> Optional[Path]:
        """Получает полный путь к ассету по относительному пути"""
        if not relative_path:
            return None
        
        full_path = self.project_path / relative_path
        if full_path.exists():
            self.assets_cache[relative_path] = full_path
            return full_path
        return None
    
    def validate_asset(self, relative_path: str) -> bool:
        """Проверяет существование ассета"""
        full_path = self.get_full_path(relative_path)
        return full_path is not None and full_path.exists()
    
    def validate_all_assets(self) -> Dict[str, List[str]]:
        """
        Проверяет все ассеты проекта
        Возвращает словарь с отсутствующими ассетами по типам
        """
        missing = {
            "backgrounds": [],
            "sprites": [],
            "music": [],
            "sound_effects": []
        }
        
        for scene in self.project.scenes:
            # Проверка фона
            if scene.background and not self.validate_asset(scene.background):
                missing["backgrounds"].append(f"{scene.id}: {scene.background}")
            
            # Проверка спрайтов
            for sprite in scene.sprites:
                if not self.validate_asset(sprite.image_path):
                    missing["sprites"].append(f"{scene.id}/{sprite.id}: {sprite.image_path}")
            
            # Проверка музыки
            if scene.music and not self.validate_asset(scene.music):
                missing["music"].append(f"{scene.id}: {scene.music}")
            
            # Проверка звуковых эффектов
            for sfx in scene.sound_effects:
                if not self.validate_asset(sfx):
                    missing["sound_effects"].append(f"{scene.id}: {sfx}")
        
        return missing
    
    def get_scene_assets(self, scene_id: str) -> Dict[str, List[str]]:
        """Получает список всех ассетов для сцены"""
        scene = self.project.get_scene_by_id(scene_id)
        if not scene:
            return {"backgrounds": [], "sprites": [], "music": [], "sound_effects": []}
        
        assets = {
            "backgrounds": [scene.background] if scene.background else [],
            "sprites": [s.image_path for s in scene.sprites],
            "music": [scene.music] if scene.music else [],
            "sound_effects": scene.sound_effects.copy()
        }
        
        return assets
    
    def collect_all_asset_paths(self) -> List[str]:
        """Собирает все уникальные пути к ассетам в проекте"""
        all_paths = set()
        
        for scene in self.project.scenes:
            if scene.background:
                all_paths.add(scene.background)
            
            for sprite in scene.sprites:
                all_paths.add(sprite.image_path)
            
            if scene.music:
                all_paths.add(scene.music)
            
            for sfx in scene.sound_effects:
                all_paths.add(sfx)
        
        return list(all_paths)
    
    def get_assets_directory(self, chapter_id: str, scene_id: str, asset_type: str) -> Path:
        """Получает директорию для конкретного типа ассетов"""
        return self.project_path / self.project.assets_folder / chapter_id / scene_id / asset_type
    
    def ensure_assets_directory(self, chapter_id: str, scene_id: str, asset_type: str) -> Path:
        """Создаёт директорию для ассетов если она не существует"""
        dir_path = self.get_assets_directory(chapter_id, scene_id, asset_type)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
