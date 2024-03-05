from browser import document

# background color
document.select_one("body").style = {
    "margin": "40px auto",
    "max-width": "650px",
    "line-height": "1.6",
    "font-size": "18px",
    "color": "#444", 
    "padding": "010px",
    "background-color": "#D2E0FB"
}

# scrollmenu
document.select_one("DIV.scrollmenu").style = {
    "overflow": "auto",
    "white-space": "nowrap",
    "display": "flex",
    "align-items": "center",
}

for f in document.select("figure"):
    f.style = {
        "display": "inline-block",
        "text-align": "center",
        "text-decoration": "none",
    }

for f in document.select("FIGCAPTION"):
    f.style = {"color": "red"}
