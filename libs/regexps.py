# sec. 2: Preliminaries
LINE_ENDING = '(?:\n|\r|\r\n)'
BLANK_LINE = '^[ \t]*$'
UNICODE_WHITESPACE_CHARS = '\u0020\u00A0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u202F\u205F\u3000\u0009\u000A\u000C\u000D'
UNICODE_WHITESPACE = '[' + UNICODE_WHITESPACE_CHARS + ']+'
ASCII_CONTROL_CHARS = '\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\u0008\u0009\u000A\u000B\u000C\u000D\u000E\u000F\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\u0018\u0019\u001A\u001B\u001C\u001D\u001E\u001F\u007F'
ASCII_PUNCTUATION_CHARS = '\u002D!"#\$%&\'\(\)\*\+,-\.\/\u0021\u0022\u0023\u0024\u0025\u0026\u0027\u0028\u0029\u002A\u002B\u002C\u002E\u002F\:\;\<\=\>\?@\u003A\u003B\u003C\u003D\u003E\u003F\u0040\[\\\]\^_`\u005B\u005C\u005D\u005E\u005F\u0060{\|}~\u007B\u007C\u007D\u007E'
UNICODE_PUNCTUATION_CHARS = ASCII_PUNCTUATION_CHARS + '\u005F\u203F\u2040\u2054\uFE33\uFE34\uFE4D\uFE4E\uFE4F\uFF3F' + '\u058A\u05BE\u1400\u1806\u2010\u2011\u2012\u2013\u2014\u2015\u2E17\u2E1A\u2E3A\u2E3B\u2E40\u301C\u3030\u30A0\uFE31\uFE32\uFE58\uFE63\uFF0D\u10EAD' + '\u0F3B\u0F3D\u169C\u2046\u207E\u208E\u2309\u230B\u232A\u2769\u276D\u276D\u2771\u2773\u2775\u27C6\u27E7\u27E9\u27EB\u27ED\u27EF\u2984\u2986\u2988\u298A\u298C\u298E\u2990\u2992\u2994\u2996\u2998\u29D9\u29DB\u29FD\u2E23\u2E25\u2E27\u2E29\u3009\u300D\u300F\u3011\u3015\u3017\u3019\u301B\u301E\u301F\uFD3E\uFE18\uFE36\uFE38\uFE3A\uFE3C\uFE3E\uFE40\uFE42\uFE44\uFE48\uFE5A\uFE5C\uFE5E\uFF09\uFF3D\uFF5D\uFF60\uFF63' + '\u00BB\u2019\u201D\u203A\u2E03\u2E05\u2E0A\u2E0D\u2E1D\u2E21' + '\u00AB\u2018\u201B\u201C\u201F\u2039\u2E02\u2E04\u2E09\u2E0C\u2E1C\u2E20' + '\u005C\u00A1\u00A7\u00B6\u00B7\u00BF\u037E\u0387\u055A\u055B\u055C\u055D\u055E\u055F\u0589\u05C0\u05C3\u05C6\u05F3\u05F4\u0609\u060A\u060C\u060D\u061B\u061D\u061E\u061F\u066A\u066B\u066C\u066D\u06D4\u0700\u0701\u0702\u0703\u0704\u0705\u0706\u0707\u0708\u0709\u070A\u070B\u070C\u070D\u07F7\u07F8\u07F9\u0830\u0831\u0832\u0833\u0834\u0835\u0836\u0837\u0838\u0839\u083A\u083B\u083C\u083D\u083E\u085E\u0964\u0965\u0970\u09FD\u0AF0\u0C77\u0C84\u0DF4\u0E4F\u0E5A\u0E5B\u0F04\u0F05\u0F06\u0F07\u0F08\u0F09\u0F0A\u0F0B\u0F0C\u0F0D\u0F0E\u0F0F\u0F10\u0F11\u0F12\u0F14\u0F85\u0FD0\u0FD1\u0FD2\u0FD3\u0FD4\u0FD9\u0FDA\u104A\u104B\u104C\u104D\u104E\u104F\u10FB\u1360\u1361\u1362\u1363\u1364\u1365\u1366\u1367\u1368\u166E\u16EB\u16EC\u16ED\u1735\u1736\u17D4\u17D5\u17D6\u17D8\u17D9\u17DA\u1800\u1801\u1802\u1803\u1804\u1805\u1807\u1808\u1809\u180A\u1944\u1945\u1A1E\u1A1F\u1AA0\u1AA1\u1AA2\u1AA3\u1AA4\u1AA5\u1AA6\u1AA8\u1AA9\u1AAA\u1AAB\u1AAC\u1AAD\u1B5A\u1B5B\u1B5C\u1B5C\u1B5D\u1B5E\u1B5F\u1B60\u1B7D\u1B7E\u1BFC\u1BFD\u1BFE\u1BFF\u1C3B\u1C3C\u1C3D\u1C3E\u1C3F\u1C7E\u1C7F\u1CC0\u1CC1\u1CC2\u1CC3\u1CC4\u1CC5\u1CC6\u1CC7\u1CD3\u2016\u2017\u2020\u2021\u2022\u2023\u2024\u2025\u2026\u2027\u2030\u2031\u2032\u2033\u2034\u2035\u2036\u2037\u2038\u203B\u203C\u203D\u203E\u2041\u2042\u2043\u2047\u2048\u2049\u204A\u204B\u204C\u204D\u204E\u204F\u2050\u2051\u2053\u2055\u2056\u2057\u2058\u2059\u205A\u205B\u205C\u205D\u205E\u2CF9\u2CFA\u2CFB\u2CFC\u2CFE\u2CFF\u2D70\u2E00\u2E01\u2E06\u2E07\u2E08\u2E0B\u2E0E\u2E0F\u2E10\u2E11\u2E12\u2E13\u2E14\u2E15\u2E16\u2E18\u2E19\u2E1B\u2E1E\u2E1F\u2E2A\u2E2B\u2E2C\u2E2D\u2E2E\u2E30\u2E31\u2E32\u2E33\u2E34\u2E35\u2E36\u2E37\u2E38\u2E39\u2E3C\u2E3D\u2E3E\u2E3F\u2E41\u2E43\u2E44\u2E45\u2E46\u2E47\u2E48\u2E49\u2E4A\u2E4B\u2E4C\u2E4D\u2E4E\u2E4F\u2E52\u2E53\u2E54\u3001\u3002\u3003\u303D\u30FB\uA4FE\uA4FF\uA60D\uA60E\uA60F\uA673\uA67E\uA6F2\uA6F3\uA6F4\uA6F5\uA6F6\uA6F7\uA874\uA875\uA876\uA877\uA8CE\uA8CF\uA8F8\uA8F9\uA8FA\uA8FC\uA92E\uA92F\uA95F\uA9C1\uA9C2\u19C3\uA9C4\uA9C5\uA9C6\uA9C7\uA9C8\uA9C9\uA9CA\uA9CB\uA9CD\uA9DE\uA9DF\uAA5C\uAA5D\uAA5E\uAA5F\uAADE\uAADF\uAAF0\uAAF1\uABEB\uFE10\uFE11\uFE12\uFE13\uFE14\uFE15\uFE16\uFE19\uFE30\uFE45\uFE46\uFE49\uFE4A\uFE4B\uFE4C\uFE50\uFE51\uFE52\uFE54\uFE55\uFE56\uFE57\uFE5F\uFE60\uFE61\uFE68\uFE6A\uFE6B\uFF01\uFF02\uFF03\uFF05\uFF06\uFF07\uFF0A\uFF0C\uFF0E\uFF0F\uFF1A\uFF1B\uFF1F\uFF20\uFF3C\uFF61\uFF64\uFF65\u10100\u10101\u10102\u1039F\u103D0\u1056F\u10857\u1091F\u1093F\u10A50\u10A51\u10A52\u10A53\u10A54\u10A55\u10A56\u10A57\u10A58\u10A7F\u10AF0\u10AF1\u10AF2\u10AF3\u10AF4\u10AF5\u10AF\u10B39\u10B3A\u10B3B\u10B3C\u10B3D\u10B3E\u10B3F\u10B99\u10B9A\u10B9B\u10B9C\u10F55\u10F56\u10F57\u10F58\u10F59\u10F86\u10F87\u10F88\u10F89\u11047\u11048\u11049\u1104A\u1104B\u1104C\u1104D\u110BB\u110BC\u110BE\u110BF\u110C0\u110C1\u11140\u11141\u11142\u11143\u11174\u11175\u111C5\u111C6\u111C7\u111C8\u111CD\u111DB\u111DD\u111DE\u111DF\u11238\u11239\u1123A\u1123B\u1123C\u1123D\u112A9\u1144B\u1144C\u1144D\u1144E\u1144F\u1145A\u1145\u1145D\u114C6\u115C1\u115C2\u115C3\u115C4\u115C5\u115C6\u115C7\u115C8\u115C9\u115CA\u115CB\u115CC\u115CD\u115CE\u115CF\u115D0\u115D1\u115D2\u115D3\u115D4\u115D5\u115D6\u115D7\u11641\u11642\u11643\u11660\u11661\u11662\u11663\u11664\u11665\u11666\u11667\u11668\u11669\u1166A\u1166B\u1166C\u116B9\u1173C\u1173D\u1173E\u1183B\u11944\u11945\u11946\u119E2\u11A3F\u11A40\u11A41\u11A42\u11A43\u11A44\u11A45\u11A46\u11A9A\u11A9B\u11A9C\u11A9E\u11A9F\u11AA0\u11AA1\u11AA2\u11C41\u11C42\u11C43\u11C44\u11C45\u11C70\u11C71\u11EF7\u11EF8\u11FFF\u12470\u12471\u12472\u12473\u12474\u12FF1\u12FF2\u16A6E\u16A6F\u1AF5\u16B37\u16B38\u16B39\u16B3A\u16B3B\u16B44\u16E97\u16E98\u16E99\u16E9A\u16FE2\u1BC9F\u1DA87\u1DA88\u1DA89\u1DA8A\u1DA8B\u1E95E\u1E95F' + '\u0F3A\u0F3C\u169B\u201A\u201E\u2045\u207D\u208D\u2308\u230A\u2329\u2768\u276A\u276C\u276E\u2770\u2772\u2774\u27C5\u27E6\u27E8\u27EA\u27EC\u27EE\u2983\u2985\u2987\u2989\u298B\u298D\u298F\u2991\u2993\u2995\u2997\u29D8\u29DA\u29FC\u2E22\u2E24\u2E26\u2E28\u2E42\u3008\u300A\u300C\u300E\u3010\u3014\u3016\u3018301A\u301D\uFD3F\uFE17\uFE35\uFE37\uFE39\uFE3B\uFE3D\uFE3F\uFE41\uFE43\uFE47\uFE59\uFE5B\uFE5D\uFF08\uFF3B\uFF5B\uFF5F\uFF62'

