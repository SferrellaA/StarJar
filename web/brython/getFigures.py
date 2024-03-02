from browser import document, html

scrollmenu = document.select_one('.scrollmenu') # get the first (only) scrollmenu element
scrollmenu.style = {
    "overflow": "auto",
    "white-space": "nowrap",
    "display": "flex",
    "align-items": "center",
}


'''
from browser.html import TABLE, TR, TH, TD

def insert_table(event):
    table = TABLE()

    # header row
    table <= TR(TH(f"Column {i}") for i in range(5))

    # table rows
    for row in range(3):
        table <= TR(TD(f"Cell {row}-{i}") for i in range(5))

    document["zone7"].clear()
    document["zone7"] <= table

document["button7"].bind("click", insert_table)
'''

figure = html.FIGURE()
figure <= html.IMG(src="images/computercraft.jpg.png", alt="???")
figure <= html.FIGCAPTION("???", style="color: red;")
figure.style = {
    "display": "inline-block",
    "text-align": "center",
    "text-decoration": "none",
}



scrollmenu <= figure
'''
    <figure>
        <img src="images/computercraft.jpg.png" alt="images/computercraft.jpg.png">
        <figcaption style="color: red;">images/computercraft.jpg.png</figcaption>
    </figure>
    <figure>
        <img src="images/horses_lisp.jpg.png" alt="images/horses_lisp.jpg.png">
        <figcaption style="color: red;">images/horses_lisp.jpg.png</figcaption>
    </figure>
    <figure>
        <img src="images/whiteboard_interviews.jpg.png" alt="images/whiteboard_interviews.jpg.png">
        <figcaption style="color: red;">images/whiteboard_interviews.jpg.png</figcaption>
    </figure>
'''