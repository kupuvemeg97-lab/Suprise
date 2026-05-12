"""
Canvas widget for editing scenes with sprites
"""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from typing import Optional, List

from src.core.models import Sprite, Scene


class SpriteItem(QGraphicsPixmapItem):
    """Графический элемент спрайта на canvas"""
    
    def __init__(self, sprite: Sprite, parent=None):
        super().__init__(parent)
        self.sprite_data = sprite
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self._update_from_sprite()
    
    def _update_from_sprite(self):
        """Обновляет позицию и масштаб из модели"""
        if self.sprite_data.image_path:
            pixmap = QPixmap(self.sprite_data.image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    int(pixmap.width() * self.sprite_data.scale),
                    int(pixmap.height() * self.sprite_data.scale),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
        
        self.setPos(self.sprite_data.x, self.sprite_data.y)
        self.setRotation(self.sprite_data.rotation)
        self.setVisible(self.sprite_data.visible)
    
    def update_sprite_data(self):
        """Обновляет модель данными из GUI"""
        self.sprite_data.x = self.pos().x()
        self.sprite_data.y = self.pos().y()
        self.sprite_data.rotation = self.rotation()
    
    def set_scale(self, scale: float):
        """Устанавливает масштаб спрайта"""
        self.sprite_data.scale = scale
        self._update_from_sprite()


class SceneCanvas(QGraphicsView):
    """Canvas для редактирования сцены"""
    
    sprite_selected = Signal(SpriteItem)
    sprite_moved = Signal(SpriteItem)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setBackgroundBrush(QBrush(QColor("#333333")))
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setMinimumSize(800, 600)
        
        self.current_scene: Optional[Scene] = None
        self.sprite_items: List[SpriteItem] = []
        
        # Подключение сигналов
        self.scene().selectionChanged.connect(self._on_selection_changed)
    
    def load_scene(self, scene: Scene):
        """Загружает сцену для редактирования"""
        self.clear()
        self.current_scene = scene
        self.sprite_items.clear()
        
        # Добавляем фон если есть
        if scene.background:
            bg_item = QGraphicsPixmapItem(QPixmap(scene.background))
            bg_item.setPos(0, 0)
            bg_item.setZValue(-1)
            self.scene().addItem(bg_item)
        
        # Добавляем спрайты
        for sprite in scene.sprites:
            sprite_item = SpriteItem(sprite)
            self.sprite_items.append(sprite_item)
            self.scene().addItem(sprite_item)
    
    def clear(self):
        """Очищает canvas"""
        self.scene().clear()
        self.sprite_items.clear()
        self.current_scene = None
    
    def add_sprite(self, sprite: Sprite) -> SpriteItem:
        """Добавляет новый спрайт на сцену"""
        sprite_item = SpriteItem(sprite)
        self.sprite_items.append(sprite_item)
        self.scene().addItem(sprite_item)
        if self.current_scene:
            self.current_scene.sprites.append(sprite)
        return sprite_item
    
    def remove_selected_sprite(self):
        """Удаляет выбранный спрайт"""
        selected = self.scene().selectedItems()
        for item in selected:
            if isinstance(item, SpriteItem):
                item.update_sprite_data()
                if self.current_scene:
                    if item.sprite_data in self.current_scene.sprites:
                        self.current_scene.sprites.remove(item.sprite_data)
                self.sprite_items.remove(item)
                self.scene().removeItem(item)
    
    def get_selected_sprite(self) -> Optional[SpriteItem]:
        """Получает выбранный спрайт"""
        selected = self.scene().selectedItems()
        if selected and isinstance(selected[0], SpriteItem):
            return selected[0]
        return None
    
    def _on_selection_changed(self):
        """Обработчик изменения выделения"""
        selected = self.get_selected_sprite()
        if selected:
            selected.update_sprite_data()
            self.sprite_selected.emit(selected)
    
    def scale_selected_sprite(self, scale_factor: float):
        """Масштабирует выбранный спрайт"""
        selected = self.get_selected_sprite()
        if selected:
            current_scale = selected.sprite_data.scale
            new_scale = max(0.1, min(5.0, current_scale * scale_factor))
            selected.set_scale(new_scale)
            self.sprite_moved.emit(selected)
    
    def navigate_sprites(self, direction: str):
        """Навигация по спрайтам стрелочками"""
        if not self.sprite_items:
            return
        
        current = self.get_selected_sprite()
        if not current:
            self.sprite_items[0].setSelected(True)
            return
        
        idx = self.sprite_items.index(current)
        current.setSelected(False)
        
        if direction == "next":
            next_idx = (idx + 1) % len(self.sprite_items)
        elif direction == "prev":
            next_idx = (idx - 1) % len(self.sprite_items)
        else:
            return
        
        self.sprite_items[next_idx].setSelected(True)
    
    def save_current_positions(self):
        """Сохраняет текущие позиции всех спрайтов в модель"""
        if not self.current_scene:
            return
        for item in self.sprite_items:
            item.update_sprite_data()
