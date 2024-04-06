from modal import Image, Stub, wsgi_app
import modal

stub = Stub(
    "example-web-flask",
    image=Image.debian_slim().pip_install("flask", "pymongo", "openai", "flask-cors"),
    secrets=[modal.Secret.from_name("flask_secrets")],
)


@stub.function()
def generate_vector(text):
    import openai
    import os
    import random
    import time

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    while True:
        try:
            response = client.embeddings.create(
                input=text, model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except openai.RateLimitError:
            attempt += 1
            wait_time = min(2**attempt + random.random(), 60)
            if attempt == 10:
                break
            time.sleep(wait_time)
        except Exception as e:
            break
    return None


@stub.function()
def generate_ics(text):
    import openai
    import os

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = "Generate a summary of the users command Say nothing else except one line about what it does:\n\n"
    prompt += f"{text}"
    # print(prompt)
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo",
    )
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return expl



@stub.function()
def search_email(gname, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][""]
    return {"result": 200, "commands": []}

@stub.function()
def search_calendar(gname, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    db = client[gname][""]
    return {"result": 200, "commands": []}


@stub.function()
def add_calendar(gname, command):
    import pymongo
    import openai
    import os
    import json

    client = pymongo.MongoClient(os.environ["MONGO_URL"])

    return {"result": 200, "inserted_id": ''}


@stub.function()
def add_email(gname, repo, content):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    return {"result": 200, "inserted_id": ''}


@stub.function()
def search_calendar(gname, repo, query):
    import pymongo
    import openai
    import os

    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client["hi"]
    openai.api_key = os.environ["OPENAI_API_KEY"]

    query_vector = generate_vector.local(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "vec",
                "queryVector": query_vector,
                "numCandidates": 5,
                "limit": 3,
            }
        }
    ]
    results = db.aggregate(pipeline)
    results = [
        {
            "hash": result["hash"],
            "message": result["message"],
            "branch": result["branch"],
        }
        for result in results
    ]
    return {"result": 200, "commits": results}


@stub.function()
@wsgi_app()
def flask_app():
    from flask import Flask, request
    from flask_cors import CORS, cross_origin

    web_app = Flask(__name__)
    cors = CORS(web_app)

    return web_app