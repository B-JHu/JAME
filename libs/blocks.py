import re

from .link_reference_definition import LinkReferenceDefinition
from .node import *
from .regexps import *

def canRemainOpen(block: Node, line: str):
    match block.node_type:
        case NodeType.DOCUMENT:
            return True
        case NodeType.BLOCK_QUOTE:
            if re.search(BLOCK_QUOTE_MARKER, line):
                return True
            return False

        case NodeType.CODE_BLOCK:
            if block.type == CodeBlockType.FENCED:
                search_result = re.search(FENCED_CODE_BLOCK_ENDING, line)
                if not search_result:
                    return True
                
                found_fence_char = search_result.group().strip()[1]
                if found_fence_char == block.delimiter_char:
                    return False
                return True
            else:
                if re.search(BLANK_LINE, line):
                    return False
                return True

        case NodeType.PARAGRAPH:
            if re.search(BLANK_LINE, line):
                return False
            if re.search(SETEXT_HEADING_UNDERLINE, line): # needed for correct parsing of setext-headings -> we need it to be closed, so openBlock() can be called to correctly build the heading
                return False
            if re.search(BULLET_LIST_MARKER, line.lstrip()) or re.search(ORDERED_LIST_MARKER, line.lstrip()): # lists may interrupt a paragraph
                return False
            if re.search(BLOCK_1_START, line) or re.search(BLOCK_2_START, line) or re.search(BLOCK_3_START, line) or re.search(BLOCK_4_START, line) or re.search(BLOCK_5_START, line) or re.search(BLOCK_6_START, line): # sec. 4.6: "An HTML block of types 1–6 can interrupt a paragraph"
                return False
            return True

        case NodeType.HEADING:
            return False

        case NodeType.THEMATIC_BREAK:
            return False

        case NodeType.HTML_BLOCK:
            if block.block_type == 1 and not re.search(re.compile(BLOCK_1_END, re.IGNORECASE), line):
                return True
            elif block.block_type == 2 and not re.search(BLOCK_2_END, line):
                return True
            elif block.block_type == 3 and not re.search(BLOCK_3_END, line):
                return True
            elif block.block_type == 4 and not re.search(BLOCK_4_END, line):
                return True
            elif block.block_type == 5 and not re.search(BLOCK_5_END, line):
                return True
            elif block.block_type == 6 and not re.search(BLOCK_6_END, line):
                return True
            elif block.block_type == 7 and not re.search(BLOCK_7_END, line):
                return True
            return False
            
        case NodeType.CUSTOM_BLOCK:
            return False

        case NodeType.LIST:
            if block.list_type == ListType.ORDERED:
                list_marker_matchobj = re.search(ORDERED_LIST_MARKER, line)
                if not list_marker_matchobj:
                    return False

                list_delimiter = re.sub(r'\d+', "", list_marker_matchobj.group().strip())
                if list_delimiter == block.delimiter:
                    return True
                return False
            else:
                list_marker_matchobj = re.search(BULLET_LIST_MARKER, line)
                if not list_marker_matchobj:
                    return False

                list_delimiter = list_marker_matchobj.group().strip()
                if list_delimiter == block.delimiter:
                    return True
                return False

        case NodeType.LIST_ITEM:
            if re.search(BLANK_LINE, line): # a blank line does not close a list item; however, it determines if the list is "tight" or "loose" as per sec. 5.3
                return True

            # reasoning for this is in sec. 5.2
            line_indent_match = re.search(r'^[ \t]+', line)
            if not line_indent_match:
                return False

            line_indent_length = len(line_indent_match.group().replace(r'\t', "    ")) # sec. 2.2: tabs count as 4 spaces of indentation

            if line_indent_length >= block.continuation_indent:
                return True
            return False

        case _:
            raise ValueError("Node type of provided block is not associated with a block:" + block.node_type)

# for paragraph continuation text: when a paragraph node is open, and "> some blockquote" is added to it, we need to remove the "> " block quote marker (same for lists)
def removePossibleMarkers(line: str):
    removed_block_quotes = re.sub(BLOCK_QUOTE_MARKER, "", line)
    removed_ol_list_markers = re.sub(ORDERED_LIST_MARKER, "", removed_block_quotes)
    removed_ul_list_markers = re.sub(BULLET_LIST_MARKER, "", removed_ol_list_markers)

    return removed_ul_list_markers.lstrip()