# sec. 4: Leaf blocks
THEMATIC_BREAK = '^[ ]{0,3}(?:(?:\-[ \t]*){3,}|(?:\_[ \t]*){3,}|(?:\*[ \t]*){3,})$'
ATX_HEADING = '^[ ]{0,3}#{1,6}(?:[ \t]+|$)'
ATX_HEADING_OPT_CLOSING_SEQ = '[ \t]+#+[ \t]*$'
SETEXT_HEADING_UNDERLINE = '^[ ]{0,3}(?:=+|-{2,})[ \t]*$'

INDENTED_CODE_BLOCK = '^(?:[ ]{4,}|\t+)'
FENCED_CODE_BLOCK_BEGINNING = '^[ ]{0,3}(?:`{3,}(?!.*`)|\~{3,}.*)'
FENCED_CODE_BLOCK_ENDING = '^[ ]{0,3}(?:`|~){3,}[ \t]*$'

## sec. 4.6: HTML blocks
BLOCK_1_START = '^[ ]{0,3}<(?:pre|script|style|textarea)(?:[ ]|\t|>|$)'
BLOCK_1_END = '</(?:pre|script|style|textarea)>'

BLOCK_2_START = '^[ ]{0,3}<!--'
BLOCK_2_END = '-->'

BLOCK_3_START = '^[ ]{0,3}<\?'
BLOCK_3_END = '\?>'

