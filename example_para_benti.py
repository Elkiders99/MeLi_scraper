# pirmero instalar estas dos libs:
# $ pip install requests
# $ pip install beautifulsoup4


import requests
from bs4 import BeautifulSoup

# hacemos el request. 
html = requests.get('tu-pagina-web.com').text

# Creamos un objecto BeautifulSoup con el html. Este objeto esta piola 
# porque en lugar de tener el string del html tenemos una representacion
# al estilo de un arbol.
soup = BeautifulSoup(html, "html.parser")

data = parse_html(soup)

output_data(data)

def parse_html(soup):
    # hacer cosas con la sopa para extraer lo que necesites: ://www.crummy.com/software/BeautifulSoup/bs4/doc/ 
    return data

def output_data(data):
    # aca llamas a la libreria csv o tomas cualquier accion para outputear tu data
    print(data)
