# Copyright (c) 2022 Serum

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from enum import IntFlag, auto
import re
from PyQt5.QtCore import (
	Qt,
	QTemporaryFile
)
from PyQt5.QtGui import (
	QFont, 
	QSyntaxHighlighter, 
	QTextCharFormat, 
	QColor
)
from typing import Callable
from enchant import DictWithPWL

class SpellCheckWrapper:
    def __init__(
        self, personal_word_list: list[str], 
		addToDictionary: Callable[[str], None]
    ):
        # Creating temporary file
        self.file = QTemporaryFile()
        self.file.open()
        self.dictionary = DictWithPWL(
            "en_US",
            self.file.fileName(),
        )

        self.addToDictionary = addToDictionary

        self.word_list = set(personal_word_list)
        self.load_words()

    def load_words(self):
        for word in self.word_list:
            self.dictionary.add(word)

    def suggestions(self, word: str) -> list[str]:
        return self.dictionary.suggest(word)

    def correction(self, word: str) -> str:
        return self.dictionary.suggest(word)[0]

    def add(self, new_word: str) -> bool:
        if self.check(new_word):
            return False
        self.word_list.add(new_word)
        self.addToDictionary(new_word)
        self.dictionary.add(new_word)
        return True

    def check(self, word: str) -> bool:
        return self.dictionary.check(word)

    def getNewWords(self) -> set[str]:
        return self.word_list


class SpellChecker(QSyntaxHighlighter):
	re_pattern = re.compile(r"\b([A-Za-z]{2,})\b")

	def highlightBlock(self, text: str) -> None:
		
		if not hasattr(self, "speller"):
			return

		self.misspelledFormat = QTextCharFormat()
		self.misspelledFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
		self.misspelledFormat.setUnderlineColor(Qt.red)

		for word_object in self.re_pattern.finditer(text):
			if not self.speller.check(word_object.group()):
				print('incorrect')
				fmt = QTextCharFormat()
				fmt.setFontItalic(True)
				self.setFormat(
					word_object.start(),
					word_object.end() - word_object.start(),
					fmt,
				)
				

	def setSpeller(self, speller: SpellCheckWrapper):
		self.speller = speller



reHtmlTags     = re.compile('<[^<>@]*>')
reHtmlSymbols  = re.compile(r'&#?\w+;')
reHtmlStrings  = re.compile('"[^"<]*"(?=[^<]*>)')
reHtmlComments = re.compile('<!--[^<>]*-->')
reAsterisks    = re.compile(r'(?<!\*)\*[^ \*][^\*]*\*')
reUnderline    = re.compile(r'(?<!_|\w)_[^_]+_(?!\w)')
reDblAsterisks = re.compile(r'(?<!\*)\*\*((?!\*\*).)*\*\*')
reDblUnderline = re.compile(r'(?<!_|\w)__[^_]+__(?!\w)')
reTrpAsterisks = re.compile(r'\*{3,3}[^\*]+\*{3,3}')
reTrpUnderline = re.compile('__[^_]+___')
reMkdHeaders   = re.compile(r"^ {0,3}(?P<level>#{1,6}) (?P<text>[^\n]+)", re.M)
reMkdLine	   = re.compile(r'---')
reMkdLinksImgs = re.compile(r'(?<=\[)[^\[\]]*(?=\])')
reMkdLinkRefs  = re.compile(r'(?<=\]\()[^\(\)]*(?=\))')
reBlockQuotes  = re.compile('^ *>.+')
reReSTDirects  = re.compile(r'\.\. [a-z]+::')
reReSTRoles    = re.compile('(:[a-z-]+:)(`.+?`)')
reReSTLinks    = re.compile('(`.+?<)(.+?)(>`__?)')
reReSTLinkRefs = re.compile(r'\.\. _`?(.*?)`?: (.*)')
reReSTFldLists = re.compile('^ *:(.*?):')
reTextileHdrs  = re.compile(r'^h[1-6][()<>=]*\.\s.+')
reTextileQuot  = re.compile(r'^bq\.\s.+')
reMkdCodeSpans = re.compile('`[^`]*`')
reMkdMathSpans = re.compile(r'\\[\(\[].*?\\[\)\]]')
reReSTCodeSpan = re.compile('``.+?``')
reWords        = re.compile('[^_\\W]+')
reSpacesOnEnd  = re.compile(r'\s+$')



class Formatter:
	def __init__(self, funcs=None):
		self._funcs = funcs or []
		
	def __or__(self, other):
		result = Formatter(self._funcs.copy())
		if isinstance(other, Formatter):
			result._funcs.extend(other._funcs)

		elif isinstance(other, QFont.Weight):
			result._funcs.append(lambda f: f.setFontWeight(other))



		return result

	def format(self, charFormat):
		for func in self._funcs:
			func(charFormat)

NF = Formatter()
ITAL = Formatter([lambda f: f.setFontItalic(True)])
UNDL = Formatter([lambda f: f.setFontUnderline(True)])

def FG(color):
	return Formatter([lambda f: f.setForeground(QColor(color))])

def QString_length(text):
	# In QString, surrogate pairs are represented using multiple QChars,
	# so the length of QString is not always equal to the number of graphemes
	# in it (which is the case with Python strings).
	return sum(2 if ord(char) > 65535 else 1 for char in text)


class Markup(IntFlag):
	Mkd = auto()
	ReST = auto()
	Textile = auto()
	HTML = auto()

	# Special value which means that no other markup is allowed inside this pattern
	CodeSpan = auto()


