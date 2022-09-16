"""
Contanki's configuration dialog and associated classes.
"""

from __future__ import annotations

from functools import partial
from typing import Any, Callable, Iterable, Type

from aqt import qconnect
from aqt.qt import QTableWidget, QTableWidgetItem, QComboBox, QFormLayout, QHeaderView
from aqt.qt import (
    QDialog,
    QWidget,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QTabWidget,
    QInputDialog,
    QKeySequenceEdit,
    QSpinBox,
    QLabel,
    QGridLayout,
    QGroupBox,
    Qt,
    QKeySequence,
    QLayout,
    QSizePolicy,
)
from aqt.theme import theme_manager
from aqt.utils import showInfo, getText, askUser

from aqt import mw as _mw

assert _mw is not None
mw = _mw

from .controller import get_controller_list
from .funcs import get_config, get_debug_str
from .profile import (
    Profile,
    create_profile,
    delete_profile,
    get_profile,
    get_profile_list,
    update_controllers,
)
from .actions import QUICK_SELECT_ACTIONS, STATE_ACTIONS
from .icons import ButtonIcon, get_button_icon
from .utils import State

alignment = Qt.AlignmentFlag

states: dict[State, str] = {
    "all": "Default",
    "deckBrowser": "Deck Browser",
    "overview": "Overview",
    "review": "Review",
    "question": "Question",
    "answer": "Answer",
    "dialog": "Dialogs",
}


class ContankiConfig(QDialog):
    """Contanki's config dialog.

    Allows the user to change the profile, settings, and bindings."""

    def __init__(self, parent: QWidget, profile: Profile | None) -> None:
        if profile is None:
            showInfo(
                "Controller not detected. Connect your controller and press any button to initialise."  # pylint: disable=line-too-long
            )
            return
        self.loaded = False

        # Initialise internal variables
        self.profile = profile.copy()
        self.config = get_config()
        self.to_delete: list[str] = list()
        self.profile_hash = hash(profile)

        # Initialise dialog
        super().__init__(parent)
        self.setWindowTitle("Contanki Options")
        self.setObjectName("Contanki Options")
        self.setFixedWidth(800)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.setAlignment(alignment.AlignTop)

        # Initialise main tabs (Options, Controls)
        self.tab_bar = QTabWidget()
        self.tab_bar.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.options_page = OptionsPage(self)
        self.tab_bar.addTab(self.options_page, "Options")
        self.controls_page = ControlsPage(self)
        self.tab_bar.addTab(self.controls_page, "Controls")
        layout.addWidget(self.tab_bar)

        # Add buttons
        _buttons = [
            Button(self, "Save", self.save),
            Button(self, "Cancel", self.close),
            Button(self, "Help", self.help),
        ]
        _buttons[0].setDefault(True)
        buttons = Container(self, QHBoxLayout, _buttons)
        buttons.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        buttons.layout().setAlignment(alignment.AlignRight)
        layout.addWidget(buttons)

        # Open
        self.setLayout(layout)
        self.resize(self.sizeHint())
        self.loaded = True
        self.open()

    def save(self) -> None:
        """Save changes, and load them. Used on close."""
        for profile in self.to_delete:
            delete_profile(profile)

        mw.addonManager.writeConfig(__name__, self.config)
        self.profile.save()
        update_controllers(self.profile.controller, self.profile.name)
        mw.contanki.profile = self.profile  # type: ignore
        self.close()

    def help(self) -> None:
        """Open the Contanki help page."""
        showInfo(get_debug_str(), textFormat="rich")

    def change_profile(self, profile_name: str) -> None:
        """Used when the user changes the profile in the profile list.

        Will only update the main profile if Save is chosen."""
        if hash(self.profile) != self.profile_hash and askUser(
            "Save changes to current profile?", self
        ):
            self.profile.save()
        profile = get_profile(profile_name)
        if profile is None:
            raise ValueError(f"Profile {profile_name} not found.")
        self.profile = profile
        self.profile_hash = hash(profile)
        self.tab_bar.removeTab(0)
        self.tab_bar.removeTab(0)
        self.options_page = OptionsPage(self)
        self.tab_bar.addTab(self.options_page, "Options")
        self.controls_page = ControlsPage(self)
        self.tab_bar.addTab(self.controls_page, "Controls")

    def get_custom_actions(self) -> list[str]:
        """Get the names of custom actions."""
        return self.options_page.custom_actions.get_actions()

    def update_binding(self, state: State, button: int, action: str) -> None:
        """Update the binding for the given button."""
        self.profile.update_binding(state, button, action)
        if state in ("all", "review"):
            self.controls_page.update_inheritance()

    def reload(self):
        """Update the controls page."""
        if self.loaded:
            self.controls_page.update()
            self.options_page.update()


