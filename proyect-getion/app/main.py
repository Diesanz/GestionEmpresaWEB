from fastapi import FastAPI, Query, HTTPException
from routers import gestores, gestiones, visualizar, users
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.include_router(gestores.router)
app.include_router(gestiones.router)
app.include_router(visualizar.router)
app.include_router(users.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las IPs
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home():
    return FileResponse("static/templates/index.html")
@app.get("/login")
async def login():
    return FileResponse("static/templates/inicio.html")

@app.get("/registro")
async def registro():
    return FileResponse("static/templates/registro.html")

@app.get("/gestiones")
async def gestiones():
    return FileResponse("static/templates/gestiones.html")

@app.get("/gestiones/nueva")
async def nueva_gestion():
    return FileResponse("static/templates/gestion.html")

@app.get("/gestiones/modificar")
async def modificar_gestion(id: int = Query(..., description="ID de la gestión a modificar")):
    return FileResponse(f"static/templates/modify-gestiones.html")

@app.get("/gestiones/detalles")
async def detalles_gestion(id: int = Query(..., description="ID de la gestión")):
    return FileResponse(f"static/templates/visualizar.html")

@app.get("/usuarios/creacion")
async def creacion_gestion(id: int = Query(..., description="ID de la gestión")):
    return FileResponse("static/templates/user.html")

@app.get("/addGestorGestión")
async def add_gestor(id: int = Query(..., description="ID de la gestión")):
    return FileResponse("static/templates/manager.html")







