###############################################################################
#    Copyright (C) 2007 Cody Precord                                          #
#    staff@editra.org                                                         #
#                                                                             #
#    Editra is free software; you can redistribute it and#or modify           #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation; either version 2 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    Editra is distributed in the hope that it will be useful,                #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program; if not, write to the                            #
#    Free Software Foundation, Inc.,                                          #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.                #
###############################################################################

"""
#-----------------------------------------------------------------------------#
# FILE: caml.py                                                               #
# AUTHOR: Cody Precord                                                        #
#                                                                             #
# SUMMARY:                                                                    #
# Lexer configuration module for                                              #
#                                                                             #
# @todo:                                                                      #
#                                                                             #
#-----------------------------------------------------------------------------#
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
import synglob
#-----------------------------------------------------------------------------#

#---- Keyword Definitions ----#
# Objective Caml 3 textual keywords
CAML_KW1 = (0, "and as assert asr begin class constraint do done downto else "
               "end exception external false for fun function functor if in "
               "include inherit initializer land lazy let lor lsl lsr lxor "
               "match method mod module mutable new object of open or private "
               "rec sig struct then to true try type val virtual when while "
               "with")

# Caml optional keywords
CAML_KW2 = (1, "option Some None ignore ref lnot succ pred parser")

# Caml type/library keywords
CAML_KW3 = (2, "array bool char float int list string unit")

#---- End Keyword Definitions ----#

#---- Syntax Style Specs ----#
SYNTAX_ITEMS = [('STC_CAML_CHAR', 'char_style'),
                ('STC_CAML_COMMENT', 'comment_style'),
                ('STC_CAML_COMMENT1', 'comment_style'),
                ('STC_CAML_COMMENT2', 'comment_style'),
                ('STC_CAML_COMMENT3', 'comment_style'),
                ('STC_CAML_DEFAULT', 'default_style'),
                ('STC_CAML_IDENTIFIER', 'default_style'),
                ('STC_CAML_KEYWORD', 'keyword_style'),
                ('STC_CAML_KEYWORD2', 'pre_style'),
                ('STC_CAML_KEYWORD3', 'keyword2_style'),
                ('STC_CAML_LINE_NUM', 'number_style'),
                ('STC_CAML_NUMBER', 'number_style'),
                ('STC_CAML_OPERATOR', 'operator_style'),
                ('STC_CAML_STRING', 'string_style'),
                ('STC_CAML_TAGNAME', 'directive_style')] #STYLE ME]

#---- Extra Properties ----#
# Folding is not currently supported

#-----------------------------------------------------------------------------#

#---- Required Module Functions ----#
def Keywords(lang_id=0):
    """Returns Specified Keywords List
    @keyword lang_id: used to select specific subset of keywords

    """
    if lang_id == synglob.ID_LANG_CAML:
        return [CAML_KW1, CAML_KW2, CAML_KW3]
    else:
        return list()

def SyntaxSpec(lang_id=0):
    """Syntax Specifications
    @keyword lang_id: used for selecting a specific subset of syntax specs

    """
    if lang_id == synglob.ID_LANG_CAML:
        return SYNTAX_ITEMS
    else:
        return list()

def Properties(lang_id=0):
    """Returns a list of Extra Properties to set
    @keyword lang_id: used to select a specific set of properties

    """
    if lang_id == synglob.ID_LANG_CAML:
        return list()
    else:
        return list()

def CommentPattern(lang_id=0):
    """Returns a list of characters used to comment a block of code
    @keyword lang_id: used to select a specific subset of comment pattern(s)

    """
    if lang_id == synglob.ID_LANG_CAML:
        return [u'(*', u'*)']
    else:
        return list()

#---- End Required Module Functions ----#

#---- Syntax Modules Internal Functions ----#
def KeywordString():
    """Returns the specified Keyword String
    @note: not used by most modules

    """
    return None

#---- End Syntax Modules Internal Functions ----#
