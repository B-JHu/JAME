from enum import Enum

class NodeType(Enum):
    PLACEHOLDER = -1
    DOCUMENT = 0

    # blocks
    BLOCK_QUOTE = 1
    CODE_BLOCK = 2
    PARAGRAPH = 3
    HEADING = 4
    THEMATIC_BREAK = 5
    HTML_BLOCK = 6
    CUSTOM_BLOCK = 7

    LIST = 8
    LIST_ITEM = 9

    # inlines
    TEXT = 10
    SOFTBREAK = 11
    LINEBREAK = 12
    CODE = 13
    EMPHASIS = 14
    STRONG = 15
    LINK = 16
    IMAGE = 17
    HTML_INLINE = 18
    CUSTOM_INLINE = 19

class ListType(Enum):
    ORDERED = 1
    UNORDERED = 2

class CodeBlockType(Enum):
    INDENTED = 1
    FENCED = 2

class HTMLInlineType(Enum):
    OPEN_TAG = 0
    CLOSING_TAG = 1
    HTML_COMMENT = 2
    PROCESSING_INSTRUCTION = 3
    DECLARATION = 4
    CDATA_SECTION = 5

class Node():
    def __init__(self, parent, node_type, raw_content = ""):
        self.node_type: int = node_type

        self.parent: Node = parent
        self.children : list[Node] = []

        self.raw_content: str = ""
        self.content: str = ""

        self.open: bool = True

        if parent:
            parent.children.append(self)

        self.addLine(raw_content)

    def getLastChild(self): # needed for Setext headings
        if self.children:
            return self.children[-1]
        return Node(None, NodeType.PLACEHOLDER)

    def getLastOpenChild(self):
        if self.children:
            for child in reversed(self.children):
                if child.open:
                    return child
            return None
        return None

    def getDeepestOpenChild(self):
        last_open_child = self.getLastOpenChild()

        if last_open_child:
            last_open_child = last_open_child.getDeepestOpenChild()
        else:
            return self
        return last_open_child

    def addLine(self, line_to_add): # adds a line to the nodes "raw_content" *as well as all of its parents "raw_content"* (needed to determine list tightness)
        if not line_to_add:
            return

        self.raw_content += line_to_add

        if self.node_type not in [NodeType.BLOCK_QUOTE, NodeType.CODE_BLOCK, NodeType.PARAGRAPH, NodeType.HEADING, NodeType.THEMATIC_BREAK, NodeType.HTML_BLOCK, NodeType.CUSTOM_BLOCK, NodeType.LIST, NodeType.LIST_ITEM]: # prevent addition to parents' raw content if we are parsing inlines
            return

        if self.parent:
            self.parent.addLine(line_to_add)

        # NOTE: For whatever reason, every time a line gets added to a list, it gets added twice; it doesn't affect any parsing work, so I will fix it at a later stage

class CodeBlockNode(Node):
    def __init__(self, parent, type, language = None, delimiter_char = "", delimiter_count = 0, indentation_width = 0, raw_content = ""):
        super().__init__(parent, NodeType.CODE_BLOCK)

        self.type = type # fenced or indented
        self.language = language

        self.delimiter_char = delimiter_char
        self.delimiter_count = delimiter_count
        self.indentation_width = indentation_width
        
        self.raw_content = raw_content

class HeadingNode(Node):
    def __init__(self, parent, heading_level, raw_content):
        super().__init__(parent, NodeType.HEADING, raw_content)

        self.heading_level = heading_level

class HTMLBlockNode(Node):
    def __init__(self, parent, block_type, raw_content = "", tag_name = "", attributes = {}):
        super().__init__(parent, NodeType.HTML_BLOCK, raw_content)

        self.tag_name : str = tag_name
        # value between 1 and 7 (inclusive); indicating the "kind of HTML block" as described in sec. 4.6
        self.block_type: int = block_type

        # "attributes" is a dictionary in the form of:
        # {
        #   "htmlAttribute1": value1,
        #   "htmlAttribute2": value2,
        #   ...
        # }
        self.attributes: dict = attributes

class ListNode(Node):
    def __init__(self, parent, list_type, delimiter, starting_number = None):
        super().__init__(parent, NodeType.LIST)

        self.list_type: int = list_type # one of the constants of the "ListType" enum
        self.delimiter: str = delimiter
        self.starting_number: int = starting_number
        self.is_tight: bool = True

class ListItemNode(Node):
    def __init__(self, parent, raw_content, continuation_indent):
        super().__init__(parent, NodeType.LIST_ITEM, raw_content)

        self.continuation_indent = continuation_indent # characters of indentation needed for the next line to be part of the last list item (see sec. 5.2)

class LinkOrImageNode(Node):
    def __init__(self, parent, node_type, link_destination, text, title):
        super().__init__(parent, node_type, text)

        self.link_destination = link_destination
        self.title = title

class HTMLInlineNode(Node):
    def __init__(self, parent, type, tag_name, raw_content = "", attributes = {}):
        super().__init__(parent, NodeType.HTML_INLINE, raw_content)

        self.type: int = type # values of the "HTMLInlineType" enum
        self.tag_name: str = tag_name
        self.attributes: dict = attributes # same format as in "HTMLBlockNode"