class Button(QPushButton):
    """A button connected to a function."""

    def __init__(self, parent: QWidget, name: str, func: Callable) -> None:
        super().__init__(parent)
        self.setText(name)
        self.setObjectName(name.lower().replace(" ", "_"))
        qconnect(self.clicked, func)


class Container(QWidget):
    """
    A container for other objects. Abstracts away the need to add
    widgets to a layout and apply the layout to a container widget.
    """

    def __init__(
        self,
        parent: QWidget,
        layout: Type[QLayout],
        widgets: Iterable[QWidget | QPushButton],
    ) -> None:
        super().__init__(parent)
        self._layout = layout(self)
        for widget in widgets:
            self._layout.addWidget(widget)
        self.setLayout(self._layout)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setFixedSize(self.sizeHint())

    def addWidget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)


class OptionsPage(QWidget):
    """A widget containing the main options."""

    def __init__(self, parent: ContankiConfig) -> None:
        super().__init__(parent)
        self._parent = parent
        self.profile = parent.profile
        self.reload = parent.reload
        layout = QGridLayout(parent)
        self.options: dict[str, Any] = dict()
        config = get_config()
        assert config is not None
        self.config = config
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        left_column = QVBoxLayout()
        centre_column = QVBoxLayout()
        right_column = QVBoxLayout()
        left_column.setSpacing(25)
        right_column.setSpacing(25)

        # Profile Bar
        self.profile_bar = self.ProfileBar(parent)
        layout.addWidget(self.profile_bar, 0, 0, 1, 3, alignment=alignment.AlignTop)

        # Axes & Flags
        self.axis_roles = self.AxisRoleSelector(parent)
        centre_column.addWidget(self.axis_roles, alignment=alignment.AlignTop)

        # Other Options
        form = QGroupBox("Options", self)
        form_layout = QFormLayout(self)
        for key, value in self.config.items():
            if isinstance(value, bool):
                widget: QCheckBox | QSpinBox = QCheckBox(self)
                widget.setChecked(self.config[key])  # type: ignore
            elif isinstance(value, int):
                widget = QSpinBox(self)
                widget.setMinimumWidth(45)
                widget.setValue(value)
            else:
                continue
            form_layout.addRow(key, widget)
            self.options[key] = widget
        form.setLayout(form_layout)
        left_column.addWidget(form, alignment=alignment.AlignTop)

        # Flags
        self.flags = self.FlagsSelector(self, self.config["Flags"])
        left_column.addWidget(self.flags, alignment=alignment.AlignTop)

        # Custom Actions
        self.custom_actions = self.CustomActions(parent, self.config["Custom Actions"])
        centre_column.addWidget(self.custom_actions, alignment=alignment.AlignTop)

        # Quick Select
        self.quick_select = self.QuickSelectSettings(parent)
        right_column.addWidget(self.quick_select, alignment=alignment.AlignTop)
        self.quick_select_actions: list[self.QuickSelectActions] = list()
        for state, actions in self.profile.quick_select["actions"].items():
            if actions:
                group = self.QuickSelectActions(parent, state)
                self.quick_select_actions.append(group)
                right_column.addWidget(group, alignment=alignment.AlignTop)

        layout.addLayout(left_column, 1, 0, alignment=alignment.AlignTop)
        layout.addLayout(centre_column, 1, 1, alignment=alignment.AlignTop)
        layout.addLayout(right_column, 1, 2, alignment=alignment.AlignTop)

        # Finish
        self.setLayout(layout)

    def get(self) -> dict:
        """Returns the currently selected options."""
        options = dict()
        for key, option in self.options.items():
            if isinstance(self.config[key], int):
                options[key] = option.value()
            elif isinstance(self.config[key], bool):
                options[key] = option.isChecked()
        options["Custom Actions"] = self.custom_actions.get()
        options["Flags"] = self.flags.get()
        return options

    def update(self):
        """Updates page to reflect user changess, such as the selected controller."""
        self.axis_roles.setup()
        self.quick_select.setup()
        for group in self.quick_select_actions:
            group.setup()

    class ProfileBar(QWidget):
        """A widget allowing the user to change, rename, or delete profiles."""

        def __init__(self, parent: ContankiConfig) -> None:
            super().__init__(parent)
            layout = QHBoxLayout()
            self.profile = parent.profile
            self.to_delete = parent.to_delete
            self.reload = parent.reload

            self.profile_combo = QComboBox(self)
            self.profile_combo.addItems(p_list := get_profile_list(defaults=False))
            self.profile_combo.setCurrentIndex(p_list.index(self.profile.name))
            qconnect(self.profile_combo.currentTextChanged, parent.change_profile)

            # Controller Selection Dropdown
            self.controller_combo = QComboBox(self)
            self.controller_combo.addItems(get_controller_list())
            self.controller_combo.setCurrentText(self.profile.controller.name)
            qconnect(self.controller_combo.currentTextChanged, self.update_controller)

            layout.addWidget(QLabel("Profile", self))
            layout.addWidget(self.profile_combo)
            layout.addWidget(Button(self, "Add Profile", self.add_profile))
            layout.addWidget(Button(self, "Rename Profile", self.rename_profile))
            layout.addWidget(Button(self, "Delete Profile", self.delete_profile))
            layout.addWidget(self.controller_combo)

            self.setLayout(layout)

        def add_profile(self) -> None:
            """Add a new profile."""
            old, okay1 = QInputDialog().getItem(
                self,
                "Create New Profile",
                "Select an existing profile to copy:",
                get_profile_list(),
                editable=False,
            )
            if not (okay1 and old):
                return
            name, okay2 = QInputDialog().getText(
                self, "Create New Profile", "Enter the new profile name:"
            )
            if not (name and okay2):
                return
            new_profile = create_profile(old, name)
            if new_profile is None:
                return
            self.profile_combo.addItem(new_profile.name)
            self.profile_combo.setCurrentText(new_profile.name)

        def delete_profile(self) -> None:
            """Delete the current profile."""
            if len(self.profile_combo) == 1:
                showInfo("You can't delete the last profile")
                return
            self.to_delete.append(self.profile.name)
            self.profile_combo.removeItem(self.profile_combo.currentIndex())

        def rename_profile(self) -> None:
            """Rename the current profile."""
            old_name = self.profile.name
            new_name, success = getText(
                "Please enter a new profile name", self, title="New Name"
            )
            if not success:
                return
            self.profile_combo.setItemText(self.profile_combo.currentIndex(), new_name)
            self.profile.name = new_name
            self.to_delete.append(old_name)

        def get_profile(self) -> str:
            """Returns the currently selected profile."""
            return self.profile_combo.currentText()

        def get_controller(self) -> str:
            """Returns the currently selected controller."""
            return self.controller_combo.currentText()

        def update_controller(self, controller: str) -> None:
            self.profile.controller = controller
            self.reload()

    class CustomActions(QWidget):
        """A widget allowing the user to modify custom actions."""

        def __init__(self, parent: ContankiConfig, actions: dict[str, str]) -> None:
            super().__init__(parent)
            layout = QGridLayout()
            self.profile = parent.profile
            self.config = parent.config
            self.reload = parent.reload

            # Table
            self.table = QTableWidget(len(actions), 2, parent)
            self.table.setColumnWidth(1, 70)
            self.table.setHorizontalHeaderLabels(["Custom Action", "Shortcut"])
            self.table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            self.table.verticalHeader().hide()
            self.key_edits = list()
            for row, (action, key_sequence) in enumerate(actions.items()):
                self.table.setItem(row, 0, QTableWidgetItem(action, 0))
                key_edit = QKeySequenceEdit(QKeySequence(key_sequence))
                self.key_edits.append(key_edit)
                self.table.setCellWidget(row, 1, key_edit)
            layout.addWidget(self.table, 1, 0, 1, 2)

            # Buttons
            add_button = Button(self, "Add", self.add_row)
            delete_button = Button(self, "Delete", self.remove_row)
            qconnect(self.table.cellChanged, self.update_config)
            layout.addWidget(add_button, 2, 0)
            layout.addWidget(delete_button, 2, 1)

            self.setLayout(layout)

        def add_row(self):
            """Add a row for a new custom action."""
            if self.table.selectedIndexes():
                current_row = self.table.currentRow() + 1
            else:
                current_row = self.table.rowCount()
            key_edit = QKeySequenceEdit(QKeySequence(""))
            self.key_edits.insert(current_row, key_edit)
            self.table.insertRow(current_row)
            self.table.setItem(current_row, 0, QTableWidgetItem("New Action", 0))
            self.table.setCellWidget(current_row, 1, key_edit)
            self.table.setCurrentCell(current_row, 0)
            self.update_config()

        def remove_row(self):
            """Remove the selected row, or the last one."""
            if not self.table.rowCount():
                return
            if self.table.selectedIndexes():
                self.key_edits.pop(self.table.currentRow())
                self.table.removeRow(self.table.currentRow())
            else:
                self.key_edits.pop()
                self.table.removeRow(self.table.rowCount() - 1)
            self.update_config()

        def get_row(self, row: int) -> tuple[str, str]:
            """Return the custom action name and key sequence at a given row."""
            if row > (num_rows := self.table.rowCount()):
                raise IndexError(f"Index {row} given but table has {num_rows} rows")
            return (
                self.table.item(row, 0).text(),
                self.key_edits[row].keySequence().toString(),
            )

        def get_actions(self) -> list[str]:
            """Return the custom action names as a list."""
            if not self.table.rowCount():
                return []
            return [
                self.table.item(row, 0).text() for row in range(self.table.rowCount())
            ]

        def get_keys(self) -> list[str]:
            """Return the custom action key sequences as a list."""
            if not self.table.rowCount():
                return []
            return [
                self.key_edits[row].keySequence().toString()
                for row in range(self.table.rowCount())
            ]

        def get(self) -> dict[str, str]:
            """Return the custom actions and key sequences as a dict."""
            if not self.table.rowCount():
                return {}
            return {k: v for k, v in zip(self.get_actions(), self.get_keys())}

        def update_config(self) -> None:
            """Update the profile with the custom actions."""
            self.config["Custom Actions"] = self.get()
            self.reload()

    class FlagsSelector(QGroupBox):
        """Lets the user select which flags are cycled when reviewing."""

        def __init__(self, parent: ContankiConfig, flags: list[int]):
            super().__init__("Flags", parent)
            self.config = parent.config
            layout = QFormLayout(self)
            self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.checkboxes: list[QCheckBox] = list()
            for flag in mw.flags.all():
                checkbox = QCheckBox(flag.label, self)
                checkbox.setIcon(theme_manager.icon_from_resources(flag.icon))
                if flag.index in flags:
                    checkbox.setChecked(True)
                qconnect(checkbox.clicked, self.update_flags)
                layout.addWidget(checkbox)
                self.checkboxes.append(checkbox)
            self.setLayout(layout)

        def update_flags(self):
            self.config["Flags"] = self.get()

        def get(self) -> list[int]:
            """Returns the list of checked flags."""
            return [i for i, cbox in enumerate(self.checkboxes) if cbox.isChecked()]

    class AxisRoleSelector(QGroupBox):
        """Allows the user to select the role for each axis."""

        items = (
            "Unassigned",
            "Buttons",
            "Cursor Horizontal",
            "Cursor Vertical",
            "Scroll Horizontal",
            "Scroll Vertical",
        )

        def __init__(self, parent: ContankiConfig) -> None:
            super().__init__("Axis Roles", parent)
            self.profile = parent.profile
            self.dropdowns: list[QComboBox] = list()
            self.reload = parent.reload
            self.setAlignment(alignment.AlignTop)
            self.setup()

        def update_binding(self, axis: int, role: str) -> None:
            """Update the binding for the given axis."""
            self.profile.axes_bindings[axis] = role
            self.reload()

        def setup(self) -> None:
            """Refresh for the current controller."""
            layout = QFormLayout(self)
            layout.setFormAlignment(alignment.AlignVCenter)
            layout.setFieldGrowthPolicy(
                QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
            )
            layout.setLabelAlignment(alignment.AlignRight | alignment.AlignVCenter)
            self.dropdowns.clear()
            for axis, name in self.profile.controller.axes.items():
                dropdown = QComboBox()
                dropdown.setSizePolicy(
                    QSizePolicy.Policy.MinimumExpanding,
                    QSizePolicy.Policy.MinimumExpanding,
                )
                dropdown.addItems(self.items)
                dropdown.setCurrentText(self.profile.axes_bindings[axis])
                qconnect(
                    dropdown.currentTextChanged,
                    partial(self.update_binding, axis),
                )
                label = QLabel()
                pixmap = get_button_icon(self.profile.controller, name)
                label.setPixmap(
                    pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio)
                )
                layout.addRow(label, dropdown)
                self.dropdowns.append(dropdown)
            _temp = QWidget()
            _temp.setLayout(self.layout())
            layout.setSizeConstraint(QFormLayout.SizeConstraint.SetFixedSize)
            self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            self.setLayout(layout)

        def __getitem__(self, item: int) -> str:
            return self.dropdowns[item].currentText()

    class QuickSelectSettings(QGroupBox):
        """Settings for the Quick Select radial menu."""

        def __init__(self, parent: ContankiConfig):
            super().__init__("Quick Select", parent)
            self.profile = parent.profile
            self.config = parent.config
            self._parent = parent
            self.setup()

        def setup(self) -> None:
            """Setup the Quick Select settings."""
            layout = QFormLayout(self._parent)
            for option, value in self.profile.quick_select.items():
                if option == "actions":
                    continue
                checkbox = QCheckBox(self._parent)
                if (
                    option == "Select with Stick"
                    and not self.profile.controller.has_stick
                ):
                    checkbox.setEnabled(False)
                else:
                    checkbox.setChecked(value)
                qconnect(checkbox.stateChanged, partial(self.update_option, option))
                layout.addRow(option, checkbox)
            self.setLayout(layout)

        def update_option(self, option: str, value: bool) -> None:
            """Update the given option."""
            self.profile.quick_select[option] = value

    class QuickSelectActions(QGroupBox):
        """Contains checkboxes to add actions to quick select for a state."""

        def __init__(self, parent: ContankiConfig, state: State) -> None:
            super().__init__("Quick Select Actions: " + states[state], parent)
            self.state = state
            self.profile = parent.profile
            self._parent = parent
            self.config = parent.config
            self.setup()

        def setup(self) -> None:
            """Adds all the checkboxes to the groupbox."""
            actions = []
            for action in QUICK_SELECT_ACTIONS[self.state] + list(
                self.config["Custom Actions"].keys()
            ):
                checkbox = QCheckBox(action, self._parent)
                checkbox.setChecked(
                    action in self.profile.quick_select["actions"][self.state]
                )
                qconnect(checkbox.stateChanged, partial(self.on_change, action))
                actions.append(checkbox)

            if actions:
                self.show()
            else:
                self.hide()

            layout = QGridLayout(self)
            for i, action_check in enumerate(actions):
                layout.addWidget(action_check, i // 2, i % 2)
            widget = QWidget()
            widget.setLayout(self.layout())
            self.setLayout(layout)

        def on_change(self, action: str, checked: bool) -> None:
            """Returns whether the checkbox is checked."""
            actions = self.profile.quick_select["actions"][self.state]
            if checked and action not in actions:
                actions.append(action)
            elif not checked and action in actions:
                actions.remove(action)


class ControlsPage(QTabWidget):
    """A widget allowing the user to modify the bindings."""

    style_sheet = "QTabWidget::pane { border: 0px; }"

    def __init__(self, parent: ContankiConfig) -> None:
        super().__init__(parent)
        self.setStyleSheet(self.style_sheet)
        self.profile = parent.profile
        self._update_binding = parent.update_binding
        self.custom_actions = parent.get_custom_actions()
        self.setObjectName("controls_page")
        self.setTabPosition(QTabWidget.TabPosition.South)
        self.tabs: dict[str, self.ControlsTab] = dict()
        self.combos: dict[State, dict[int, QComboBox]] = dict()
        self.update()

    def update_inheritance(self):
        """Updates action selection dropdowns to reflect inherited values."""
        combos_iter = [
            (state, index, combo)
            for state, state_combos in self.combos.items()
            if state != "all"
            for index, combo in state_combos.items()
            if index in state_combos
        ]

        all_bindings = {
            i: action
            for (state, i), action in self.profile.bindings.items()
            if state == "all"
        }

        review_bindings = {
            i: action
            for (state, i), action in self.profile.bindings.items()
            if state == "review"
        }

        for state, i, combo in combos_iter:
            inherited = ""
            if action := all_bindings[i]:
                inherited = action + " (inherited)"
            if state in ("question", "answer") and (action := review_bindings[i]):
                inherited = action + " (inherited)"
            combo.setItemText(0, inherited)

    def update(self):
        """Updates the controls to reflect the chosen options."""
        for _ in self.tabs:
            self.removeTab(0)
        self.tabs.clear()
        self.combos.clear()
        for state, state_name in states.items():
            self.tabs[state] = state_tab = self.ControlsTab(self, state)
            state_tab.setObjectName("state_tab")
            self.combos[state] = state_tab.combos
            self.addTab(state_tab, state_name)
        self.update_inheritance()

    def update_binding(self, state: State, button: int, action: str) -> None:
        """Updates the binding for the given state, mod, and index."""
        if "inherit" not in action:
            self._update_binding(state, button, action)

    class ControlsTab(QWidget):
        """Shows control binding options for a singel state."""

        def __init__(self, parent: ControlsPage, state: State) -> None:
            super().__init__()
            self.columns = [
                QFormLayout(),
                QFormLayout(),
                QFormLayout(),
            ]
            col = 0
            axes_bindings = parent.profile.axes_bindings
            self.combos: dict[int, QComboBox] = dict()
            for index, button in parent.profile.controller.buttons.items():
                if index >= 100:
                    axis = (index - 100) // 2
                    if axis > len(axes_bindings) or axes_bindings[axis] != "Buttons":
                        continue
                combo = QComboBox()
                combo.addItems(STATE_ACTIONS[state] + parent.custom_actions)
                combo.setCurrentText(parent.profile.bindings[(state, index)])
                combo.setMaximumWidth(170)
                combo.setSizePolicy(
                    QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding
                )
                qconnect(
                    combo.currentTextChanged,
                    partial(parent.update_binding, state, index),
                )
                icon = ButtonIcon(None, button, parent.profile.controller, index)
                icon.setFixedSize(60, 60)
                self.columns[col].addRow(icon, combo)
                self.combos[index] = combo
                col = (col + 1) % 3
            layout = QHBoxLayout()
            for column in self.columns:
                layout.addLayout(column)
            self.setLayout(layout)