BLOCK_4_START = '^[ ]{0,3}<![A-Za-z]'
BLOCK_4_END = '>'

BLOCK_5_START = '^[ ]{0,3}<!\[CDATA\['
BLOCK_5_END = '\]\]>'

BLOCK_6_START = '^[ ]{0,3}<\/?(?:address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|nav|noframes|ol|optgroup|option|p|param|section|source|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul)(?:[ ]|\t|$|>|\/\>)'
BLOCK_6_END = BLANK_LINE

# from sec. 6.6, because jumps in a spec sheet are somehow OK?
TAG_NAME = '[A-Za-z][A-Za-z0-9\-]*'

ATTRIBUTE_NAME = '[A-Za-z\_\:][A-Za-z0-9\_\.\:\-]*'
UNQUOTED_ATTR_VALUE = '[^\s\"\'\=\<\>\`]+'
SINGLE_QUOT_ATTR_VALUE = '\'[^\']*\''
DOUBLE_QUOT_ATTR_VALUE = '\"[^\"]*\"'
ATTRIBUTE_VALUE = '(?:' + UNQUOTED_ATTR_VALUE + "|" +  SINGLE_QUOT_ATTR_VALUE + "|" + DOUBLE_QUOT_ATTR_VALUE + ')'

ATTRIBUTE_VALUE_SPEC = '(?:[ \t]*(?:\n|\r|\r\n)?\=[ \t]*(?:\n|\r|\r\n)?' + ATTRIBUTE_VALUE + ')'

