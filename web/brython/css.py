from browser import document

document.select_one("body").style = {
    "margin": "40px auto",
    "max-width": "650px",
    "line-height": "1.6",
    "font-size": "18px",
    "color": "#444", 
    "padding": "010px",
    "background-color": "#D2E0FB",
}

'''
h1,h2,h3{line-height:1.2}

'''

# glowing text
for elem in document.select("LI.glowing"):
    elem.style = {"text-shadow": "0 0 5px #00ff00, 0 0 10px #00ff00, 0 0 15px #00ff00;"}
