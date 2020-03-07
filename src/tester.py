# coding: utf-8
# Copyright 2017

"""Implementing the application."""

from datetime import datetime
from json import JSONDecodeError, load
from os import path
from sys import stderr
from typing import Dict, List, Tuple, Union

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from widgetskv import WKV_PATH_CHOOSER, WKV_SEPARATOR_LINE


class Tester(BoxLayout):

    """Class of the testing window."""

    name: str
    timer: int
    time_temp: int
    directory: str
    answers: int = 0
    questions: int = 0
    test_temporary: List[List[str]]

    RED: str = "[color=#ff0000]{0}[/color]"
    GREEN: str = "[color=#00ff00]{0}[/color]"
    THEME_STYLE: Tuple[float, float, float, int] = (0.2, 0.2, 0.2, 1)
    FILE_NAME: str = ".testing-settings.json"
    TITLE_STR: str = "Testing"
    SECONDS_LEFT_STR: str = "Seconds left: {0}"
    QUESTIONS_LEFT_STR: str = "Questions left: {0}"
    CORRECT_ANSWERS_STR: str = "Correct answers: {0}"
    TOTAL_QUESTIONS_STR: str = "Total questions: {0}"
    FILE_IS_DAMAGED_STR: str = "File is damaged!"

    def launch_test(self):
        """Implement launch test."""
        settings: Dict[str, str] = self.read_settings()
        self.timer = int(settings["time"])
        self.directory = settings["path"]
        Factory.Launch().open()

    def start(self):
        """Forming the testing window and running the test."""
        len_test_temporary: int = len(self.test_temporary)
        self.time_temp = len_test_temporary * self.timer

        self.ids.all_issues.text = \
            self.TOTAL_QUESTIONS_STR.format(len_test_temporary)
        self.ids.issues.text = \
            self.QUESTIONS_LEFT_STR.format(len_test_temporary)
        self.ids.time_status.text = \
            self.SECONDS_LEFT_STR.format(self.time_temp)

        self.question_show(0)
        Clock.schedule_interval(self.move_timer, 1)

    def previous_question(self):
        """Implement previous question button."""
        if self.questions > 0 and self.test_temporary[0]:
            self.questions -= 1
            self.question_show(self.questions)

    def next_question(self):
        """Implement next question button."""
        if self.questions < len(self.test_temporary) - 1:
            self.questions += 1
            self.question_show(self.questions)

    def question_show(self, question: int):
        """Display a frame with a question of a given number."""
        self.ids.radio0.active = True
        for i in range(1, 10):
            self.ids[f"radio{i}"].disabled = True
            self.ids[f"radio{i}"].active = False
            self.ids[f"answer{i}"].text = ''

        self.ids.reply.text = self.test_temporary[question][0]
        if len(self.test_temporary[question]) > 2:
            for i in range(1, len(self.test_temporary[question]) - 1):
                self.ids[f"answer{i}"].text = self.test_temporary[question][i]
                self.ids[f"radio{i}"].disabled = False

    def move_timer(self, _: float) -> bool:
        """Return a timer interrupt condition."""
        self.time_temp -= 1

        if self.time_temp > self.timer:
            self.ids.time_status.text = \
                self.GREEN.format(self.SECONDS_LEFT_STR.format(self.time_temp))
        elif self.time_temp > 0:
            self.ids.time_status.text = \
                self.RED.format(self.SECONDS_LEFT_STR.format(self.time_temp))
        else:
            self.ids.time_status.text = \
                self.SECONDS_LEFT_STR.format(self.time_temp)
            self.test_temporary = [[]]
            self.questions = 0

        return bool(self.time_temp)

    def accept_answer(self):
        """Process selected answer."""
        for i in range(0, 10):
            if self.ids[f"radio{i}"].active:
                active_button: str = str(i)
                break

        if self.test_temporary[0]:
            if active_button == self.test_temporary[self.questions][-1]:
                self.answers += 1
            self.ids.issues.text = \
                self.QUESTIONS_LEFT_STR.format(len(self.test_temporary) - 1)

        del self.test_temporary[self.questions]

        if self.test_temporary:
            if self.questions > len(self.test_temporary) - 1:
                self.questions -= 1
            self.question_show(self.questions)
        else:
            self.save_and_show_result()

    def save_and_show_result(self):
        """Save and display the result."""
        time_temp: int = self.time_temp
        issues: int = int(self.ids.issues.text.split()[-1])
        all_issues: int = int(self.ids.all_issues.text.split()[-1])

        self.time_temp = 1
        self.remove_widget(self.ids.top_grid)
        self.remove_widget(self.ids.bottom_box)

        date_time: List[str] = \
            datetime.now().isoformat(timespec="seconds").split('T')
        results: str = "\n{0} of {1}\n{2} of {3}\n{4} of {5}".format(
            self.CORRECT_ANSWERS_STR.format(self.answers), all_issues - issues,
            self.ids.issues.text, all_issues,
            self.SECONDS_LEFT_STR.format(time_temp), all_issues * self.timer
        )

        path_results: str = path.join(self.directory, f"{date_time[0]}.txt")
        with open(path_results, 'a') as files:
            files.write(f"{self.name}\t{date_time[1]}{results}\n\n")
            files.flush()

        self.ids.reply.text = f"[size=30px]TEST COMPLETED![/size]\n"\
            f"[size=20px]{results}[/size]"

    def read_settings(self) -> Dict[str, str]:
        """Return settings from hidden file."""
        config_file: str = path.join(path.expanduser('~'), self.FILE_NAME)
        settings: Dict[str, str]

        try:
            with open(config_file, 'r') as files:
                settings = load(files)
            if not isinstance(settings, dict):
                raise OSError(self.FILE_IS_DAMAGED_STR)
        except (OSError, UnicodeDecodeError, JSONDecodeError) as error:
            stderr.write(f"{error}\n")
            settings = {}

        settings.setdefault("time", "50")
        settings.setdefault("path", path.expanduser('~'))
        return settings

    @staticmethod
    def open_test(path_test: str) -> Union[List[List[str]], list]:
        """Return a list of questions from a file."""
        try:
            with open(path_test, 'r') as files:
                temp_test: List[List[str]] = load(files)

            if isinstance(temp_test, list) and isinstance(temp_test[0], list) \
                    and isinstance(temp_test[0][0], str):
                return temp_test

        except (OSError, UnicodeDecodeError, JSONDecodeError) as error:
            stderr.write(f"{error}\n")

        return []

    def impl_path_chooser(self, path_file: str):
        """Test open and launch."""
        self.test_temporary = self.open_test(path_file)
        if self.test_temporary:
            self.launch_test()
        else:
            Factory.PathChooser().open()


if __name__ == "__main__":
    PROJECT_PATH: str = path.split(path.dirname(__file__))[0]
    Builder.load_file(path.join(PROJECT_PATH, "uix", "tester.kv"))
    Builder.load_file(path.join(PROJECT_PATH, "uix", "dialog.kv"))
    Builder.load_file(WKV_SEPARATOR_LINE)
    Builder.load_file(WKV_PATH_CHOOSER)

    Window.clearcolor = Tester.THEME_STYLE
    Tester.test_temporary = list()

    app: App = App()
    app.root = Tester()
    app.root.padding = 10
    app.title = app.root.TITLE_STR
    app.impl_path_chooser = app.root.impl_path_chooser
    Clock.schedule_once(Factory.PathChooser().open)
    app.run()
