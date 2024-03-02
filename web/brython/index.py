from browser import document
from browser.html import *

document.select_one("head") <= TITLE("STOP REVERSE ENGINEERING")
#document <= html.H1("index.py")

header = HEADER()
header <= H1("STOP DOING ") <= CODE("Reverse engineering")
header <= ASIDE("APIS WERE NOT MEANT TO BE UNDERSTOOD")
document <= header

arguments = UL()
arguments <= LI("YEARS OF REVERSE ENGINEERING yet NO REAL-WORLD USE FOR understanding compiled CODE")
arguments <= LI("sure we are not relaying information that could be used against us")
arguments <= LI("security through obscurity")
arguments <= LI("cease and desist")
arguments <= LI("Title 49 Code of Federal Regulations parts § 1540.103(c) states: No person may make, or cause to be made any reproduction or alteration, for fraudulent purpose, of any report, record, security program, access medium, or identification medium issued under this subchapter. ")
arguments <= LI("Computers were supposed to solve meath, not to be programmed")
arguments <= LI("C is a letter, not a language")
arguments <= LI("wanna print() something? Write in a paper with a pen 📁3️⃣3️⃣")
arguments <= LI("\"I'n writing a recursive method with threads to optimize the cpu usage in a 0.02%\" this is a nonsensical statement made by deranged people")
arguments <= LI("glowing text", Class="glowing")
document <= arguments

document <= P("look at what FMA has been demanding your respect for, after we put all the walls around their section")
document <= P() <= STRONG("(this is real computer science done by real computer scientists):")
document <= DIV(Class="scrollmenu")
# The getFigures.py called next will populate this box

document <= P() <= STRONG("IF REVERSE ENGINEERING WAS REAL HOW COME NOBODY THOUGHT OF PUBLISHING SOURCE CODE")
document <= P() <= STRONG("THEY'VE PLAYED US FOR ABSOLUTE FOOLS")