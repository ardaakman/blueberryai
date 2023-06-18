import uvicorn 

if __name__ == "__main__":
    uvicorn.run("websocket:app", port=9000, host="127.0.0.1", reload=True)