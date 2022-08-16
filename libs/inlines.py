import re

from .link_reference_definition import LinkReferenceDefinition
from .node import *
from .regexps import *
from enum import Enum


class DelimiterFunction(Enum):
    OPENING = 1
    CLOSING = 2
    BOTH = 3

class DelimiterStackEntry:
    def __init__(self, referenced_text_node: Node, delimiter_type: str, delimiter_count: int, function: int, active: bool = True):
        self.referenced_text_node = referenced_text_node
        self.delimiter_type = delimiter_type
        self.delimiter_count = delimiter_count
        self.function = function    # one of the values in "DelimiterFunction" enum
        self.active = active

    def __eq__(self, other):
        return (self.referenced_text_node == other.referenced_text_node)

    def __str__(self):
        return f'{repr(self)}:\n(referenced_text_node:{self.referenced_text_node}\nself.delimiter_type:{self.delimiter_type}\n\t↳count:{self.delimiter_count}\nfunction:{self.function}\nactive:{self.active})'

def parseInlines(root_block: Node, raw_content: str, link_reference_defs: list[LinkReferenceDefinition]):
    current_char_index = 0
    raw_content_from_index = root_block.raw_content[current_char_index:]

    delimiter_stack: list[DelimiterStackEntry] = []

    while current_char_index < len(root_block.raw_content):
        if re.match(r"\\", raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            if len(raw_content_from_index) == 1: # if the '\' is the end of input
                next_char = ""
            else:
                next_char = raw_content_from_index[1]

            if re.match(f"[{ASCII_PUNCTUATION_CHARS}]", next_char):
                new_node = Node(root_block, NodeType.TEXT)
                new_node.content = next_char
                new_node.open = False

                current_char_index += 2
                raw_content_from_index = root_block.raw_content[current_char_index:]
            elif re.match(LINE_ENDING, next_char):
                new_node = Node(root_block, NodeType.LINEBREAK)
                new_node.open = False

                current_char_index += 2
                raw_content_from_index = root_block.raw_content[current_char_index:]
            else:
                new_node = Node(root_block, NodeType.TEXT)
                new_node.content = "\\"
                new_node.open = False

                current_char_index += 1
                raw_content_from_index = root_block.raw_content[current_char_index:]

        elif re.match(URI_AUTOLINK, raw_content_from_index): # re.match NOT re.search, as we're searching for matches only in the beginning of the string to ensure a correct order of parsing
            root_block.getDeepestOpenChild().open = False

            link_dest = re.match(URI_AUTOLINK, raw_content_from_index).group().replace("<", "").replace(">", "")

            new_node = LinkOrImageNode(root_block, NodeType.LINK, link_dest, link_dest, "")
            new_node.open = False
            link_text_node = Node(new_node, NodeType.TEXT)
            link_text_node.content = link_dest
            link_text_node.open = False

            current_char_index += re.match(URI_AUTOLINK, raw_content_from_index).end() # advance the inline parser to the next relevant position in the string
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(EMAIL_AUTOLINK, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            link_dest = re.match(EMAIL_AUTOLINK, raw_content_from_index).group().replace("<", "").replace(">", "")

            new_node = LinkOrImageNode(root_block, NodeType.LINK, "mailto:" + link_dest, link_dest, "")
            new_node.open = False
            link_text_node = Node(new_node, NodeType.TEXT)
            link_text_node.content = link_dest
            link_text_node.open = False

            current_char_index += re.match(EMAIL_AUTOLINK, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]

        elif re.match(OPEN_TAG, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            # TODO: attribute matching
            tag_name = re.match(TAG_NAME, raw_content_from_index[1:]).group() # remove the opening "<", then parse it as the name

            new_node = HTMLInlineNode(root_block, HTMLInlineType.OPEN_TAG, tag_name)
            new_node.open = False

            current_char_index += re.match(OPEN_TAG, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(CLOSING_TAG, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False
            
            # TODO: attribute matching
            tag_name = re.match(TAG_NAME, raw_content_from_index[2:]).group() # same as above

            new_node = HTMLInlineNode(root_block, HTMLInlineType.CLOSING_TAG, tag_name)
            new_node.open = False

            current_char_index += re.match(CLOSING_TAG, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(HTML_COMMENT, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            comment_text = re.match(HTML_COMMENT, raw_content_from_index).group()[4:-3]

            new_node = HTMLInlineNode(root_block, HTMLInlineType.HTML_COMMENT, "", comment_text)
            new_node.open = False

            current_char_index += re.match(HTML_COMMENT, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(PROCESSING_INSTRUCTION, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            instruction_text = re.match(PROCESSING_INSTRUCTION, raw_content_from_index).group()[2:-2]

            new_node = HTMLInlineNode(root_block, HTMLInlineType.PROCESSING_INSTRUCTION, "", instruction_text)
            new_node.open = False

            current_char_index += re.match(PROCESSING_INSTRUCTION, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(DECLARATION, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            declaration_text = re.match(DECLARATION, raw_content_from_index).group()[2:-1]

            new_node = HTMLInlineNode(root_block, HTMLInlineType.DECLARATION, "", declaration_text)
            new_node.open = False

            current_char_index += re.match(DECLARATION, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(CDATA_SECTION, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            cdata_text = re.match(CDATA_SECTION, raw_content_from_index).group()[9:-3]

            new_node = HTMLInlineNode(root_block, HTMLInlineType.CDATA_SECTION, "", cdata_text)
            new_node.open = False

            current_char_index += re.match(CDATA_SECTION, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]

        elif re.match(BACKTICK_STRING, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            delimiter_length = len(re.match(BACKTICK_STRING, raw_content_from_index).group())
            raw_code = ""

            matching_closer_found = False
            starting_index = current_char_index

            current_char_index += delimiter_length
            raw_content_from_index = root_block.raw_content[current_char_index:]

            while not current_char_index >= len(root_block.raw_content):
                if re.match(BACKTICK_STRING, raw_content_from_index):
                    if len(re.match(BACKTICK_STRING, raw_content_from_index).group()) == delimiter_length:
                        matching_closer_found = True
                        break
                    else: # We have found a delimiter string; however, it does not match the length requirement: hence append it at once so the parser does not get confused and tries to parse this string "one by one"
                        raw_code += re.match(BACKTICK_STRING, raw_content_from_index).group()
                        current_char_index += len(re.match(BACKTICK_STRING, raw_content_from_index).group())
                        raw_content_from_index = root_block.raw_content[current_char_index:]
                if not current_char_index >= len(root_block.raw_content): # No, this test is not redundant, as the else block above can result in advancing the parser state such that current_char_index >= len(root_block.raw_content) is true and consequently throwing an IndexError
                    raw_code += raw_content_from_index[0]
                    current_char_index += 1
                    raw_content_from_index = root_block.raw_content[current_char_index:]

            if matching_closer_found:
                raw_code = re.sub(LINE_ENDING, " ", raw_code)

                if raw_code[0] == " " and raw_code[-1] == " " and not re.match("^[ ]+$", raw_code):
                    raw_code = raw_code[1:-1]

                new_node = Node(root_block, NodeType.INLINE_CODE, raw_code)
                new_node.open = False
            
                current_char_index += delimiter_length
                raw_content_from_index = root_block.raw_content[current_char_index:]
            else: # We have not found a matching closer until the end of the block; hence we append literal backticks to the root block
                current_char_index = starting_index
                raw_content_from_index = root_block.raw_content[current_char_index:]

                new_node = Node(root_block, NodeType.TEXT)
                new_node.content = "`" * delimiter_length
                new_node.open = False

                current_char_index += delimiter_length
                raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(LINE_ENDING, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            new_node = Node(root_block, NodeType.SOFTBREAK)
            new_node.open = False

            current_char_index += re.match(LINE_ENDING, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(HARD_LINE_BREAK, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            new_node = Node(root_block, NodeType.LINEBREAK)
            new_node.open = False

            current_char_index += re.match(HARD_LINE_BREAK, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]

        elif re.match(DELIMITER_RUN, raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            new_node = Node(root_block, NodeType.TEXT)
            new_node.content = re.match(DELIMITER_RUN, raw_content_from_index).group()
            new_node.open = False

            # determine whether it is a left flanking delimiter run or a right flanking delimiter run (or both)
            previous_char = root_block.raw_content[(current_char_index-1)]
            if current_char_index + len(new_node.content) >= len(root_block.raw_content):
                next_char = ""
            else:
                next_char = root_block.raw_content[(current_char_index + len(new_node.content))]
            delim_stack_entry = None

            # left-flanking case 1 + 2a
            if not re.match(UNICODE_WHITESPACE, next_char) and not re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', next_char):
                delim_stack_entry = DelimiterStackEntry(new_node, new_node.content[0], len(new_node.content), DelimiterFunction.OPENING)
                delimiter_stack.append(delim_stack_entry)
            # left-flanking case 1 + 2b
            elif not re.match(UNICODE_WHITESPACE, next_char) and re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', next_char) and (re.match(UNICODE_WHITESPACE, previous_char) or re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', previous_char)):
                delim_stack_entry = DelimiterStackEntry(new_node, new_node.content[0], len(new_node.content), DelimiterFunction.OPENING)
                delimiter_stack.append(delim_stack_entry)

            # right-flanking case 1 + 2a
            # *if*, not *elif*, as a delimiter run can be both left and right flanking at the same time
            if not re.match(UNICODE_WHITESPACE, previous_char) and not re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', previous_char):
                if delim_stack_entry:
                    delim_stack_entry.function = DelimiterFunction.BOTH # if a delimiter stack entry was created by the previous if-statement, then just change the function accordingly
                else:
                    delim_stack_entry = DelimiterStackEntry(new_node, new_node.content[0], len(new_node.content), DelimiterFunction.CLOSING)
                    delimiter_stack.append(delim_stack_entry)
            # right-flanking case 1 + 2b
            elif not re.match(UNICODE_WHITESPACE, previous_char) and re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', previous_char) and (re.match(UNICODE_WHITESPACE, next_char) or re.match(r'[' + UNICODE_PUNCTUATION_CHARS + r']', next_char)):
                if delim_stack_entry:
                    delim_stack_entry.function = DelimiterFunction.BOTH
                else:
                    delim_stack_entry = DelimiterStackEntry(new_node, new_node.content[0], len(new_node.content), DelimiterFunction.CLOSING)
                    delimiter_stack.append(delim_stack_entry)

            current_char_index += re.match(DELIMITER_RUN, raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(r'(?<!\\)\!?\[', raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            new_node = Node(root_block, NodeType.TEXT)
            new_node.content = re.match(r'\!?\[', raw_content_from_index).group()
            new_node.open = False

            delim_stack_entry = DelimiterStackEntry(new_node, new_node.content, 1, DelimiterFunction.OPENING)
            delimiter_stack.append(delim_stack_entry)

            current_char_index += re.match(r'\!?\[', raw_content_from_index).end()
            raw_content_from_index = root_block.raw_content[current_char_index:]
        elif re.match(r']', raw_content_from_index):
            root_block.getDeepestOpenChild().open = False

            look_for_link_or_image(root_block, delimiter_stack, raw_content_from_index[1:], link_reference_defs)

            current_char_index += 1
            raw_content_from_index = root_block.raw_content[current_char_index:]
        else:
            deepest_open_child = root_block.getDeepestOpenChild()
            if deepest_open_child and deepest_open_child.node_type == NodeType.TEXT:
                deepest_open_child.content += raw_content_from_index[0]
            else:
                root_block.getDeepestOpenChild().open = False

                new_node = Node(root_block, NodeType.TEXT)
                new_node.content = raw_content_from_index[0]

            current_char_index += 1
            raw_content_from_index = root_block.raw_content[current_char_index:]

    process_emphasis(root_block, delimiter_stack)
            
# Implementation of the "*process emphasis*" procedure described in the [Appendix of the CommonMark 0.30 spec](https://spec.commonmark.org/0.30/#appendix-a-parsing-strategy). Credit goes to the respective authors.
# TODO: refactor this mess
def process_emphasis(block_node_to_modify: Node, delimiter_stack: list[DelimiterStackEntry], stack_bottom: DelimiterStackEntry = None):
    if not delimiter_stack or len(delimiter_stack) == 1:
        return

    current_position_index = 0
    if stack_bottom:
        current_position_index = (delimiter_stack.index(stack_bottom) + 1)

    if current_position_index >= len(delimiter_stack): # if we have not found a closing delimiter, there is nothing to parse
        return

    current_position = delimiter_stack[current_position_index]
    openers_bottom_star = stack_bottom
    openers_bottom_underscore = stack_bottom

    while True: # this - due to the break in "if not current_position" - will result in actually meaning: While we have not run out of potential closers, as suggested by the reference in the appendix
        if not delimiter_stack or len(delimiter_stack) == 1:
            break

        if current_position_index >= len(delimiter_stack):
            current_position = delimiter_stack[-1]
        else:
            current_position = delimiter_stack[current_position_index] # reset current position just for security

        while not ((current_position.function == DelimiterFunction.CLOSING or current_position.function == DelimiterFunction.BOTH) and (current_position.delimiter_type == "*" or current_position.delimiter_type == "_")): # move current_position forward until we find a potential closer
            if (current_position_index >= len(delimiter_stack) - 1) or (current_position_index == 0 and len(delimiter_stack) == 1): # avoid IndexErrors
                current_position = None
                break
            else:
                current_position_index += 1
                current_position = delimiter_stack[current_position_index]

        if not current_position:
            break
        
        matching_opener = None
        tmp_index = current_position_index
        tmp = current_position
        # look back in the delimiter stack for a matching opener
        if current_position.delimiter_type == "*":
            while True: # one could fuse this "while True" loop and the if block with "tmp.delimiter_type == ...." together; however, I chose against this because - in my opinion - the current version is easier to understand & debug
                if tmp_index == -1:
                    tmp = None
                    break
                else:
                    if tmp.delimiter_type == "*" and (tmp.function == DelimiterFunction.OPENING or tmp.function == DelimiterFunction.BOTH) and not (current_position == tmp):
                        break
                    else:
                        tmp_index -= 1
                        tmp = delimiter_stack[tmp_index]

            if not tmp:
                pass
            elif not openers_bottom_star:
                matching_opener = tmp
            elif tmp_index > delimiter_stack.index(openers_bottom_star):
                matching_opener = tmp
        else:
            while True:
                if tmp_index == -1:
                    tmp = None
                    break
                else:
                    if tmp.delimiter_type == "_" and (tmp.function == DelimiterFunction.OPENING or tmp.function == DelimiterFunction.BOTH) and not (current_position == tmp):
                        break
                    else:
                        tmp_index -= 1
                        tmp = delimiter_stack[tmp_index]

            if not tmp:
                pass
            elif not openers_bottom_underscore:
                matching_opener = tmp
            elif tmp_index > delimiter_stack.index(openers_bottom_underscore):
                matching_opener = tmp


        if matching_opener: # we have found a potential opener
            if not matching_opener.referenced_text_node in block_node_to_modify.children: # it is possible that the matching opener is not actually a delimiter for emphasis, but rather raw textual context of another emphasis; see sec. 6.2, rule #15 for an example of this
                    break
            if matching_opener.delimiter_count >= 2 and current_position.delimiter_count >= 2:
                opener_text_node_index = block_node_to_modify.children.index(matching_opener.referenced_text_node)
                closer_text_node_index = block_node_to_modify.children.index(current_position.referenced_text_node)

                nodes_between_opener_and_closer = block_node_to_modify.children[opener_text_node_index +1:closer_text_node_index]
                del block_node_to_modify.children[opener_text_node_index + 1:closer_text_node_index]

                new_node = Node(block_node_to_modify, NodeType.STRONG)
                block_node_to_modify.children.remove(new_node)
                block_node_to_modify.children.insert(opener_text_node_index + 1, new_node)
                new_node.children.extend(nodes_between_opener_and_closer)
            else:
                opener_text_node_index = block_node_to_modify.children.index(matching_opener.referenced_text_node)
                closer_text_node_index = block_node_to_modify.children.index(current_position.referenced_text_node)

                nodes_between_opener_and_closer = block_node_to_modify.children[opener_text_node_index + 1:closer_text_node_index]
                del block_node_to_modify.children[opener_text_node_index + 1:closer_text_node_index]

                new_node = Node(block_node_to_modify, NodeType.EMPHASIS)
                block_node_to_modify.children.remove(new_node)
                block_node_to_modify.children.insert(opener_text_node_index + 1, new_node)
                new_node.children.extend(nodes_between_opener_and_closer)

            matching_opener_index = delimiter_stack.index(matching_opener)
            del delimiter_stack[matching_opener_index + 1:current_position_index - 1]

            if matching_opener.delimiter_count >= 2 and current_position.delimiter_count >= 2:
                matching_opener.delimiter_count -= 2
                current_position.delimiter_count -= 2
            else:
                matching_opener.delimiter_count -= 1
                current_position.delimiter_count -= 1

            if matching_opener.delimiter_count <= 0:
                block_node_to_modify.children.remove(matching_opener.referenced_text_node)
                delimiter_stack.remove(matching_opener)

            current_position_index = delimiter_stack.index(current_position)

            if current_position.delimiter_count <= 0:
                block_node_to_modify.children.remove(current_position.referenced_text_node)
                delimiter_stack.remove(current_position)

        else: # we have not found a matching opener
            if current_position.delimiter_type == "*":
                if current_position_index == 0: # necessary because else it would lead to delimiter_stack[-1] being called, which is the *last* element in the list, hence destroying this parsing algorithm
                    openers_bottom_star = None
                else:
                    openers_bottom_star = delimiter_stack[current_position_index - 1]
            else:
                if current_position_index == 0:
                    openers_bottom_underscore = None
                else:
                    openers_bottom_underscore = delimiter_stack[current_position_index - 1]

            if current_position.function == DelimiterFunction.CLOSING:
                delimiter_stack.remove(current_position)
            else:
                if current_position_index >= len(delimiter_stack) - 1:
                    return
                else:
                    current_position_index += 1
                    current_position = delimiter_stack[current_position_index]

    # cleanup; last step of the procedure in the appendix
    if stack_bottom:
        del delimiter_stack[delimiter_stack.index(stack_bottom) + 1:]
    else:
        del delimiter_stack[:]

# Implementation of the "*look for link or image*" procedure described in the [Appendix of the CommonMark 0.30 spec](https://spec.commonmark.org/0.30/#appendix-a-parsing-strategy). Credit goes to the respective authors.
def look_for_link_or_image(block_node_to_modify: Node, delimiter_stack: list[DelimiterStackEntry], string_after_bracket: str, link_reference_defs: list[LinkReferenceDefinition]):
    original_string_after_bracket = string_after_bracket
    found_opener = None
    for child in reversed(delimiter_stack): # "look backwards through the stack"
        if child.delimiter_type == "[" or child.delimiter_type == "![":
            found_opener = child
            break
    
    if not found_opener:
        new_node = Node(block_node_to_modify, NodeType.TEXT)
        new_node.content = "]"
        new_node.open = False
    elif not found_opener.active:
        delimiter_stack.remove(found_opener)
        new_node = Node(block_node_to_modify, NodeType.TEXT)
        new_node.content = "]"
        new_node.open = False
    else:
        link_text = None
        link_destination = None
        link_title = None

        matched_link_syntax = False # save whether we have found an actual link to this variable, so we can switch over it later

        # "parse ahead" to see if we have a link and if we have one, what type it is
        # case inline link
        if string_after_bracket and string_after_bracket[0] == "(":
            full_inline_string = "("
            string_after_bracket = string_after_bracket[1:]

            if re.match(LINK_DESTINATION, string_after_bracket.lstrip()):
                link_destination = re.match(LINK_DESTINATION, string_after_bracket.lstrip()).group()

                full_inline_string += string_after_bracket[:re.match(LINK_DESTINATION, string_after_bracket.lstrip()).end()]
                string_after_bracket = string_after_bracket.replace(link_destination, "")

            if re.match(r'[ \t]*' + LINE_ENDING + r'?', string_after_bracket):
                re.sub(r'[ \t]*' + LINE_ENDING + r'?', "", string_after_bracket)
            if re.match(LINK_TITLE, string_after_bracket.lstrip()):
                link_title = re.match(LINK_TITLE, string_after_bracket.lstrip()).group()

                full_inline_string += string_after_bracket[:re.match(LINK_TITLE, string_after_bracket.lstrip()).end() + 1]
                string_after_bracket = string_after_bracket.replace(link_title, "")
            if re.match(r'[ \t]*' + LINE_ENDING + r'?', string_after_bracket):
                re.sub(r'[ \t]*' + LINE_ENDING + r'?', "", string_after_bracket)

            if string_after_bracket.lstrip()[0] == ")":
                block_node_to_modify.raw_content = block_node_to_modify.raw_content.replace(full_inline_string + ")", "") # we need to remove the inline declaration afterwards, so that it does not appear as normal text after the link
                matched_link_syntax = True
        elif string_after_bracket and string_after_bracket[0] == "[": # either a full or collapsed reference link
            string_after_bracket = string_after_bracket[1:]
            if re.match(LINK_LABEL, string_after_bracket):
                possible_link_label = re.match(LINK_LABEL, string_after_bracket).group()

                for reference_def in link_reference_defs:
                    if reference_def.link_label.casefold().strip() == possible_link_label.casefold().strip():
                        link_destination = reference_def.link_destination
                        link_title = reference_def.link_title
                        break
                re.sub(LINK_LABEL, "", string_after_bracket)
            else:
                possible_link_label = "".join([node.raw_content for node in block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) - 1:]])
                
                for reference_def in link_reference_defs:
                    if reference_def.link_label.casefold().strip() == possible_link_label.casefold().strip():
                        link_destination = reference_def.link_destination
                        link_title = reference_def.link_title
                        break

            if string_after_bracket[0] == "]":
                matched_link_syntax = True
        else: # shortcut reference link
            possible_link_label = "".join([node.content for node in block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) - 1:]])

            for reference_def in link_reference_defs:
                    if reference_def.link_label.casefold().strip() == possible_link_label.casefold().strip():
                        link_destination = reference_def.link_destination
                        link_title = reference_def.link_title
                        break

            matched_link_syntax = True

        if matched_link_syntax:
            if found_opener.delimiter_type == "![":
                inlines_after_opener = block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) + 1:]

                del block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) + 1:]

                new_node = LinkOrImageNode(block_node_to_modify, NodeType.IMAGE, link_destination, link_text, link_title)
                new_node.children.extend(inlines_after_opener)

                process_emphasis(new_node, delimiter_stack, found_opener)

                block_node_to_modify.children.remove(found_opener.referenced_text_node)
                delimiter_stack.remove(found_opener)
            else:
                inlines_after_opener = block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) + 1:]
                del block_node_to_modify.children[block_node_to_modify.children.index(found_opener.referenced_text_node) + 1:]

                new_node = LinkOrImageNode(block_node_to_modify, NodeType.LINK, link_destination, link_text, link_title)
                new_node.children.extend(inlines_after_opener)

                process_emphasis(new_node, delimiter_stack, found_opener)

                for entry in delimiter_stack[:delimiter_stack.index(found_opener)]:
                    entry.active = False
                
                block_node_to_modify.children.remove(found_opener.referenced_text_node)
                delimiter_stack.remove(found_opener)
        else:
            delimiter_stack.remove(found_opener)
            new_node = Node(block_node_to_modify, NodeType.TEXT)
            new_node.content = "]"
            new_node.open = False