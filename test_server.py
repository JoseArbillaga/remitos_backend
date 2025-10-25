""""""

"""
Servidor minimo para testing
"""Servidor de prueba mínimo para diagnosticar problemas

""""""

from fastapi import FastAPIfrom fastapi import FastAPI

from fastapi.responses import HTMLResponseimport uvicorn



app = FastAPI(title="Test Server")app = FastAPI()



@app.get("/")@app.get("/")

async def root():async def root():

    return {"message": "Server working", "status": "ok"}    return {"message": "Test server working"}



@app.get("/health")@app.get("/health")

async def health():async def health():

    return {"status": "healthy"}    return {"status": "ok"}



@app.get("/test")if __name__ == "__main__":

async def test_page():    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>🚀 Test Server Working!</h1>
        <p>This is a simple test page.</p>
        <p><a href="/health">Health Check</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)