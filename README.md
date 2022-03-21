# Spelling Corrector

It is a spelling corrector based on symspell algorithm which can be integrated with any existing projects.

## How it works:

The input string is split into tokens. Then the Symmetric Delete spelling correction algorithm is used to get suggestions for every token individually.

#### Dictionary generation

Dictionary quality is paramount for correction quality, This Spell Corrector is made for tourism and travell based chatbot. In order to achieve this two data sources were combined by intersection:

> 10000 most frequent used english words + tourism and travell based english words

#### Packages used:

- re
- nltk
- pickle

## Installation

Download or Clone the repo, Navigate to the directory containing the files and run
` python setup.py`

Final project can be found here [MP Travel and Tourism Facebook Chatbot](https://github.com/TheSumitTiwari/MP-Travel-and-Tourism-Facebook-Chatbot)