ATTRIBUTE = '(?:[ \t]+(?:\n|\r|\r\n)?' + ATTRIBUTE_NAME  + ATTRIBUTE_VALUE_SPEC + '?)'

OPEN_TAG = '<' + TAG_NAME + ATTRIBUTE + '*[ \t]*(?:\n|\r|\r\n)?\/?\>'
CLOSING_TAG = '<\/' + TAG_NAME + '[ \t]*(?:\n|\r|\r\n)?\>'

# END stuff from sec. 6.6

BLOCK_7_START = '^[ ]{0,3}(?:' + OPEN_TAG + '|' + CLOSING_TAG + ')[ \t]*$'
BLOCK_7_END = BLANK_LINE
# END sec. 4.6

LINK_LABEL = '(?:^|\n)\[(?:[^\\\[\]]|\\.){0,1000}\]'

LINK_DESTINATION = '(?:<[^\n\<\>]*>|[^\<' + ASCII_CONTROL_CHARS + ' \)][^' + ASCII_CONTROL_CHARS + ' \)]+)' # TODO: link destinations may include non-backslash-escaped closing parentheses if they are a pair of matching parentheses

LINK_TITLE = '(?:\"[^\"]*\"|\'[^\']\'|\([^\(\)]\))'  # TODO: fix this so that "hi \" there" becomes a legitimate link title (backslash escaped quotation marks will currently not match this expression
LINK_REFERENCE_DEF = '^[ ]{0,3}' + LINK_LABEL + '\:[ \t]*(?:\n|\r|\r\n)?' + LINK_DESTINATION + '[ \t]*(?:\n|\r|\r\n)?([ \t]+' + LINK_TITLE + ')?'

# sec. 5: Container blocks
BLOCK_QUOTE_MARKER = '^[ ]{0,3}>[ ]?'

BULLET_LIST_MARKER = '^[ ]{0,3}(?:\-|\+|\*)\s+'
ORDERED_LIST_MARKER = '^[ ]{0,3}\d{1,9}(?:\.|\))\s+'

# sec. 6: Inlines
BACKTICK_STRING = '\`+'
DELIMITER_RUN = '(?:\*+|\_+)'

# No RegExps for sec. 6.4; "heavy lifting" is done in "inlines.py"

SCHEME = '[A-Za-z][A-Za-z\d\+\.\-]{1,31}'
ABS_URI = SCHEME + ':[^' + ASCII_CONTROL_CHARS + ' <>]*'
URI_AUTOLINK = '<' + ABS_URI + '>'

EMAIL_ADDRESS = "[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*"
EMAIL_AUTOLINK = '<' + EMAIL_ADDRESS + '>'

# The rest from sec. 6.6
HTML_COMMENT = '<!---->|<!--(?:-?[^>-])(?:-?[^-])*-->'
PROCESSING_INSTRUCTION = '<\?[^(\?\>)]+\?>'
DECLARATION = '<![A-Za-z][^\>]*>'
CDATA_SECTION = '<!\[CDATA\[(?!]]>).*\]\]>'
# End sec. 6.6

HARD_LINE_BREAK = '(?:[ ]{2,}\n|\\\n)'