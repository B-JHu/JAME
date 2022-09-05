from functools import partial
import sys
import os
import re
from PyQt5 import QtWidgets, QtGui, QtCore

from libs import parser, htmlrenderer, jsonrenderer, syntaxhighlighter
from layout import Ui_mainWindow

__version__ = "0.1.1"

class MainWindow(QtWidgets.QMainWindow, Ui_mainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.text = self.textEdit.toPlainText()
        self.current_open_file = "untitled"

        self.parser = parser.Parser()
        self.htmlRenderer = htmlrenderer.HTMLRenderer({"indent": 4, "include_html_backbone": True, "css_styling": ""})
        self.ast = None

        self.STYLESHEET_PATHS = {
            "GitHub": os.path.join(os.getcwd(), "stylesheets", "github-markdown.css"),
            "Foghorn": os.path.join(os.getcwd(), "stylesheets", "foghorn.css")
        }

        self.textEdit.textChanged.connect(self.handleInputChange)

        self.actionSave.triggered.connect(self.menubar_save_clicked)
        self.actionSave_as.triggered.connect(self.menubar_save_as_clicked)
        self.actionNew.triggered.connect(self.menubar_new_clicked)
        self.actionOpen.triggered.connect(self.menubar_open_clicked)
        self.actionQuit.triggered.connect(self.menubar_quit_clicked)

        self.actionHTML_plain.triggered.connect(self.menubar_export_to_HTML_plain_clicked)
        self.actionHTML_styled.triggered.connect(self.menubar_export_to_HTML_styled_clicked)
        self.actionJSON.triggered.connect(self.menubar_export_to_JSON_clicked)

        self.actionNone_default.triggered.connect(partial(self.applyStylesheet, stylesheet_path=None))
        self.actionGitHub.triggered.connect(partial(self.applyStylesheet, stylesheet_path=self.STYLESHEET_PATHS["GitHub"]))
        self.actionFoghorn.triggered.connect(partial(self.applyStylesheet, stylesheet_path=self.STYLESHEET_PATHS["Foghorn"]))

        self.actionBold.triggered.connect(partial(self.insertMarkdown, what_to_insert="Bold"))
        self.actionItalic.triggered.connect(partial(self.insertMarkdown, what_to_insert="Italic"))
        self.actionBullet_list.triggered.connect(partial(self.insertMarkdown, what_to_insert="Bullet list"))
        self.actionOrdered_list.triggered.connect(partial(self.insertMarkdown, what_to_insert="Ordered list"))
        self.actionCode_block.triggered.connect(partial(self.insertMarkdown, what_to_insert="Code block"))
        self.actionBlock_quote.triggered.connect(partial(self.insertMarkdown, what_to_insert="Block quote"))
        self.actionHeading_Lvl_1.triggered.connect(partial(self.insertMarkdown, what_to_insert="Heading 1"))
        self.actionHeading_Lvl_2.triggered.connect(partial(self.insertMarkdown, what_to_insert="Heading 2"))
        self.actionHeading_Lvl_3.triggered.connect(partial(self.insertMarkdown, what_to_insert="Heading 3"))

        self.actionGitHub_open_repo.triggered.connect(self.menubar_GitHub_repo_clicked)
        self.actionMarkdown_Tutorial.triggered.connect(self.menubar_Markdown_tutorial_clicked)
        self.actionAbout_JAME.triggered.connect(self.menubar_about_clicked)

        # correct the relative sizes of the elements in the splitter
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)

        # set version number in the "status bar" on the bottom of the UI
        self.JAME_name_label.setText(f"JAME — Just another Markdown editor v{__version__}")
        # + make it monospace
        current_font = self.JAME_name_label.font()
        current_font.setStyleHint(QtGui.QFont.Monospace)
        self.JAME_name_label.setFont(current_font)

    def handleInputChange(self):
        self.text = self.textEdit.toPlainText()

        self.ast = self.parser.parse(self.text)
        self.textEdit.blockSignals(True)
        syntaxhighlighter.highlightSyntax(self.textEdit, self.text, self.ast, 0)
        self.textEdit.blockSignals(False)
        html_string = self.htmlRenderer.render(self.ast)

        self.webEngineView.setHtml(html_string)
        self.updateLineNumbers()
        self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}*")

    def updateLineNumbers(self):
        lines = len(self.text.splitlines())
        words = len(self.text.split())
        characters = len(self.text)

        self.document_status_label.setText(f"{words} words (with {characters} characters) spanning {lines} lines.")

    def applyStylesheet(self, stylesheet_path: str):
        if not stylesheet_path: # "None (default)" stylesheet has been chosen
            self.htmlRenderer.options["css_styling"] = ""
        else:
            with open(stylesheet_path, "r") as stylesheet:
                raw_css = stylesheet.read()
                self.htmlRenderer.options["css_styling"] = raw_css

        self.handleInputChange()

    def insertMarkdown(self, what_to_insert: str):
        text_cursor = self.textEdit.textCursor()
        self.textEdit.setTextCursor(text_cursor)

        match what_to_insert:
            case "Bold":
                if text_cursor.hasSelection():
                    selection_beginning_position = text_cursor.anchor()
                    selection_ending_position = text_cursor.position()

                    if selection_beginning_position > selection_ending_position: # If the anchor is to the right of the cursor's position, swap it so the code below works
                        tmp = selection_beginning_position
                        selection_beginning_position = selection_ending_position
                        selection_ending_position = tmp

                    text_cursor.setPosition(selection_beginning_position)
                    text_cursor.insertText("**")
                    text_cursor.setPosition(selection_ending_position + 2) # We need to account for the freshly inserted '**', hence '+ 2'
                    text_cursor.insertText("**")
                    self.textEdit.setTextCursor(text_cursor)
                else:
                    text_cursor.insertText("****")
                    text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left, n=2)
                    self.textEdit.setTextCursor(text_cursor)
            case "Italic":
                if text_cursor.hasSelection():
                    selection_beginning_position = text_cursor.anchor()
                    selection_ending_position = text_cursor.position()

                    if selection_beginning_position > selection_ending_position:
                        tmp = selection_beginning_position
                        selection_beginning_position = selection_ending_position
                        selection_ending_position = tmp

                    text_cursor.setPosition(selection_beginning_position)
                    text_cursor.insertText("*")
                    text_cursor.setPosition(selection_ending_position + 1)
                    text_cursor.insertText("*")
                    self.textEdit.setTextCursor(text_cursor)
                else:
                    text_cursor.insertText("**")
                    text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left, n=1)
                    self.textEdit.setTextCursor(text_cursor)
            case "Bullet list":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("- ")
            case "Ordered list":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("1. ")
            case "Code block":
                if text_cursor.hasSelection():
                    selection_beginning_position = text_cursor.anchor()
                    selection_ending_position = text_cursor.position()

                    if selection_beginning_position > selection_ending_position:
                        tmp = selection_beginning_position
                        selection_beginning_position = selection_ending_position
                        selection_ending_position = tmp

                    text_cursor.setPosition(selection_beginning_position)
                    text_cursor.insertText("```\n")
                    text_cursor.setPosition(selection_ending_position + 4)
                    text_cursor.insertText("\n```")
                    self.textEdit.setTextCursor(text_cursor)
                else:
                    text_cursor.insertText("```\n\n```")
                    text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.Up)
                    self.textEdit.setTextCursor(text_cursor)
            case "Block quote":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("> ")
            case "Heading 1":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("# ")
            case "Heading 2":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("## ")
            case "Heading 3":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("### ")

    # begin menu buttons
    def menubar_save_clicked(self): # if we do not have a file open, we need to create one to save it to
        if self.current_open_file == "untitled":
            self.menubar_save_as_clicked()
        else:
            with open(self.current_open_file, "w") as file:
                file.write(self.text)

            self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")

    def menubar_save_as_clicked(self):
        file_name_to_save_to, filter_chosen = QtWidgets.QFileDialog.getSaveFileName(self, "Save your work", os.getcwd() + "/untitled", "Markdown files (*.md)")
        if not file_name_to_save_to: # User has chosen the "Cancel" option
            return

        if not re.search(r'\.md$', file_name_to_save_to):
            file_name_to_save_to += ".md"

        with open(file_name_to_save_to, "w") as new_file:
            new_file.write(self.text)

        self.current_open_file = file_name_to_save_to
        self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")

    def menubar_new_clicked(self):
        if len(self.text) == 0: # nothing has been typed yet; hence trying to open a new file would be unnecessary
            pass
        else:
            save_dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, "Save or discard changes", "Do you want to save the current document before opening a new one?", QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel)
            chosen_option = save_dialog.exec()

            match chosen_option:
                case QtWidgets.QMessageBox.StandardButton.Save:
                    self.menubar_save_clicked()
                    self.current_open_file = "untitled"
                    self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")
                    self.textEdit.setText("")

                case QtWidgets.QMessageBox.StandardButton.Discard:
                    self.current_open_file = "untitled"
                    self.textEdit.setText("")

                case QtWidgets.QMessageBox.StandardButton.Cancel:
                    pass

    def menubar_open_clicked(self):
        if len(self.text) == 0: # nothing has been typed yet; hence we can just open the user requested file without needing to save any edits
            file_name_to_open, filter_chosen = QtWidgets.QFileDialog.getOpenFileName(self, "Open a Markdown file", os.getcwd(), "Markdown files (*.md);;Text files (*.txt)", "Markdown files (*.md)")

            with open(file_name_to_open, "r") as file_to_open:
                self.textEdit.setText(file_to_open.read())

            self.current_open_file = file_name_to_open
            self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")
        else:
            save_dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, "Save or discard changes", "Do you want to save the current document before opening another one?", QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel)
            chosen_option = save_dialog.exec()

            match chosen_option:
                case QtWidgets.QMessageBox.StandardButton.Save:
                    self.menubar_save_clicked()

                    file_name_to_open, filter_chosen = QtWidgets.QFileDialog.getOpenFileName(self, "Open a Markdown file", os.getcwd(), "Markdown files (*.md);;Text files (*.txt)", "Markdown files (*.md)")

                    with open(file_name_to_open, "r") as file_to_open:
                        self.textEdit.setText(file_to_open.read())

                    self.current_open_file = file_name_to_open
                    self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")

                case QtWidgets.QMessageBox.StandardButton.Discard:
                    self.menubar_save_clicked()

                    file_name_to_open, filter_chosen = QtWidgets.QFileDialog.getOpenFileName(self, "Open a Markdown file", os.getcwd(), "Markdown files (*.md);;Text files (*.txt)", "Markdown files (*.md)")

                    with open(file_name_to_open, "r") as file_to_open:
                        self.textEdit.setText(file_to_open.read())

                    self.current_open_file = file_name_to_open
                    self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}")

                case QtWidgets.QMessageBox.StandardButton.Cancel:
                    pass

    def menubar_quit_clicked(self):
        if len(self.text) == 0:
            sys.exit()
        else:
            save_dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, "Save or discard changes", "Do you want to save the current document before quitting?", QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel)
            chosen_option = save_dialog.exec()

            match chosen_option:
                case QtWidgets.QMessageBox.StandardButton.Save:
                    self.menubar_save_clicked()
                    sys.exit()

                case QtWidgets.QMessageBox.StandardButton.Discard:
                    sys.exit()

                case QtWidgets.QMessageBox.StandardButton.Cancel:
                    pass

    def menubar_GitHub_repo_clicked(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/B-JHu/JAME/"))

    def menubar_Markdown_tutorial_clicked(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://commonmark.org/help/tutorial/"))

    def menubar_about_clicked(self):
        about_string_with_version = f"<body style=\"align:center;text-align:center\"><b>JAME</b> - just another Markdown editor<br/>Version {__version__}<br/><br/>Published under the GPL v3 license</body>"
        QtWidgets.QMessageBox.about(self, f"About JAME", about_string_with_version)

    # exporters
    def menubar_export_to_HTML_plain_clicked(self):
        file_name_to_save_to, filter_chosen = QtWidgets.QFileDialog.getSaveFileName(self, "Export to a file", os.getcwd() + "/untitled", "HTML files (*.html *.htm)")
        if not re.search(r'\.html$', file_name_to_save_to):
            file_name_to_save_to += ".html"

        with open(file_name_to_save_to, "w") as new_file:
            new_file.write(self.htmlRenderer.renderWithoutStyling(self.ast))

    def menubar_export_to_HTML_styled_clicked(self):
        file_name_to_save_to, filter_chosen = QtWidgets.QFileDialog.getSaveFileName(self, "Export to a file", os.getcwd() + "/untitled", "HTML files (*.html *.htm)")
        if not re.search(r'\.html$', file_name_to_save_to):
            file_name_to_save_to += ".html"

        with open(file_name_to_save_to, "w") as new_file:
            new_file.write(self.htmlRenderer.render(self.ast))

    def menubar_export_to_JSON_clicked(self):
        file_name_to_save_to, filter_chosen = QtWidgets.QFileDialog.getSaveFileName(self, "Export to a file", os.getcwd() + "/untitled", "JSON files (*.json)")
        if not re.search(r'\.json$', file_name_to_save_to):
            file_name_to_save_to += ".json"

        with open(file_name_to_save_to, "w") as new_file:
            json_renderer = jsonrenderer.JSONRenderer({"jsonIndent": 4, "debug_infos": False})
            new_file.write(json_renderer.render(self.ast))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    q_stylesheet = QtCore.QFile("ui/resources_dark/stylesheet.qss")
    q_stylesheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    style_stream = QtCore.QTextStream(q_stylesheet)
    app.setStyleSheet(style_stream.readAll())

    app.setWindowIcon(QtGui.QIcon("ui/logo_dark_text.svg"))

    window = MainWindow()
    window.setWindowIcon(QtGui.QIcon("ui/logo_dark_text.svg"))

    def toggleLightMode():
        if window.actionLight_mode.isChecked():
            q_stylesheet = QtCore.QFile("ui/resources_light/stylesheet.qss")
            q_stylesheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
            style_stream = QtCore.QTextStream(q_stylesheet)
            app.setStyleSheet(style_stream.readAll())
        else:
            q_stylesheet = QtCore.QFile("ui/resources_dark/stylesheet.qss")
            q_stylesheet.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
            style_stream = QtCore.QTextStream(q_stylesheet)
            app.setStyleSheet(style_stream.readAll())

    window.actionLight_mode.toggled.connect(toggleLightMode)

    window.show()
    app.exec()