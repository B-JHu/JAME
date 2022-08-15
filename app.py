from functools import partial
import sys
import os
import re
from PyQt5 import QtWidgets, QtGui

from libs import parser, htmlrenderer, jsonrenderer
from layout import Ui_mainWindow

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
            "GitHub": os.getcwd() + "/stylesheets/github-markdown.css",
            "Foghorn": os.getcwd() + "/stylesheets/foghorn.css"
        }

        self.textEdit.textChanged.connect(self.handleInputChange)

        self.actionSave.triggered.connect(self.menubar_save_clicked)
        self.actionSave_as.triggered.connect(self.menubar_save_as_clicked)
        self.actionNew.triggered.connect(self.menubar_new_clicked)
        self.actionOpen.triggered.connect(self.menubar_open_clicked)

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

        # correct the relative sizes of the elements in the splitter
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        

    def handleInputChange(self):
        self.text = self.textEdit.toPlainText()

        self.ast = self.parser.parse(self.text)
        html_string = self.htmlRenderer.render(self.ast)

        self.webEngineView.setHtml(html_string)
        self.updateLineNumbers()
        self.setWindowTitle(f"JAME: just another Markdown editor — {self.current_open_file}*")

    def updateLineNumbers(self):
        lines = len(self.text.splitlines())
        words = len(self.text.split())
        characters = len(self.text)

        self.statusbar.showMessage(f"{words} words (with {characters} characters) spanning {lines} lines.")

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
                text_cursor.insertText("****")
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left, n=2)
                self.textEdit.setTextCursor(text_cursor)
            case "Italic":
                text_cursor.insertText("**")
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.Left, n=1)
                self.textEdit.setTextCursor(text_cursor)
            case "Bullet list":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("- ")
            case "Ordered list":
                text_cursor.movePosition(QtGui.QTextCursor.MoveOperation.StartOfLine)
                text_cursor.insertText("1.")
            case "Code block":
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
            save_dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question, "Save or discard changes", "Do you want to save the current document before opening a new one?", QtWidgets.QMessageBox.StandardButton.Save | QtWidgets.QMessageBox.StandardButton.Discard | QtWidgets.QMessageBox.StandardButton.Cancel)
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

    window = MainWindow()
    window.show()
    app.exec()