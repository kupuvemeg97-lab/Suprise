"""
Main window of the Visual Novel Editor
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolBar, QStatusBar, QMenuBar, QMenu,
    QSplitter, QGroupBox, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QFormLayout, QLineEdit, 
    QDoubleSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtGui import QIcon, QKeySequence, QAction
from PySide6.QtCore import Qt, Signal

from src.core.models import Project, Scene, Sprite, Dialogue
from src.widgets.canvas import SceneCanvas


class MainWindow(QMainWindow):
    """Главное окно редактора визуальных новелл"""
    
    project_changed = Signal(object)  # Project
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Novel Editor for Yandex Games")
        self.setMinimumSize(1200, 800)
        
        self.current_project: Project = None
        self.current_scene: Scene = None
        
        self._init_ui()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._connect_signals()
    
    def _init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Splitter для resizable панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Левая панель - список сцен
        left_panel = self._create_scenes_panel()
        splitter.addWidget(left_panel)
        
        # Центральная панель - canvas
        center_panel = self._create_canvas_panel()
        splitter.addWidget(center_panel)
        
        # Правая панель - свойства
        right_panel = self._create_properties_panel()
        splitter.addWidget(right_panel)
        
        # Установка размеров splitter
        splitter.setSizes([250, 700, 300])
    
    def _create_scenes_panel(self) -> QWidget:
        """Панель списка сцен"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("Сцены")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Список сцен
        self.scenes_list = QListWidget()
        self.scenes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.scenes_list)
        
        # Кнопки управления сценами
        btn_layout = QHBoxLayout()
        
        self.add_scene_btn = QPushButton("+ Добавить")
        btn_layout.addWidget(self.add_scene_btn)
        
        self.remove_scene_btn = QPushButton("- Удалить")
        btn_layout.addWidget(self.remove_scene_btn)
        
        layout.addLayout(btn_layout)
        
        # Навигация стрелочками
        nav_layout = QHBoxLayout()
        
        self.prev_scene_btn = QPushButton("← Пред.")
        nav_layout.addWidget(self.prev_scene_btn)
        
        self.next_scene_btn = QPushButton("След. →")
        nav_layout.addWidget(self.next_scene_btn)
        
        layout.addLayout(nav_layout)
        
        return panel
    
    def _create_canvas_panel(self) -> QWidget:
        """Панель canvas"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("Редактор сцены")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Canvas
        self.canvas = SceneCanvas()
        layout.addWidget(self.canvas)
        
        # Инструменты масштабирования
        scale_layout = QHBoxLayout()
        
        scale_label = QLabel("Масштаб:")
        scale_layout.addWidget(scale_label)
        
        self.scale_down_btn = QPushButton("-")
        self.scale_down_btn.setFixedWidth(40)
        scale_layout.addWidget(self.scale_down_btn)
        
        self.scale_value = QLabel("100%")
        scale_layout.addWidget(self.scale_value)
        
        self.scale_up_btn = QPushButton("+")
        self.scale_up_btn.setFixedWidth(40)
        scale_layout.addWidget(self.scale_up_btn)
        
        layout.addLayout(scale_layout)
        
        return panel
    
    def _create_properties_panel(self) -> QWidget:
        """Панель свойств выбранного спрайта"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Заголовок
        title = QLabel("Свойства спрайта")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # Форма свойств
        form_layout = QFormLayout()
        
        self.prop_id = QLineEdit()
        self.prop_id.setReadOnly(True)
        form_layout.addRow("ID:", self.prop_id)
        
        self.prop_x = QDoubleSpinBox()
        self.prop_x.setRange(-10000, 10000)
        self.prop_x.setDecimals(1)
        form_layout.addRow("X:", self.prop_x)
        
        self.prop_y = QDoubleSpinBox()
        self.prop_y.setRange(-10000, 10000)
        self.prop_y.setDecimals(1)
        form_layout.addRow("Y:", self.prop_y)
        
        self.prop_scale = QDoubleSpinBox()
        self.prop_scale.setRange(0.1, 5.0)
        self.prop_scale.setDecimals(2)
        self.prop_scale.setValue(1.0)
        form_layout.addRow("Масштаб:", self.prop_scale)
        
        self.prop_rotation = QDoubleSpinBox()
        self.prop_rotation.setRange(-360, 360)
        self.prop_rotation.setDecimals(1)
        form_layout.addRow("Поворот:", self.prop_rotation)
        
        self.prop_visible = QCheckBox()
        form_layout.addRow("Видимый:", self.prop_visible)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        self.apply_props_btn = QPushButton("Применить")
        layout.addWidget(self.apply_props_btn)
        
        self.delete_sprite_btn = QPushButton("Удалить спрайт")
        layout.addWidget(self.delete_sprite_btn)
        
        layout.addStretch()
        
        return panel
    
    def _create_menu_bar(self):
        """Создание меню бара"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        
        new_action = QAction("Новый проект", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Открыть проект", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Сохранить проект", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Сохранить как...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Редактирование
        edit_menu = menubar.addMenu("Редактирование")
        
        add_sprite_action = QAction("Добавить спрайт", self)
        add_sprite_action.setShortcut(QKeySequence.StandardKey.InsertParagraph)
        add_sprite_action.triggered.connect(self.add_sprite)
        edit_menu.addAction(add_sprite_action)
        
        delete_action = QAction("Удалить выделенное", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        # Навигация
        nav_menu = menubar.addMenu("Навигация")
        
        prev_sprite_action = QAction("Пред. спрайт", self)
        prev_sprite_action.setShortcut(QKeySequence.StandardKey.MoveToPreviousLine)
        prev_sprite_action.triggered.connect(lambda: self.canvas.navigate_sprites("prev"))
        nav_menu.addAction(prev_sprite_action)
        
        next_sprite_action = QAction("След. спрайт", self)
        next_sprite_action.setShortcut(QKeySequence.StandardKey.MoveToNextLine)
        next_sprite_action.triggered.connect(lambda: self.canvas.navigate_sprites("next"))
        nav_menu.addAction(next_sprite_action)
    
    def _create_toolbar(self):
        """Создание toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        toolbar.addAction("Новый", self.new_project)
        toolbar.addAction("Открыть", self.open_project)
        toolbar.addAction("Сохранить", self.save_project)
        toolbar.addSeparator()
        toolbar.addAction("Добавить спрайт", self.add_sprite)
    
    def _create_status_bar(self):
        """Создание status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Готов")
    
    def _connect_signals(self):
        """Подключение сигналов"""
        # Сцены
        self.scenes_list.itemClicked.connect(self.on_scene_selected)
        self.add_scene_btn.clicked.connect(self.add_scene)
        self.remove_scene_btn.clicked.connect(self.remove_scene)
        self.prev_scene_btn.clicked.connect(self.prev_scene)
        self.next_scene_btn.clicked.connect(self.next_scene)
        
        # Canvas
        self.canvas.sprite_selected.connect(self.on_sprite_selected)
        
        # Масштабирование
        self.scale_up_btn.clicked.connect(lambda: self.canvas.scale_selected_sprite(1.1))
        self.scale_down_btn.clicked.connect(lambda: self.canvas.scale_selected_sprite(0.9))
        
        # Свойства
        self.apply_props_btn.clicked.connect(self.apply_sprite_properties)
        self.delete_sprite_btn.clicked.connect(self.canvas.remove_selected_sprite)
        
        # Изменение свойств
        self.prop_x.valueChanged.connect(self.update_sprite_position)
        self.prop_y.valueChanged.connect(self.update_sprite_position)
        self.prop_scale.valueChanged.connect(self.update_sprite_scale)
        self.prop_rotation.valueChanged.connect(self.update_sprite_rotation)
        self.prop_visible.stateChanged.connect(self.update_sprite_visibility)
    
    # Методы работы с проектом
    def new_project(self):
        """Создание нового проекта"""
        self.current_project = Project(name="New Project")
        self._update_scenes_list()
        self.statusbar.showMessage("Создан новый проект")
    
    def open_project(self):
        """Открытие проекта"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                self.current_project = Project.load_from_json(filepath)
                self._update_scenes_list()
                self.statusbar.showMessage(f"Открыт проект: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть проект: {e}")
    
    def save_project(self):
        """Сохранение проекта"""
        if not self.current_project:
            QMessageBox.warning(self, "Предупреждение", "Нет открытого проекта")
            return
        
        if not hasattr(self, '_save_path'):
            self.save_project_as()
        else:
            self.current_project.save_to_json(self._save_path)
            self.statusbar.showMessage(f"Проект сохранён: {self._save_path}")
    
    def save_project_as(self):
        """Сохранение проекта как"""
        if not self.current_project:
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить проект", "", "JSON Files (*.json)"
        )
        if filepath:
            self._save_path = filepath
            self.current_project.save_to_json(filepath)
            self.statusbar.showMessage(f"Проект сохранён: {filepath}")
    
    # Методы работы со сценами
    def _update_scenes_list(self):
        """Обновление списка сцен"""
        self.scenes_list.clear()
        if self.current_project:
            for scene in self.current_project.scenes:
                item = QListWidgetItem(scene.name)
                item.setData(Qt.ItemDataRole.UserRole, scene.id)
                self.scenes_list.addItem(item)
    
    def add_scene(self):
        """Добавление новой сцены"""
        if not self.current_project:
            QMessageBox.warning(self, "Предупреждение", "Сначала создайте проект")
            return
        
        scene_id = f"scene_{len(self.current_project.scenes) + 1}"
        scene_name = f"Сцена {len(self.current_project.scenes) + 1}"
        scene = Scene(id=scene_id, name=scene_name)
        self.current_project.add_scene(scene)
        self._update_scenes_list()
    
    def remove_scene(self):
        """Удаление сцены"""
        current_item = self.scenes_list.currentItem()
        if not current_item or not self.current_project:
            return
        
        scene_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.current_project.remove_scene(scene_id)
        self._update_scenes_list()
        self.canvas.clear()
    
    def on_scene_selected(self, item: QListWidgetItem):
        """Выбор сцены из списка"""
        if not self.current_project:
            return
        
        scene_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_scene = self.current_project.get_scene_by_id(scene_id)
        if self.current_scene:
            self.canvas.load_scene(self.current_scene)
            self.statusbar.showMessage(f"Сцена: {self.current_scene.name}")
    
    def prev_scene(self):
        """Переход к предыдущей сцене"""
        current_row = self.scenes_list.currentRow()
        if current_row > 0:
            self.scenes_list.setCurrentRow(current_row - 1)
            # Реально загружаем сцену после переключения
            item = self.scenes_list.item(current_row - 1)
            if item:
                self.on_scene_selected(item)
    
    def next_scene(self):
        """Переход к следующей сцене"""
        current_row = self.scenes_list.currentRow()
        if current_row < self.scenes_list.count() - 1:
            self.scenes_list.setCurrentRow(current_row + 1)
            # Реально загружаем сцену после переключения
            item = self.scenes_list.item(current_row + 1)
            if item:
                self.on_scene_selected(item)
    
    # Методы работы со спрайтами
    def add_sprite(self):
        """Добавление спрайта"""
        if not self.current_scene:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите сцену")
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выбрать спрайт", "", "Images (*.png *.jpg *.jpeg)"
        )
        if filepath:
            # TODO: Использовать ProjectIO.add_asset() для копирования в assets/
            # Сейчас используется абсолютный путь для тестирования GUI
            sprite_id = f"sprite_{len(self.current_scene.sprites) + 1}"
            sprite = Sprite(id=sprite_id, image_path=filepath, x=100, y=100)
            self.canvas.add_sprite(sprite)
            self.statusbar.showMessage(f"Добавлен спрайт: {filepath}")
    
    def delete_selected(self):
        """Удаление выделенного"""
        self.canvas.remove_selected_sprite()
    
    def on_sprite_selected(self, sprite_item):
        """Выбор спрайта на canvas"""
        sprite = sprite_item.sprite_data
        self.prop_id.setText(sprite.id)
        self.prop_x.setValue(sprite.x)
        self.prop_y.setValue(sprite.y)
        self.prop_scale.setValue(sprite.scale)
        self.prop_rotation.setValue(sprite.rotation)
        self.prop_visible.setChecked(sprite.visible)
        self.scale_value.setText(f"{int(sprite.scale * 100)}%")
    
    def apply_sprite_properties(self):
        """Применение свойств спрайта"""
        selected = self.canvas.get_selected_sprite()
        if not selected:
            return
        
        selected.sprite_data.x = self.prop_x.value()
        selected.sprite_data.y = self.prop_y.value()
        selected.sprite_data.scale = self.prop_scale.value()
        selected.sprite_data.rotation = self.prop_rotation.value()
        selected.sprite_data.visible = self.prop_visible.isChecked()
        selected._update_from_sprite()
    
    def update_sprite_position(self):
        """Обновление позиции спрайта"""
        selected = self.canvas.get_selected_sprite()
        if selected:
            selected.setPos(self.prop_x.value(), self.prop_y.value())
    
    def update_sprite_scale(self):
        """Обновление масштаба спрайта"""
        selected = self.canvas.get_selected_sprite()
        if selected:
            selected.set_scale(self.prop_scale.value())
            self.scale_value.setText(f"{int(self.prop_scale.value() * 100)}%")
    
    def update_sprite_rotation(self):
        """Обновление поворота спрайта"""
        selected = self.canvas.get_selected_sprite()
        if selected:
            selected.setRotation(self.prop_rotation.value())
    
    def update_sprite_visibility(self):
        """Обновление видимости спрайта"""
        selected = self.canvas.get_selected_sprite()
        if selected:
            selected.setVisible(self.prop_visible.isChecked())
