# coding: utf-8
# Copyright 2017

"""Implementing the application."""

from glob import glob
from json import dump
from os import path
from sys import stderr
from typing import List

from kivy.app import App
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from widgetskv import WKV_ALL_FILES

from .tester import Tester


class Gui(App):

    """Class of the create test window and runing of the application."""

    tester: Tester = Tester()
    title: str = "Test constructor"
    version: str = "0.1.0"
    create_year: int = 2017
    license_link: str = "https://www.gnu.org/licenses/gpl-3.0"
    project_link: str = "https://github.com/Paduct/test_constructor"
    description: str = "Application for creating and passing tests."
    current_issue: int = 1
    number_replies: int = 0
    test_temporary: List[List[str]] = [[]]

    MAXIMUM_NUMBER_ANSWERS: int = 9
    MAXIMUM_NUMBER_QUESTIONS: int = 999
    MARK_STR: str = "• {0}"
    NOT_SAVED_STR: str = "Not saved!"
    SETTINGS_SAVED_STR: str = "Settings saved!"
    CURRENT_QUESTION_STR: str = "Current question: {0}"
    ANSWERS_TO_QUESTION_STR: str = "Answers to question: {0}"
    BUBLE: Bubble = Bubble(size=(150, 50), size_hint=(None, None),
                           arrow_pos="bottom_right", pos=(-100, -100))

    def build(self):
        """Accumulate of resources and the start of the main window."""
        project_path: str = path.split(path.dirname(__file__))[0]
        kv_files_path: str = path.join(project_path, "uix", "*.kv")
        kv_file_names: List[str] = glob(kv_files_path)
        kv_file_names.extend(WKV_ALL_FILES)

        for file_name in kv_file_names:
            Builder.load_file(file_name)

        Window.clearcolor = self.tester.THEME_STYLE
        self.BUBLE.add_widget(Label(text="Marked as correct"))
        self.icon = path.join(project_path, "data", "forum.png")
        self.root = Factory.RootWindow()

    def question_add(self):
        """Implement question add."""
        active_question: ToggleButton = next(
            (toggle for toggle in ToggleButton.get_widgets("select_question")
             if toggle.state == "down")
        )
        number_question: int = \
            self.root.ids.box_quest.children.index(active_question)
        amount_questions: int = len(self.root.ids.box_quest.children)

        if amount_questions < self.MAXIMUM_NUMBER_QUESTIONS:
            self.save_form()
            self.clear_form()
            self.test_temporary.insert(number_question + 1, [''])

            active_question.state = "normal"
            self.root.ids.box_quest.add_widget(Factory.GToggleButton(),
                                               number_question + 1)

            self.current_issue = number_question + 2
            self.root.ids.all_issues.text = \
                self.tester.TOTAL_QUESTIONS_STR.format(amount_questions + 1)
            self.root.ids.issues.text = \
                self.CURRENT_QUESTION_STR.format(self.current_issue)

    def question_del(self):
        """Implement question del."""
        active_question: ToggleButton = next(
            (toggle for toggle in ToggleButton.get_widgets("select_question")
             if toggle.state == "down")
        )
        number_question: int = \
            self.root.ids.box_quest.children.index(active_question)
        amount_questions: int = len(self.root.ids.box_quest.children)

        if number_question > 0:
            del self.test_temporary[number_question]

            self.root.ids.box_quest.remove_widget(active_question)
            active_question.state = "normal"
            self.root.ids.box_quest.children[number_question - 1].state = \
                "down"

            self.clear_form()
            self.fill_form()

            self.root.ids.all_issues.text = \
                self.tester.TOTAL_QUESTIONS_STR.format(amount_questions - 1)

    def answer_add(self):
        """Implement answer add."""
        if self.number_replies < self.MAXIMUM_NUMBER_ANSWERS:
            self.number_replies += 1

            self.root.ids[f"radio{self.number_replies}"].disabled = False
            self.root.ids[f"text{self.number_replies}"].disabled = False
            self.root.ids[f"text{self.number_replies}"].focused = True

            self.root.ids.reply.text = \
                self.ANSWERS_TO_QUESTION_STR.format(self.number_replies)
            self.root.ids.status.text = \
                self.tester.RED.format(self.NOT_SAVED_STR)

    def answer_del(self):
        """Implement answer del."""
        if self.number_replies > 0:
            self.root.ids[f"radio{self.number_replies}"].disabled = True
            if self.root.ids[f"radio{self.number_replies}"].active:
                self.root.ids[f"radio{self.number_replies}"].active = False
                self.root.ids.radio0.active = True

            self.root.ids[f"text{self.number_replies}"].disabled = True
            self.root.ids[f"text{self.number_replies}"].text = ''
            self.root.ids[f"text{self.number_replies - 1}"].focused = True

            self.root.ids.reply.text = \
                self.ANSWERS_TO_QUESTION_STR.format(self.number_replies - 1)
            self.root.ids.status.text = \
                self.tester.RED.format(self.NOT_SAVED_STR)

            self.number_replies -= 1

    def save_test(self, path_file: str):
        """Implement test saving."""
        self.save_form()
        try:
            with open(path_file, 'w') as files:
                dump(self.test_temporary, files, indent=1)
                files.flush()

            self.root.ids.status.text = self.tester.GREEN.format(
                self.NOT_SAVED_STR[4:].capitalize()
            )
        except OSError as error:
            stderr.write(f"{error}\n")

    def open_test(self, path_file: str):
        """Implement test opening."""
        temp_test: List[List[str]] = self.tester.open_test(path_file)
        len_temp_test: int = len(temp_test)

        if len_temp_test > 0:
            next((toggle for toggle
                  in ToggleButton.get_widgets("select_question")
                  if toggle.state == "down")).state = "normal"
            self.root.ids.box_quest.clear_widgets()

            for i in range(len_temp_test):
                self.root.ids.box_quest.add_widget(Factory.GToggleButton(
                    text=self.MARK_STR.format(temp_test[i][0]), state="normal"
                ), i)
            self.root.ids.box_quest.children[-1].state = "down"

            self.root.ids.all_issues.text = \
                self.tester.TOTAL_QUESTIONS_STR.format(len_temp_test)
            self.test_temporary = temp_test

            self.clear_form()
            self.fill_form()
        else:
            self.root.ids.status.text = \
                self.tester.RED.format(self.tester.FILE_IS_DAMAGED_STR)

    def launch_test(self, path_file: str):
        """Implement test launching."""
        temp_test: List[List[str]] = self.tester.open_test(path_file)
        if temp_test:
            Window.set_title(self.tester.TITLE_STR)
            self.root.clear_widgets()
            self.root.add_widget(Tester())
            self.root = self.root.children[0]
            self.root.test_temporary = temp_test
            self.root.launch_test()
        else:
            self.root.ids.status.text = \
                self.tester.RED.format(self.tester.FILE_IS_DAMAGED_STR)

    def save_settings(self, timer: str, directory: str):
        """Implement bar - settings saving."""
        path_settings: str = path.join(path.expanduser('~'),
                                       self.tester.FILE_NAME)
        with open(path_settings, 'w') as files:
            dump({"time": timer, "path": directory}, files)

        self.root.ids.status.text = \
            self.tester.GREEN.format(self.SETTINGS_SAVED_STR)

    def save_form(self):
        """Preservation of the form of the current issue."""
        number_question: int = self.current_issue - 1
        self.test_temporary[number_question].clear()

        for i in range(10):
            if not self.root.ids[f"text{i}"].disabled:
                self.test_temporary[number_question].append(
                    self.root.ids[f"text{i}"].text
                )

        for i in range(10):
            if self.root.ids[f"radio{i}"].active:
                self.test_temporary[number_question].append(str(i))

        self.root.ids.box_quest.children[number_question].text = \
            self.MARK_STR.format(self.test_temporary[number_question][0])

    def clear_form(self):
        """Clean the mold and return to the initial state."""
        self.number_replies = 0
        self.root.ids.radio0.active = True
        self.root.ids.text0.text = ''
        self.root.ids.text0.focused = True

        for i in range(1, 10):
            self.root.ids[f"radio{i}"].disabled = True
            self.root.ids[f"radio{i}"].active = False
            self.root.ids[f"text{i}"].disabled = True
            self.root.ids[f"text{i}"].text = ''

        self.root.ids.status.text = self.tester.RED.format(self.NOT_SAVED_STR)
        self.root.ids.reply.text = \
            self.ANSWERS_TO_QUESTION_STR.format(self.number_replies)

    def fill_form(self):
        """Fill out the form in accordance with the number of the question."""
        active_question: ToggleButton = next(
            (toggle for toggle in ToggleButton.get_widgets("select_question")
             if toggle.state == "down")
        )
        num_issues: int = \
            self.root.ids.box_quest.children.index(active_question)
        self.number_replies = len(self.test_temporary[num_issues]) - 2

        for i in range(self.number_replies + 1):
            self.root.ids[f"radio{i}"].disabled = False
            if i == int(self.test_temporary[num_issues]
                        [self.number_replies + 1]):
                self.root.ids.radio0.active = False
                self.root.ids[f"radio{i}"].active = True

            self.root.ids[f"text{i}"].disabled = False
            self.root.ids[f"text{i}"].text = self.test_temporary[num_issues][i]
            self.root.ids[f"text{i}"].focused = True

        self.current_issue = num_issues + 1
        self.root.ids.issues.text = \
            self.CURRENT_QUESTION_STR.format(self.current_issue)
        self.root.ids.reply.text = \
            self.ANSWERS_TO_QUESTION_STR.format(self.number_replies)

    def on_pause(self) -> bool:
        """Return the sign of switching to pause mode."""
        return True
