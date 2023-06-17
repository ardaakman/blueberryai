import uvicorn 


if __name__ == "__main__":
    uvicorn.run("API:app", port=8201, host="127.0.0.1", reload=True)