def openBlock(document: Node, line: str, deepest_open_child: Node = None):
    if re.search(ATX_HEADING, line):
        heading_level = len(re.search(ATX_HEADING, line).group().strip())

        removed_heading_marker = re.sub(ATX_HEADING, "", line)
        removed_closing_seq = re.sub(ATX_HEADING_OPT_CLOSING_SEQ, "", removed_heading_marker)
        removed_spaces = removed_closing_seq.strip()

        new_node = HeadingNode(document, heading_level, removed_spaces)
        new_node.open = False
    elif re.search(SETEXT_HEADING_UNDERLINE, line):
        if document.children and document.getLastChild().node_type == NodeType.PARAGRAPH:
            original_paragraph_text = document.getLastChild().raw_content
            heading_level = 1
            if line.strip()[0] == '-':
                heading_level = 2

            del document.children[-1] # the new heading replaces the old paragraph

            new_node = HeadingNode(document, heading_level, original_paragraph_text)
            new_node.open = False
        elif re.search(THEMATIC_BREAK, line): # if a setext heading underline is in the first line of input, it could well be a thematic break
            new_node = Node(document, NodeType.THEMATIC_BREAK)
            new_node.open = False
        else: # neither a setext heading nor a thematic break; return dashes as literal
            new_node = Node(document, NodeType.PARAGRAPH, line)
    elif re.search(THEMATIC_BREAK, line):
        new_node = Node(document, NodeType.THEMATIC_BREAK)
        new_node.open = False
    elif re.search(INDENTED_CODE_BLOCK, line):
        code_text = line[4:]

        new_node = CodeBlockNode(document, CodeBlockType.INDENTED, raw_content=code_text)
    elif re.search(FENCED_CODE_BLOCK_BEGINNING, line):
        info_text = None
        if line.lstrip()[0] == '`':
            info_text = line.replace("`", "").strip()
        else:
            info_text = re.sub(r'^[ ]{0,3}~+', "", line).strip()
        if info_text == "":
            info_text = None

        indentation_match_obj = re.search(r'^[ ]{0,3}', line)
        indentation_width = 0
        if indentation_match_obj:
            indentation_width = len(indentation_match_obj.group())

        delimiter_char = line.lstrip()[0]
        delimiter_count = len(re.sub(r'[^' + delimiter_char + ']', "", line).strip())

        new_node = CodeBlockNode(document, CodeBlockType.FENCED, info_text, delimiter_char, delimiter_count, indentation_width)
    
    elif re.search(re.compile(BLOCK_1_START, re.IGNORECASE), line): # re.compile needed to have case-insensitive search as mandated in sec. 4.6
        new_node = HTMLBlockNode(document, 1, line)

        if re.search(re.compile(BLOCK_1_END, re.IGNORECASE), line): # an HTML block may be closed on the same line it has been opened
            new_node.open = False
    elif re.search(BLOCK_2_START, line):
        new_node = HTMLBlockNode(document, 2, line)

        if re.search(re.compile(BLOCK_2_END, re.IGNORECASE), line):
            new_node.open = False
    elif re.search(BLOCK_3_START, line):
        new_node = HTMLBlockNode(document, 3, line)

        if re.search(re.compile(BLOCK_3_END, re.IGNORECASE), line):
            new_node.open = False
    elif re.search(BLOCK_4_START, line):
        new_node = HTMLBlockNode(document, 4, line)

        if re.search(re.compile(BLOCK_4_END, re.IGNORECASE), line):
            new_node.open = False
    elif re.search(BLOCK_5_START, line):
        new_node = HTMLBlockNode(document, 5, line)

        if re.search(re.compile(BLOCK_5_END, re.IGNORECASE), line):
            new_node.open = False
    elif re.search(re.compile(BLOCK_6_START, re.IGNORECASE), line):
        new_node = HTMLBlockNode(document, 6, line)

        if re.search(re.compile(BLOCK_6_END, re.IGNORECASE), line):
            new_node.open = False
    elif re.search(BLOCK_7_START, line):
        new_node = HTMLBlockNode(document, 7, line)

        # block 7 cannot be closed on the same line it is opened as its closing condition is a blank line
    elif re.search(BLOCK_QUOTE_MARKER, line):
        line_without_marker = re.sub(BLOCK_QUOTE_MARKER, "", line)
        new_node = Node(document, NodeType.BLOCK_QUOTE, line_without_marker)
        openBlock(new_node, line_without_marker) # block quotes are container blocks
    elif re.search(BULLET_LIST_MARKER, line):
        line_without_marker = re.sub(BULLET_LIST_MARKER, "", line)

        continuation_indent_matchobj = re.search(BULLET_LIST_MARKER, line)
        continuation_indent = len(continuation_indent_matchobj.group().lstrip())

        delimiter_char = re.search(BULLET_LIST_MARKER, line).group().strip()

        if deepest_open_child and deepest_open_child.node_type == NodeType.LIST and deepest_open_child.list_type == ListType.UNORDERED and deepest_open_child.delimiter == delimiter_char: # if another list of the same type **and the same delimiter** is already open, then just append the new list item to that one
            new_node = ListItemNode(deepest_open_child, line_without_marker, continuation_indent)

            openBlock(new_node, line_without_marker)
        else:      
            new_list_node = ListNode(document, ListType.UNORDERED, delimiter_char)
            new_node = ListItemNode(new_list_node, line_without_marker, continuation_indent)

            openBlock(new_node, line_without_marker)
    elif re.search(ORDERED_LIST_MARKER, line):
        line_without_marker = re.sub(ORDERED_LIST_MARKER, "", line)

        list_marker = re.search(ORDERED_LIST_MARKER, line).group()
        continuation_indent = len(list_marker.lstrip())
        delimiter_char = re.sub(r'\d', "", list_marker.strip())
        starting_number = int(re.sub(r'(\.|\))', "", list_marker.strip()))

        if deepest_open_child and deepest_open_child.node_type == NodeType.LIST and deepest_open_child.list_type == ListType.ORDERED and deepest_open_child.delimiter == delimiter_char: # same as bullet list
            new_node = ListItemNode(deepest_open_child, line_without_marker, continuation_indent)

            openBlock(new_node, line_without_marker)
        else:
            new_list_node = ListNode(document, ListType.ORDERED, delimiter_char, starting_number)
            new_node = ListItemNode(new_list_node, line_without_marker, continuation_indent)

            openBlock(new_node, line_without_marker)
    else: # just a normal paragraph
        if not re.search(BLANK_LINE, line):
            new_node = Node(document, NodeType.PARAGRAPH, line.lstrip())

