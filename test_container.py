#!/bin/python3

# This file provides an interface to test the parser against the [CommonMark spec](code.commonmark.org)
import sys
from libs.parser import Parser
from libs.htmlrenderer import HTMLRenderer

if __name__ == "__main__":
    parser = Parser()
    html_renderer = HTMLRenderer()

    ast = parser.parse("".join(sys.stdin.readlines()))
    html_string = html_renderer.render(ast)

    print(html_string)