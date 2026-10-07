from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "venture mobile application Backend Running"
    }