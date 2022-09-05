from PyQt5 import QtGui, QtWidgets
from .node import *

def setFormat(text_edit: QtWidgets.QTextEdit, beginning_index: int, length: int, format: QtGui.QTextCharFormat):
    text_cursor = text_edit.textCursor()
    original_position = text_cursor.position()

    text_cursor.setPosition(beginning_index)
    text_cursor.setPosition(beginning_index + length, QtGui.QTextCursor.MoveMode.KeepAnchor)

    text_edit.setTextCursor(text_cursor)
    text_cursor.setCharFormat(format)

    text_cursor.setPosition(original_position, QtGui.QTextCursor.MoveMode.MoveAnchor)
    text_cursor.setCharFormat(QtGui.QTextCharFormat())
    text_edit.setTextCursor(text_cursor)  

# No, I cannot use QSyntaxHighlighter, as the Markdown syntax defined in the CommonMark spec cannot be entirely expressed through regular expressions alone
def highlightSyntax(text_edit: QtWidgets.QTextEdit, text: str, ast: Node, p_current_index: int):
    current_index = p_current_index

    while current_index and (current_index + 1) < len(text) and text[current_index] == "\n": # There could be some blank lines that are not represented within the abstract syntax tree; skip over them
        current_index += 1

    match ast.node_type:
        case NodeType.DOCUMENT:
            setFormat(text_edit, 0, len(text), QtGui.QTextCharFormat()) # clear all previous formatting/highlighting

            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child , current_index)
            return current_index

        case NodeType.PARAGRAPH:
            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            return current_index

        case NodeType.BLOCK_QUOTE:
            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(QtGui.QFont.Bold)
            setFormat(text_edit, current_index, 1, fmt)
            
            current_index += 1 # advance to after the '>'
            if current_index < len(text) and text[current_index] == " ": # If there is a space after the block quote marker, skip over it as well
                current_index += 1

            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            return current_index

        case NodeType.CODE_BLOCK:
            if ast.type == CodeBlockType.INDENTED:
                current_index += 4 # skip the four spaces of indentation
                beginning_index = current_index
                current_index += len(ast.raw_content)
                ending_index = current_index

                fmt = QtGui.QTextCharFormat()
                font = QtGui.QFont("monospace")
                font.setStyleHint(QtGui.QFont.Monospace)
                fmt.setFont(font, QtGui.QTextCharFormat.FontPropertiesInheritanceBehavior.FontPropertiesSpecifiedOnly)
                setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            else:
                beginning_index = current_index
                while (current_index + 1) < len(text) and not text[current_index] == "\n": # Advance to after the code fence
                    current_index += 1
                if (current_index + 1) < len(text):
                    current_index += 1

                current_index += len(ast.raw_content)
                while (current_index + 1) < len(text) and not text[current_index] == "\n": # Advance to after the ending code fence
                    current_index += 1
                if (current_index + 1) < len(text):
                    current_index += 1
                
                ending_index = current_index

                fmt = QtGui.QTextCharFormat()
                font = QtGui.QFont("monospace")
                font.setStyleHint(QtGui.QFont.Monospace)
                fmt.setFont(font, QtGui.QTextCharFormat.FontPropertiesInheritanceBehavior.FontPropertiesSpecifiedOnly)
                setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            return current_index

        case NodeType.PARAGRAPH:
            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            return current_index

        case NodeType.HEADING:
            beginning_index = current_index
            if text[current_index] == "#": # ATX heading
                current_index += ast.heading_level + 1

                for child in ast.children:
                    current_index = highlightSyntax(text_edit, text, child, current_index)

                if current_index + 1 < len(text):
                    current_index += 1 # Do not forget about the '\n' at the end of the heading line
                ending_index = current_index

                fmt = QtGui.QTextCharFormat()
                fmt.setFontWeight(QtGui.QFont.Bold)
                setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            else: # Setext heading
                for child in ast.children:
                    current_index = highlightSyntax(text_edit, text, child, current_index)

                if current_index + 1 < len(text):
                    current_index += 1 # Do not forget about the '\n' at the end of the heading line

                while (current_index + 1) < len(text) and not text[current_index] == "\n": # Advance to after the heading underline
                    current_index += 1
                if (current_index + 1) < len(text):
                    current_index += 1

                ending_index = current_index

                fmt = QtGui.QTextCharFormat()
                fmt.setFontWeight(QtGui.QFont.Bold)
                setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            return current_index

        case NodeType.THEMATIC_BREAK:
            while (current_index + 1) < len(text) and not text[current_index] == "\n":
                current_index += 1
            if (current_index + 1) < len(text):
                current_index += 1

            return current_index

        case NodeType.HTML_BLOCK:
            current_index += len(ast.raw_content)

            return current_index


        case NodeType.LIST:
            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            return current_index

        case NodeType.LIST_ITEM:
            beginning_index = current_index
            current_index += ast.continuation_indent
            ending_index = current_index

            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(QtGui.QFont.Bold)
            setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            return current_index


        case NodeType.TEXT:
            current_index += len(ast.content)

            return current_index

        case NodeType.SOFTBREAK:
            current_index += 1

            return current_index

        case NodeType.LINEBREAK:
            while (current_index + 1) < len(text) and not text[current_index] == "\n":
                current_index += 1
            if (current_index + 1) < len(text):
                current_index += 1

            return current_index

        case NodeType.INLINE_CODE:
            beginning_index = current_index
            current_index += 1
            current_index += len(ast.raw_content)
            current_index += 1
            ending_index = current_index

            fmt = QtGui.QTextCharFormat()
            font = QtGui.QFont("monospace")
            font.setStyleHint(QtGui.QFont.Monospace)
            fmt.setFont(font, QtGui.QTextCharFormat.FontPropertiesInheritanceBehavior.FontPropertiesSpecifiedOnly)
            setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            return current_index

        case NodeType.EMPHASIS:
            beginning_index = current_index
            current_index += 1

            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            current_index += 1
            ending_index = current_index

            fmt = QtGui.QTextCharFormat()
            fmt.setFontItalic(True)

            setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            return current_index

        case NodeType.STRONG:
            beginning_index = current_index
            current_index += 2

            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)

            current_index += 2
            ending_index = current_index

            fmt = QtGui.QTextCharFormat()
            fmt.setFontWeight(QtGui.QFont.Bold)
            setFormat(text_edit, beginning_index, ending_index - beginning_index, fmt)

            return current_index

        case NodeType.LINK:
            current_index += 1
            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)
            current_index += 1

            return current_index

        case NodeType.IMAGE:
            current_index += 2
            for child in ast.children:
                current_index = highlightSyntax(text_edit, text, child, current_index)
            current_index += 1

            return current_index

        case NodeType.HTML_INLINE:
            current_index += len(ast.raw_content)

            return current_index