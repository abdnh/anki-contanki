import os
import json

from aqt import QIcon, QTabBar, mw, qconnect 
from aqt import QComboBox, QFormLayout, QHeaderView, QKeySequence, QLayout, QPoint, QShortcut
from aqt import QTableWidget, QTableWidgetItem
from aqt.qt import QAction, QDialog, QWidget, QPushButton, QCheckBox, QHBoxLayout, QVBoxLayout, QTabWidget
from aqt.qt import QKeySequenceEdit, QSpinBox, QLabel, QGridLayout, QGroupBox, QFont
from aqt.webview import AnkiWebView
from aqt.theme import theme_manager
from aqt.utils import showInfo, tooltip
from waitress import profile

from .funcs import get_button_icon
from .CONSTS import BUTTON_NAMES
from .svg import buildSVG, CONTROLLER_IMAGE_MAPS
from .profile import createProfile, getControllerList, getProfile, getProfileList, Profile, user_files_path, updateControllers, addon_path
from .actions import button_actions, state_actions
from .overlay import ControlsOverlay
from .components import ControlButton


class ContankiConfig(QDialog):
    
    def __init__(self, parent: QWidget, profile: Profile) -> None:
        if not profile:
            showInfo("Controller not detected. Connect using Bluetooth or USB, and press any button to initialise.")
        
        super().__init__(parent)
        self.setWindowTitle("Contanki Options")
        self.setFixedWidth(800)
        self.setFixedHeight(660)

        self.profile = profile
        self.layout = QVBoxLayout(self)
        self.tabBar = QTabWidget()
        self.tabs = dict()
        self.setupOptions()
        self.setup_bindings()
        
        self.saveButton = QPushButton(self)
        self.cancelButton = QPushButton(self)
        self.helpButton = QPushButton(self)

        self.saveButton.setText('Save')
        self.cancelButton.setText('Cancel')
        self.helpButton.setText('Help')
        
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)
        self.helpButton.clicked.connect(self.help)

        self.buttons = QWidget()
        self.buttons.layout = QHBoxLayout()

        self.buttons.layout.addWidget(self.helpButton)
        self.buttons.layout.addWidget(self.cancelButton)
        self.buttons.layout.addWidget(self.saveButton)
        
        self.buttons.layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.buttons.setLayout(self.buttons.layout)
        
        self.layout.addWidget(self.tabBar)
        self.layout.addWidget(self.buttons)

        self.setLayout(self.layout)
        self.open()


    def save(self) -> None:
        for key in self.options.keys():
            if type(self._options[key]) == int:
                self._options[key] = self.options[key].value()
            elif type(self._options[key]) == bool:
                self._options[key] = self.options[key].isChecked()
            elif key == "Custom Actions":
                for row in range(self.options[key].rowCount()):
                    self._options[self.options[key].item(row, 0).text()] = self.options[key].cellWidget(row, 1).keySequence().toString()
            elif key == "Flags":
                self._options["Flags"] = []
                for flag in self.options[key].findChildren(QCheckBox):
                    if flag.isChecked():
                        self._options["Flags"].append(int(flag.objectName()))

        mw.addonManager.writeConfig(__name__, self._options)

        states = [
            "all",
            "deckBrowser",
            "overview",
            "review",
            "question",
            "answer",
            "dialog",
        ]

        mods = {0:"No Modifier"}
        for i, mod in enumerate(self.profile.mods):
            if mod in BUTTON_NAMES[self.controller]:
                mods[i+1] = BUTTON_NAMES[self.controller][mod]
            else:
                mods[i+1] = "Modifier Unassigned"

        controls = self.tabs['bindings']

        for key in range(self.profile.len_axes):
            self.profile.axes_bindings[key] = self.axes_bindings[key].currentText()

        for state in states:
            for mod, title in mods.items():
                for button in range(self.profile.len_buttons):
                    if button in self.profile.mods or button not in controls.stateTabs[state].modTabs[mod].controls:
                        continue

                    action = controls.stateTabs[state].modTabs[mod].controls[button].currentText()
                    if 'inherit' in action:
                        action = ""
                    self.profile.updateBinding(state, mod, button, action, build_actions=False)

        self.profile.buildActions()
        self.profile.controller = self.corner.currentText()
        mw.controller.update_profile(self.profile)
        updateControllers(self.controller, self.profile.name)
        self.profile.save()
        self.close()


    def help(self) -> None:
        pass

    
    def changeProfile(self, profile: Profile = None) -> None:
        if not profile:
            profile = getProfile(self._profile.currentText())
        elif type(profile) == str:
            profile = getProfile(profile)
        if not profile:
            return
        self.profile = profile
        self.tabBar.removeTab(1)
        self.setupBindings()


    def findCustomActions(self) -> None:
        shortcuts = [shortcut for name, shortcut in self._options["Custom Actions"].items()]
        for action in mw.findChildren(QAction):
            if (scut := action.shortcut().toString()) != "" and scut not in shortcuts:
                if action.objectName() != "":
                    self._options["Custom Actions"][action.objectName()] = scut
                else:
                    self._options["Custom Actions"][scut] = scut

        for scut in mw.findChildren(QShortcut):
            if scut.key().toString() != "":
                self._options["Custom Actions"][scut.key().toString()] = scut.key().toString()


    def addProfile(self) -> None:
        new_profile = createProfile()
        if not new_profile: return
        self._profile.addItem(new_profile.name)
        self._profile.setCurrentIndex(-1)
        self.changeProfile(new_profile)


    def setupOptions(self) -> None:
        tab = QWidget()
        self.tabs['main'] = tab
        tab.layout = QGridLayout(tab)
        tab.layout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)

        main                    = QWidget()
        mouse                   = QWidget()
        flags                   = QGroupBox('Flags', self.tabs['main'])
        form                    = QWidget()
        axes                    = QWidget()

        main.layout             = QVBoxLayout()
        mouse.layout            = QGridLayout()
        flags.layout            = QFormLayout()
        form.layout             = QFormLayout()
        axes.layout             = QFormLayout()
        
        profileBar = QWidget()
        profileBar.layout = QHBoxLayout()
        self._profile = profileCombo = QComboBox(tab)
        profileCombo.addItems(p_list := getProfileList(include_defaults=False))
        profileCombo.setCurrentIndex(p_list.index(self.profile.name))
        profileCombo.currentTextChanged.connect(self.changeProfile)
        profileBar.layout.addWidget(QLabel("Profile", tab))
        profileBar.layout.addWidget(profileCombo)
        
        addButton = QPushButton('Add Profile', tab)
        addButton.clicked.connect(self.addProfile)
        profileBar.layout.addWidget(addButton)
        profileBar.layout.addWidget(QPushButton('Delete Profile', tab))
        profileBar.layout.addWidget(QPushButton('Rename Profile', tab))
        profileBar.setLayout(profileBar.layout)

        self._options = mw.addonManager.getConfig(__name__)
        self.findCustomActions()
        self.options = dict()

        flags.layout.setVerticalSpacing(20)
        form.layout.setVerticalSpacing(20)

        for key, value in self._options.items():
            if type(value) == int:
                self.options[key] = QSpinBox(tab)
                self.options[key].setMinimumWidth(70)
                self.options[key].setValue(value)
                form.layout.addRow(key, self.options[key])
            elif type(value) == bool:
                self.options[key] = QCheckBox(key, tab)
                self.options[key].setChecked(self._options[key])
                form.layout.addRow(self.options[key])
            elif key == "Custom Actions":
                self.options[key] = QTableWidget(len(value),2,tab)
                self.options[key].setHorizontalHeaderLabels(["Name", "Shortcut"])
                for row, (_key, _value) in enumerate(value.items()):
                    self.options[key].setItem(row, 0, QTableWidgetItem(_key,0))
                    self.options[key].setCellWidget(row, 1, QKeySequenceEdit(QKeySequence(_value)))
                self.options[key].horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeMode.Stretch)
                self.options[key].setColumnWidth(1, 70)
                tab.layout.addWidget(self.options[key],1,2)
            elif key == "Flags":
                self.options[key] = flags
                for flag in mw.flags.all():
                    check = QCheckBox(flag.label, tab)
                    check.setIcon(theme_manager.icon_from_resources(flag.icon))
                    check.setObjectName(str(flag.index))
                    if flag.index in self._options["Flags"]:
                        check.setChecked(True)
                    flags.layout.addWidget(check)
                flags.setLayout(flags.layout)
                tab.layout.addWidget(self.options[key],1,1)
            else: continue
        form.setLayout(form.layout)
        tab.layout.addWidget(form,1,0)

        # Axes
        
        self.axes_bindings = list()
        for axis, value in self.profile.axes_bindings.items():
            button = QComboBox()
            button.addItems([
                "Unassigned", 
                # "Buttons",
                "Cursor Horizontal",
                "Cursor Vertical",
                "Scroll Horizontal",
                "Scroll Vertical",
            ])
            button.setCurrentText(value)
            self.axes_bindings.append(button)
            axes.layout.addRow(f"Axis {axis}", button)

        axes.setLayout(axes.layout)
        tab.layout.addWidget(axes,2,0)

        tab.layout.addWidget(profileBar,0,0,1,3)
        
        # Finish

        tab.setLayout(tab.layout)
        self.tabBar.addTab(tab, "Options")

    def setup_bindings(self):
        tab = self.tabs['bindings'] = QTabWidget()
        
        corner = self.corner = QComboBox()
        controllers = getControllerList()
        for controller in controllers:
            corner.addItem(controller)
        controller = self.profile.controller
        corner.setCurrentIndex(controllers.index(controller))
        self.controller = controller = corner.currentText()
        corner.currentIndexChanged.connect(self.refresh_bindings)
        self.tabs['bindings'].setCornerWidget(corner)

        mods = {0:"Default"}
        for i, mod in enumerate(self.profile.mods):
            if mod in BUTTON_NAMES[self.controller]:
                mods[i+1] = BUTTON_NAMES[self.controller][mod]
            else:
                mods[i+1] = "Modifier Unassigned"

        tab.stateTabs = dict()
        for state, title in states.items():
            tab.stateTabs[state] = QTabWidget()
            tab.stateTabs[state].setObjectName(state)
            tab.stateTabs[state].modTabs = dict()
            for mod, mTitle in mods.items():
                tab.stateTabs[state].modTabs[mod] = widget = QWidget()
                widget.setObjectName(str(mod))
                widget.layout = QGridLayout()
                widget.controls = {
                    control: ControlButton(button, self.profile.controller, actions = state_actions[state])
                    for control, button 
                    in BUTTON_NAMES[self.profile.controller].items()
                }
                for button, control in widget.controls.items():
                    control.action.addItems(state_actions[state])
                    if button in self.profile.bindings[state][mod]:
                        control.action.setCurrentIndex(
                            state_actions[state].index(self.profile.bindings[state][mod][button])
                            )
                        qconnect(control.action.currentIndexChanged, self.updateInheritence) 
                        qconnect(control.action.currentIndexChanged, lambda: self.updateBinding(state, mod, button))
                row = col = 0
                for i, control in widget.controls.items():
                    widget.layout.addWidget(control, row, col)
                    if col == 2:
                        row += 1
                        col = 0
                    else:
                        col += 1
                widget.setLayout(widget.layout)
                if mod == 0:
                    tab.stateTabs[state].addTab(widget, "No Modifier")
                else:
                    tab.stateTabs[state].addTab(widget, QIcon(get_button_icon(controller, mods[mod])), mTitle)
            tab.stateTabs[state].setTabPosition(QTabWidget.TabPosition.South)
            tab.addTab(tab.stateTabs[state], title)
        self.updateInheritence()
        self.tabBar.addTab(tab, "Controls")

    def refresh_bindings(self) -> None:
        self.controller = self.profile.controller = self.corner.currentText()
        self.tabBar.removeTab(1)
        self.setup_bindings()
        self.tabBar.setCurrentIndex(1)

    def updateBinding(self, state, mod, button):
        tooltip(f"Updated Binding {state} {mod} {button}")
        action = self.tabs['bindings'].stateTabs[state].modTabs[mod].controls[button].currentText()
        self.profile.updateBinding(state, mod, button, action)

    def updateInheritence(self):
        for state in states:
            for mod in range(len(self.profile.mods) + 1):
                for button, control in self.tabs['bindings'].stateTabs[state].modTabs[mod].controls.items():
                    if button in self.profile.mods:
                        continue
                    inherited = None
                    if state != 'all' and button in (b := self.profile.bindings["all"][mod]):
                        inherited = b[button]
                    if (state == "question" or state == "answer") and button in self.profile.bindings["review"][mod]:
                        if action := self.profile.bindings["review"][mod][button]:
                            inherited = action
                    if inherited:
                        control.action.setItemText(0, inherited + " (inherit)")
                    else:
                        control.action.setItemText(0, "")


states = {
    "all": "Default",
    "deckBrowser": "Deck Browser", 
    "overview": "Deck Overview", 
    "review": "Review",
    "question": "Question", 
    "answer": "Answer",
    "dialog": "Dialogs",
}