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
