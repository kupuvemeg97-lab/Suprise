"""
Project I/O operations
Управление проектом: создание, сохранение, загрузка, работа с относительными путями
"""
import os
import json
import shutil
from pathlib import Path
from typing import Optional
from .models import Project, Scene, Chapter


class ProjectIO:
    """Класс для операций ввода-вывода проекта"""
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else None
        self.project: Optional[Project] = None
    
    def create_new_project(self, name: str, project_dir: str) -> Project:
        """Создаёт новый проект в указанной директории"""
        project_path = Path(project_dir)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Создаём структуру папок
        assets_dir = project_path / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        self.project_path = project_path
        self.project = Project(name=name, assets_folder="assets")
        self.save_project()
        
        return self.project
    
    def load_project(self, project_dir: str) -> Project:
        """Загружает проект из директории"""
        project_path = Path(project_dir)
        project_file = project_path / "project.json"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Проект не найден: {project_file}")
        
        self.project_path = project_path
        self.project = Project.load_from_json(str(project_file))
        
        return self.project
    
    def save_project(self) -> None:
        """Сохраняет текущий проект"""
        if self.project is None or self.project_path is None:
            raise ValueError("Проект не инициализирован")
        
        project_file = self.project_path / "project.json"
        self.project.save_to_json(str(project_file))
    
    def get_asset_path(self, relative_path: str) -> Path:
        """Получает полный путь к ассету относительно проекта"""
        if self.project_path is None:
            raise ValueError("Проект не инициализирован")
        return self.project_path / relative_path
    
    def make_relative_path(self, absolute_path: str) -> str:
        """Преобразует абсолютный путь в относительный относительно проекта"""
        if self.project_path is None:
            raise ValueError("Проект не инициализирован")
        
        abs_path = Path(absolute_path).resolve()
        rel_path = abs_path.relative_to(self.project_path.resolve())
        return str(rel_path).replace("\\", "/")  # Используем forward slashes для кроссплатформенности
    
    def add_asset(self, source_path: str, chapter_id: str, scene_id: str, asset_type: str) -> str:
        """
        Копирует ассет в правильную структуру папок проекта
        asset_type: 'background', 'sprite', 'music', 'sfx'
        Возвращает относительный путь к ассету
        """
        if self.project_path is None or self.project is None:
            raise ValueError("Проект не инициализирован")
        
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Ассет не найден: {source_path}")
        
        # Создаём структуру папок: assets/chapter_XX/scene_XXX/type/
        asset_dir = self.project_path / self.project.assets_folder / chapter_id / scene_id / asset_type
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        dest = asset_dir / source.name
        
        # Копируем файл
        shutil.copy2(source, dest)
        
        # Возвращаем относительный путь
        rel_path = dest.relative_to(self.project_path)
        return str(rel_path).replace("\\", "/")
    
    def get_scene_assets_dir(self, chapter_id: str, scene_id: str) -> Path:
        """Получает директорию для ассетов сцены"""
        if self.project_path is None or self.project is None:
            raise ValueError("Проект не инициализирован")
        return self.project_path / self.project.assets_folder / chapter_id / scene_id
    
    def export_project_structure(self) -> dict:
        """Возвращает структуру проекта для экспорта"""
        if self.project is None or self.project_path is None:
            raise ValueError("Проект не инициализирован")
        
        return {
            "project": self.project,
            "project_path": self.project_path,
            "assets_path": self.project_path / self.project.assets_folder
        }
