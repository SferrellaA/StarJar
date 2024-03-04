from browser import document
from browser.html import *

'''
The final part is not actually a coding challenge
You must find three pieces of information and enter them below:
- one word, all lower case, no space

1. What campaign did the squadron first serve in?
2. Who is the longest-serving civillian in the squadron?
3. What was the earlier name of the squadron?
'''

form = FORM()
form <= LABEL("Question 1", For="one") + INPUT(id="one", type="text") + BR()
form <= LABEL("Question 1", For="two") + INPUT(id="two", type="text") + BR()
form <= LABEL("Question 1", For="three") + INPUT(id="three", type="text") + BR()
form <= INPUT(type="submit", value="Submit") + BR()
document <= form