docTypesMapping = {
	'Markdown': Markup.Mkd,
	'reStructuredText': Markup.ReST,
	'Textile': Markup.Textile,
	'html': Markup.HTML,
}


class SyntaxHighlighter(QSyntaxHighlighter):
	
	#: For spell checking
	# r"\b([A-Za-z]{2,})\b"
	re_pattern = re.compile(r"\b([A-Za-z]{2,})\b")

	def __init__(
		self, 
		parent=None, 
		docType=None, 
		dictionaries=None, 
		palette=None,
		spell_checker=None
	):
		super(SyntaxHighlighter, self).__init__(parent)
		
		self.palette = palette
		self.dictionaries = dictionaries
		self.docType = docType
		self.speller = spell_checker

		darker = QColor(self.palette.COLOR_TEXT_2).darker(200).name()
		self.patterns = (
			# regex,         color,                                markups
			(reMkdCodeSpans, NF,                                   Markup.Mkd | Markup.CodeSpan),
			(reMkdMathSpans, NF,                                   Markup.Mkd | Markup.CodeSpan),
			(reReSTCodeSpan, NF,                                   Markup.ReST | Markup.CodeSpan),
			(reHtmlTags,     FG(self.palette.COLOR_ACCENT_1) | QFont.Weight.Bold,               Markup.Mkd | Markup.Textile | Markup.HTML),
			(reHtmlSymbols,  NF | QFont.Weight.Bold,               Markup.Mkd | Markup.HTML),
			(reHtmlStrings,  NF |QFont.Weight.Bold,                Markup.Mkd | Markup.HTML),
			(reHtmlComments, NF,                   				   Markup.Mkd | Markup.HTML),
			(reAsterisks,    ITAL,                                 Markup.Mkd | Markup.ReST),
			(reUnderline,    ITAL,                                 Markup.Mkd | Markup.Textile),
			(reDblAsterisks, NF | QFont.Weight.Bold,               Markup.Mkd | Markup.ReST | Markup.Textile),
			(reDblUnderline, NF | QFont.Weight.Bold,               Markup.Mkd),
			(reTrpAsterisks, ITAL | QFont.Weight.Bold,             Markup.Mkd),
			(reTrpUnderline, ITAL | QFont.Weight.Bold,             Markup.Mkd),
			(reMkdHeaders,   NF | QFont.Weight.Bold,               Markup.Mkd),
			(reMkdLine, 	 FG(darker),						   Markup.Mkd),
			(reMkdLinksImgs, NF,                                   Markup.Mkd),
			(reMkdLinkRefs,  ITAL | UNDL,                          Markup.Mkd),
			(reBlockQuotes,  NF,                                   Markup.Mkd),
			(reReSTDirects,  NF | QFont.Weight.Bold,               Markup.ReST),
			(reReSTRoles,    NF, QFont.Weight.Bold,                Markup.ReST),
			(reTextileHdrs,  NF | QFont.Weight.Black,              Markup.Textile),
			(reTextileQuot,  NF,                                   Markup.Textile),
			(reAsterisks,    NF | QFont.Weight.Bold,               Markup.Textile),
			(reDblUnderline, ITAL,                                 Markup.Textile),
			(reReSTLinks,    NF, NF, ITAL | UNDL, NF,              Markup.ReST),
			(reReSTLinkRefs, NF, ITAL | UNDL,                      Markup.ReST),
			(reReSTFldLists, NF,                                   Markup.ReST),
		)

	def spellCheck(self, text):
		self.misspelledFormat = QTextCharFormat()
		self.misspelledFormat.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)
		self.misspelledFormat.setUnderlineColor(Qt.red)

		for word_object in self.re_pattern.finditer(text):
			if not self.speller.check(word_object.group()):
				self.setFormat(
					word_object.start(),
					word_object.end() - word_object.start(),
					self.misspelledFormat,
				)


	def highlightBlock(self, text):
		# Syntax highlighter
	
		codeSpans = set()

		if self.speller:
			self.spellCheck(text)
		
		if self.docType in docTypesMapping:
			markup = docTypesMapping[self.docType]
			for pattern, *formatters, markups in self.patterns:
				if not (markup & markups):
					continue
				for match in pattern.finditer(text):
					start, end = match.start(), match.end()
					if markups & Markup.CodeSpan:
						codeSpans.add((start, end))
					elif any(start < codeEnd and end > codeStart
							 for codeStart, codeEnd in codeSpans):
						# Ignore any syntax if its match intersects with code spans.
						# See https://github.com/retext-project/retext/issues/529
						continue
					for i, formatter in enumerate(formatters):
						charFormat = QTextCharFormat()
						formatter.format(charFormat)
						self.setFormat(QString_length(text[:match.start(i)]),
									   QString_length(match.group(i)),
									   charFormat)
		for match in reSpacesOnEnd.finditer(text):
			charFormat = QTextCharFormat()
			self.setFormat(QString_length(text[:match.start()]),
						   QString_length(match.group(0)),
						   charFormat)
		# Spell checker
		if self.dictionaries:
			charFormat = QTextCharFormat()
			charFormat.setUnderlineColor(Qt.GlobalColor.red)
			charFormat.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SpellCheckUnderline)
			for match in reWords.finditer(text):
				finalFormat = QTextCharFormat()
				finalFormat.merge(charFormat)
				finalFormat.merge(self.format(match.start()))
				word = match.group(0)
				correct = any(dictionary.check(word) for dictionary in self.dictionaries)
				if not correct:
					self.setFormat(QString_length(text[:match.start()]),
								   QString_length(word),
								   finalFormat)
