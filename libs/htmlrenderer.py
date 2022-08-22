from .node import *

DEFAULT_OPTIONS = {
    "indent": 4,
    "include_html_backbone": False,
    "css_styling": "",
    "softbreak_rendering": "" # TODO: actually implement this into the renderer
}

def block_quote(block_quote_node: Node):
    output = "<blockquote>"
    for child in block_quote_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</blockquote>"

    return output

def code_block(code_block_node: CodeBlockNode):
    if code_block_node.language:
        if not code_block_node.raw_content or code_block_node.raw_content[-1] == "\n": # code block rendering is handled very weirdly in the CommonMark spec (in my opinion)
            return f"<pre><code class=\"language-{code_block_node.language}\">{code_block_node.raw_content}</code></pre>"
        return f"<pre><code class=\"language-{code_block_node.language}\">{code_block_node.raw_content}\n</code></pre>"

    if not code_block_node.raw_content or code_block_node.raw_content[-1] == "\n":
        return f"<pre><code>{code_block_node.raw_content}</code></pre>"
    return f"<pre><code>{code_block_node.raw_content}\n</code></pre>"

def paragraph(paragraph_node: Node):
    if not paragraph_node.children:
        return ""

    output = "<p>"
    for child in paragraph_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</p>"

    return output

def heading(heading_node: HeadingNode):
    output = f"<h{heading_node.heading_level}>"
    for child in heading_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += f"</h{heading_node.heading_level}>"

    return output

def thematic_break(thematic_break_node: Node):
    return "<hr/>"

def html_block(html_block_node: HTMLBlockNode):
    return html_block_node.raw_content

def list(list_node: ListNode):
    tag_name = "ul"
    if list_node.list_type == ListType.ORDERED:
        tag_name = "ol"

    output = f"<{tag_name}>"
    for child in list_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += f"</{tag_name}>"

    return output

def list_item(list_item_node: ListItemNode): # TODO: implement list tightness
    output = "<li>"
    for child in list_item_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</li>"

    return output

def text(text_node: Node):
    return text_node.content

def softbreak(softbreak_node: Node):
    return "\n"

def linebreak(linebreak_node: Node):
    return "<br/>"

def inline_code(inline_code_node: Node):
    return f"<code>{inline_code_node.raw_content}</code>"

def emphasis(emphasis_node: Node):
    output = "<em>"
    for child in emphasis_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</em>"

    return output

def strong(strong_node: Node):
    output = "<strong>"
    for child in strong_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</strong>"

    return output

def link(link_node: LinkOrImageNode):
    if link_node.title:
        output = f"<a href=\"{link_node.link_destination}\" title=\"{link_node.title}\">"
    else:
        output = f"<a href=\"{link_node.link_destination}\">"

    for child in link_node.children:
        output += ASSOCIATED_FUNCTION[child.node_type](child)
    output += "</a>"

    return output

def image(image_node: LinkOrImageNode):
    alt_text = ""
    for child in image_node.children: # TODO: fix this
        alt_text += child.content

    if image_node.title:
        return f"<img src=\"{image_node.link_destination}\" alt=\"{alt_text}\" title=\"{image_node.title}\" />"
    return f"<img src=\"{image_node.link_destination}\" alt=\"{alt_text}\" />"

def html_inline(html_inline_node: Node):
    return f"{html_inline_node.raw_content}"

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

class HTMLRenderer:
    def __init__(self, options: dict = DEFAULT_OPTIONS):
        self.options = options

        self.output = ""
        
    def render(self, document_node: Node):
        self.output = ""

        if self.options["include_html_backbone"]:
            self.output = f"<!DOCTYPE html>\n<html>\n<head>\n<style>" + self.options["css_styling"] + "</style>\n</head>\n<body>\n"

        if document_node.children:
            for child in document_node.children:
                self.output += ASSOCIATED_FUNCTION[child.node_type](child)

        if self.options["include_html_backbone"]:
            self.output += "\n</body>\n</html>"

        return self.output

    def renderWithoutStyling(self, document_node: Node):
        self.output = ""

        if self.options["include_html_backbone"]:
            self.output = f"<!DOCTYPE html>\n<html>\n<body>\n"

        if document_node.children:
            for child in document_node.children:
                self.output += ASSOCIATED_FUNCTION[child.node_type](child)

        if self.options["include_html_backbone"]:
            self.output += "\n</body>\n</html>"

        return self.output