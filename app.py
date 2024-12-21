from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional
import sqlite3
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_categories():
    conn = sqlite3.connect('processors.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM processors")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def get_sockets():
    conn = sqlite3.connect('processors.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT socket FROM processors")
    sockets = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sockets

def get_cores():
    conn = sqlite3.connect('processors.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cores FROM processors")
    cores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cores

def get_max_frequencies():
    conn = sqlite3.connect('processors.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT max_frequency FROM processors")
    max_frequencies = [row[0] for row in cursor.fetchall()]
    conn.close()
    return max_frequencies

def filter_processors(category=None, socket=None, cores=None, max_frequency=None):
    query = "SELECT rank, name, category, release_date, socket, cores, max_frequency, link FROM processors WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if socket:
        query += " AND socket = ?"
        params.append(socket)

    if cores is not None:
        query += " AND cores = ?"
        params.append(cores)

    if max_frequency is not None:
        query += " AND max_frequency = ?"
        params.append(max_frequency)

    print("Executing query:", query)
    print("With parameters:", params)

    conn = sqlite3.connect('processors.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    processors = cursor.fetchall()
    conn.close()

    return processors



@app.get("/", response_class=HTMLResponse)
async def index(request: Request,
                category: Optional[str] = None,
                socket: Optional[str] = None,
                cores: Optional[str] = None,
                max_frequency: Optional[str] = None):
    logging.info(
        f"Received parameters: category={category}, socket={socket}, cores={cores}, max_frequency={max_frequency}")

    if category in ["All", None]:
        category = None
    if socket in ["All", None]:
        socket = None

    if cores in ["All", None, ""]:
        cores = None
    else:
        try:
            cores = int(cores)
        except ValueError:
            cores = None

    if max_frequency in ["None", None, ""]:
        max_frequency = None
    else:
        try:
            max_frequency = float(max_frequency)
        except ValueError:
            max_frequency = None

    processors = filter_processors(category, socket, cores, max_frequency)
    categories = get_categories()
    sockets = get_sockets()
    all_cores = get_cores()
    max_frequencies = get_max_frequencies()

    logging.info(f"Found {len(processors)} processors")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "processors": processors,
        "categories": categories,
        "sockets": sockets,
        "cores": all_cores,
        "max_frequencies": max_frequencies,
        "selected_category": category,
        "selected_socket": socket,
        "selected_cores": cores,
        "selected_max_frequency": max_frequency
    })


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
