import json
from .node import *

DEFAULT_OPTIONS = {
    "jsonIndent": 3,
    "debug_infos": True
}

# The method of splitting the renderer into a "node walker", which then calls the appropriate rendering option for each block type stems from [the official JS CommonMark implementation](https://github.com/commonmark/commonmark.js/blob/master/lib/render/renderer.js)

def block_quote(block_quote_node: Node, debug: bool):
    if debug:
        return {
            "node_type": "block_quote",
            "open": block_quote_node.open,
            "raw_content": block_quote_node.raw_content,
            "children": []
        }
    return {
        "node_type": "block_quote",
        "children": []
    }

def code_block(code_block_node: CodeBlockNode, debug: bool):
    if debug:
        if code_block_node.type == CodeBlockType.INDENTED:
            return {
                "node_type": "code_block",
                "open": code_block_node.open,
                "type": "indented",
                "content": code_block_node.content,
                "raw_content": code_block_node.raw_content
            }
        return {
            "node_type": "code_block",
            "open": code_block_node.open,
            "type": "fenced",
            "language": code_block_node.language,

            "delimiter_char": code_block_node.delimiter_char,
            "delimiter_count": code_block_node.delimiter_count,
            "delimiter_indentation": code_block_node.indentation_width,

            "content": code_block_node.content,
            "raw_content": code_block_node.raw_content
        }
    if code_block_node.type == CodeBlockType.INDENTED:
        return {
            "node_type": "code_block",
            "type": "indented",
            "content": code_block_node.content
        }
    return {
        "node_type": "code_block",
        "type": "fenced",
        "language": code_block_node.language,

        "content": code_block_node.content
    }

def paragraph(paragraph_node: Node, debug: bool):
    if debug:
        return {
            "node_type": "paragraph",
            "open": paragraph_node.open,
            "raw_content": paragraph_node.raw_content,
            "children": []
        }
    return {
        "node_type": "paragraph",
        "children": []
    }

def heading(heading_node: HeadingNode, debug: bool):
    if debug:
        return {
            "node_type": "heading",
            "open": heading_node.open,
            "heading_level": heading_node.heading_level,
            "raw_content": heading_node.raw_content,
            "children": []
        }
    return {
        "node_type": "heading",
        "heading_level": heading_node.heading_level,
        "children": []
    }

def thematic_break(thematic_break_node: Node, debug: bool): # yes, "debug" is unused here; despite this, it needs to stay due to the generalized caller in the main method
    return {
        "node_type": "thematic_break"
    }

def html_block(html_block_node: HTMLBlockNode, debug: bool):
    if debug:
        return {
            "node_type": "html_block",
            "open": html_block_node.open,
            "content": html_block_node.raw_content
        }
    return {
        "node_type": "html_block",
        "content": html_block_node.raw_content
    } 

def list(list_node: ListNode, debug: bool):
    if debug:
        if list_node.list_type == ListType.UNORDERED:
            return {
                "node_type": "list",
                "open": list_node.open,

                "list_type": "unordered",
                "list_delimiter": list_node.delimiter,
                "is_tight": list_node.is_tight,

                "raw_content": list_node.raw_content,
                "children": []
            }
        return {
            "node_type": "list",
            "open": list_node.open,

            "list_type": "ordered",
            "list_delimiter": list_node.delimiter,
            "list_starting_number": list_node.starting_number,
            "is_tight": list_node.is_tight,

            "raw_content": list_node.raw_content,
            "children": []
        }
    if list_node.list_type == ListType.UNORDERED:
        return {
            "node_type": "list",
            "list_type": "unordered",
            "is_tight": list_node.is_tight,
            "children": []
        }
    return {
        "node_type": "list",
        "list_type": "ordered",
        "list_starting_number": list_node.starting_number,
        "is_tight": list_node.is_tight,
        "children": []
    }

def list_item(list_item_node: ListItemNode, debug: bool):
    if debug:
        return {
            "node_type": "list_item",
            "open": list_item_node.open,
            "continuation_indent": list_item_node.continuation_indent,
            "raw_content": list_item_node.raw_content,
            "children": []
        }
    return {
        "node_type": "list_item",
        "children": []
    }

def text(text_node: Node, debug: bool): # for all inline nodes it is the same as the "thematic_break": not needed in the method itself, however necessary due to the calling method
    return {
        "node_type": "text",
        "content": text_node.content
    }

def softbreak(softbreak_node: Node, debug: bool):
    return {
        "node_type": "softbreak"
    }

def linebreak(linebreak_node: Node, debug: bool):
    return {
        "node_type": "linebreak"
    }

def inline_code(inline_code_node: Node, debug: bool):
    return {
        "node_type": "inline_code",
        "content": inline_code_node.raw_content
    }

def emphasis(emphasis_node: Node, debug: bool):
    return {
        "node_type": "emphasis",
        "children": []
    }

def strong(strong_node: Node, debug: bool):
    return {
        "node_type": "strong",
        "children": []
    }

def link(link_node: LinkOrImageNode, debug: bool):
    return {
        "node_type": "link",
        "href": link_node.link_destination,
        "title": link_node.title,
        "text": link_node.content,
        "children": []
    }

def image(image_node: LinkOrImageNode, debug: bool):
    return {
        "node_type": "image",
        "src": image_node.link_destination,
        "title": image_node.title,
        "altText": image_node.content,
        "children": []
    }

def html_inline(html_inline_node: Node, debug: bool):
    return {
        "node_type": "html_inline",
        "content": html_inline_node.raw_content
    }

# -----
ASSOCIATED_FUNCTION = {
    NodeType.BLOCK_QUOTE: block_quote,
    NodeType.CODE_BLOCK: code_block,
    NodeType.PARAGRAPH: paragraph,
    NodeType.HEADING: heading,
    NodeType.THEMATIC_BREAK: thematic_break,
    NodeType.HTML_BLOCK: html_block,
    NodeType.CUSTOM_BLOCK: None,

    NodeType.LIST: list,
    NodeType.LIST_ITEM: list_item,

    NodeType.TEXT: text,
    NodeType.SOFTBREAK: softbreak,
    NodeType.LINEBREAK: linebreak,
    NodeType.INLINE_CODE: inline_code,
    NodeType.EMPHASIS: emphasis,
    NodeType.STRONG: strong,
    NodeType.LINK: link,
    NodeType.IMAGE: image,
    NodeType.HTML_INLINE: html_inline,
    NodeType.CUSTOM_INLINE: None
}

def recursiveRender(root_node: Node, current_ast_as_dict: dict, debug: bool):
    this_node_as_dict = ASSOCIATED_FUNCTION[root_node.node_type](root_node, debug)
    if root_node.children:
        for child in root_node.children:
            recursiveRender(child, this_node_as_dict, debug)
    current_ast_as_dict["children"].append(this_node_as_dict)

class JSONRenderer:
    def __init__(self, options: dict = DEFAULT_OPTIONS):
        self.options = options

        self.ast_as_dict = {
            "node_type": "document",
            "children": []
        }

    def render(self, document_node: Node):
        if document_node.children:
            for child in document_node.children:
                if self.options["debug_infos"]:
                    recursiveRender(child, self.ast_as_dict, True)
                else:
                    recursiveRender(child, self.ast_as_dict, False)

        if self.options["jsonIndent"]:
            return json.dumps(self.ast_as_dict, indent=self.options["jsonIndent"])
        return json.dumps(self.ast_as_dict, indent=0)