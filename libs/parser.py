import re
from .node import *
from .regexps import *
from .blocks import *
from .inlines import *
from .link_reference_definition import LinkReferenceDefinition

# This implementation follows the guidelines set out in the [Appendix of the CommonMark 0.30 spec](https://spec.commonmark.org/0.30/#appendix-a-parsing-strategy). Credit goes to the respective authors.

def parseBlocks(document: Node, line: str, link_reference_defs: list[LinkReferenceDefinition]):
    deepest_open_child = document.getDeepestOpenChild()

    # paragraph continuation text/"lazy continuation" (sec. 5.1)
    if deepest_open_child.node_type == NodeType.PARAGRAPH and canRemainOpen(deepest_open_child, line):
        line_text = removePossibleMarkers(line)

        deepest_open_child.addLine(line_text)
        pass
    elif not deepest_open_child.node_type == NodeType.DOCUMENT: # no lazy continuation, but still an open block
        if canRemainOpen(deepest_open_child, line):
            deepest_open_child.addLine(line)

            if deepest_open_child.node_type == NodeType.LIST_ITEM:             
                openBlock(deepest_open_child, line[deepest_open_child.continuation_indent:], deepest_open_child)
        else: # block cannot remain open; hence close it and open a new fitting block
            while not canRemainOpen(deepest_open_child, line): # back up to the deepest block that *can* remain open
                if deepest_open_child.node_type == NodeType.PARAGRAPH: # if we are about to close a paragraph, parse all link reference defs for later use
                    parseLinkReferenceDefs(deepest_open_child, link_reference_defs)

                deepest_open_child.open = False
                deepest_open_child = document.getDeepestOpenChild()

            if deepest_open_child.node_type == NodeType.LIST_ITEM: # needed to make sub-lists possible
                openBlock(deepest_open_child, line[deepest_open_child.continuation_indent:], deepest_open_child)
            elif document.getLastChild().node_type == NodeType.CODE_BLOCK: # if we just closed a code block, we do not want the closing sequence of backticks to be interpreted as the beginning of a new code block; hence skip it
                pass
            else:
                openBlock(document, line, deepest_open_child)
    else: # no lazy continuation and no open block: open a new one...
        deepest_open_child = document.getDeepestOpenChild()
        openBlock(document, line, deepest_open_child)

def recursiveInlineParsing(node_to_parse_inlines: Node, link_reference_defs: list):
    if node_to_parse_inlines.node_type == NodeType.PARAGRAPH or node_to_parse_inlines.node_type == NodeType.HEADING:
        node_to_parse_inlines.raw_content = node_to_parse_inlines.raw_content.rstrip()
        parseInlines(node_to_parse_inlines, node_to_parse_inlines.raw_content.rstrip(), link_reference_defs)
    elif node_to_parse_inlines.children:
        for child in node_to_parse_inlines.children:
            recursiveInlineParsing(child, link_reference_defs)

class Parser:
    def __init__(self):
        self.document = None
        self.link_reference_defs: list[LinkReferenceDefinition] = None

    def parse(self, markdownInput: str):
        self.document = Node(None, NodeType.DOCUMENT)
        self.link_reference_defs: list[LinkReferenceDefinition] = []

        markdownInput = re.sub(r'\\uOOOO', r'\\uFFFD', markdownInput) # as per sec. 2.3
        markdownInput = markdownInput.rstrip() # ignore new-lines & spaces at the end of the document
        lines = markdownInput.splitlines(True)

        for line in lines:
            parseBlocks(self.document, line, self.link_reference_defs)

        if self.document and self.document.getLastChild() and self.document.getLastChild().node_type == NodeType.PARAGRAPH:
            parseLinkReferenceDefs(self.document.getLastChild(), self.link_reference_defs) # at the end of input, it is possible to have an open paragraph node that has not been checked for link reference definitions

        for child in self.document.children:
            recursiveInlineParsing(child, self.link_reference_defs)

        return self.document