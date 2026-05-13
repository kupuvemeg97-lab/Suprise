"""
Scene Canvas widget for Visual Novel Editor
Отображение сцены с фоном и спрайтами
"""
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QPen, QColor
from PySide6.QtCore import Qt, Signal, QPointF, QRectF


class SpriteItem(QGraphicsPixmapItem):
    """Графический элемент спрайта с поддержкой данных модели"""
    
    def __init__(self, sprite_data, parent=None):
        super().__init__(parent)
        self.sprite_data = sprite_data
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        
        # Установка начальных параметров из sprite_data
        self._update_from_sprite()
    
    def _update_from_sprite(self):
        """Обновляет отображение из данных спрайта"""
        # Загрузка изображения
        if self.sprite_data.image_path:
            pixmap = QPixmap(self.sprite_data.image_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap)
                
                # Применение масштаба
                self.set_scale(self.sprite_data.scale)
                
                # Применение поворота
                self.setRotation(self.sprite_data.rotation)
                
                # Применение видимости
                self.setVisible(self.sprite_data.visible)
                
                # Применение позиции
                self.setPos(self.sprite_data.x, self.sprite_data.y)
                
                # Применение z-index
                self.setZValue(self.sprite_data.z_index)
                
                # Добавление рамки при выделении
                self.setPen(QPen(QColor(0, 128, 255), 2))
    
    def set_scale(self, value):
        """Устанавливает масштаб спрайта"""
        self.setScale(value)
        self.sprite_data.scale = value
    
    def itemChange(self, change, value):
        """Обрабатывает изменения элемента"""
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionHasChanged:
            # Обновляем координаты в sprite_data при перемещении
            new_pos = value.toPoint() if isinstance(value, QPointF) else value
            self.sprite_data.x = float(new_pos.x()) if hasattr(new_pos, 'x') else float(new_pos[0])
            self.sprite_data.y = float(new_pos.y()) if hasattr(new_pos, 'y') else float(new_pos[1])
        return super().itemChange(change, value)
    
    def mouseReleaseEvent(self, event):
        """Обработка отпускания мыши - запись координат"""
        super().mouseReleaseEvent(event)
        pos = self.pos()
        self.sprite_data.x = pos.x()
        self.sprite_data.y = pos.y()


class SceneCanvas(QGraphicsView):
    """Canvas для отображения и редактирования сцены"""
    
    sprite_selected = Signal(object)  # Передаёт SpriteItem
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Создание сцены
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Настройка view
        self.setRenderHint(QGraphicsView.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Фон сцены (серый)
        self.scene.setBackgroundBrush(QColor(64, 64, 64))
        
        # Текущая сцена (модель)
        self.current_scene = None
        
        # Спрайты на канвасе
        self.sprite_items = {}  # sprite_id -> SpriteItem
    
    def clear(self):
        """Очищает canvas"""
        self.scene.clear()
        self.scene.setBackgroundBrush(QColor(64, 64, 64))
        self.current_scene = None
        self.sprite_items.clear()
    
    def load_scene(self, scene):
        """Загружает сцену на canvas"""
        self.clear()
        self.current_scene = scene
        
        # Установка фона сцены если есть
        if scene.background:
            bg_pixmap = QPixmap(scene.background)
            if not bg_pixmap.isNull():
                # Масштабируем фон под размер view
                bg_item = QGraphicsPixmapItem(bg_pixmap)
                bg_item.setPos(0, 0)
                bg_item.setZValue(-1000)  # Фон всегда позади
                self.scene.addItem(bg_item)
        
        # Добавление спрайтов
        for sprite in scene.sprites:
            self.add_sprite(sprite)
    
    def add_sprite(self, sprite):
        """Добавляет спрайт на canvas"""
        if sprite.id in self.sprite_items:
            return  # Уже существует
        
        sprite_item = SpriteItem(sprite)
        self.scene.addItem(sprite_item)
        self.sprite_items[sprite.id] = sprite_item
        
        # Добавляем спрайт в current_scene.sprites если его там ещё нет
        if self.current_scene and sprite not in self.current_scene.sprites:
            self.current_scene.sprites.append(sprite)
        
        # Подключение сигнала выделения
        sprite_item.installSceneEventFilter(self)
    
    def remove_selected_sprite(self):
        """Удаляет выделенный спрайт"""
        selected = self.get_selected_sprite()
        if selected:
            sprite_id = selected.sprite_data.id
            self.scene.removeItem(selected)
            del self.sprite_items[sprite_id]
            
            # Удаляем из current_scene
            if self.current_scene:
                self.current_scene.sprites = [
                    s for s in self.current_scene.sprites if s.id != sprite_id
                ]
    
    def get_selected_sprite(self):
        """Получает выделенный спрайт"""
        for item in self.scene.selectedItems():
            if isinstance(item, SpriteItem):
                return item
        return None
    
    def scale_selected_sprite(self, factor):
        """Масштабирует выделенный спрайт"""
        selected = self.get_selected_sprite()
        if selected:
            new_scale = selected.sprite_data.scale * factor
            new_scale = max(0.1, min(5.0, new_scale))  # Ограничение 0.1-5.0
            selected.set_scale(new_scale)
    
    def navigate_sprites(self, direction):
        """Переключает выделение между спрайтами"""
        if not self.sprite_items:
            return
        
        sprite_list = list(self.sprite_items.values())
        current = self.get_selected_sprite()
        
        if current is None:
            # Выделяем первый
            sprite_list[0].setSelected(True)
            self.sprite_selected.emit(sprite_list[0])
            return
        
        # Находим текущий индекс
        try:
            current_idx = sprite_list.index(current)
        except ValueError:
            current_idx = -1
        
        # Снимаем выделение со всех
        for item in sprite_list:
            item.setSelected(False)
        
        # Вычисляем новый индекс
        if direction == "next":
            new_idx = (current_idx + 1) % len(sprite_list)
        else:  # prev
            new_idx = (current_idx - 1) % len(sprite_list)
        
        # Выделяем новый спрайт
        new_item = sprite_list[new_idx]
        new_item.setSelected(True)
        self.sprite_selected.emit(new_item)
    
    def sceneEventFilter(self, watched, event):
        """Фильтр событий сцены для обработки выделения"""
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.Type.GraphicsSceneMouseClick:
            if isinstance(watched, SpriteItem):
                self.sprite_selected.emit(watched)
        return super().sceneEventFilter(watched, event)