def parseLinkReferenceDefs(paragraph_node: Node, link_reference_defs: list[LinkReferenceDefinition]):
    possible_reference_defs = re.finditer(LINK_LABEL + r'\:', paragraph_node.raw_content)

    original_raw_content = paragraph_node.raw_content
    
    for definition in possible_reference_defs:
        full_reference_def_string = definition.group() # save the full reference definition as a string so we can remove it from the paragraph node's raw content later

        string_after_label = original_raw_content[definition.end():]
        link_reference = None

        if re.search(LINK_DESTINATION, string_after_label.lstrip()):
            full_reference_def_string += string_after_label[:re.search(LINK_DESTINATION, string_after_label.lstrip()).end()]

            link_reference = LinkReferenceDefinition(definition.group().lstrip()[1:-2], re.search(LINK_DESTINATION, string_after_label.lstrip()).group())
            link_reference_defs.append(link_reference)

            string_after_label = string_after_label[re.search(LINK_DESTINATION, string_after_label.lstrip()).end():]

        if link_reference and re.search(LINK_TITLE, string_after_label.lstrip()):
            full_reference_def_string += string_after_label[:re.search(LINK_TITLE, string_after_label.lstrip()).end()]

            link_reference.link_title = re.search(LINK_TITLE, string_after_label.lstrip()).group()[1:-1] # remove the surrounding quotation marks or brackets

        if link_reference:
            paragraph_node.raw_content = paragraph_node.raw_content.replace(full_reference_def_string, "") # delete the link reference defs from the node's raw content, as link reference definitions are not "a structural element of the document" (sec. 4.7)