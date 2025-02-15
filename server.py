from flask import Flask, request, jsonify
from retrieve import retrieve

app = Flask(__name__)


@app.route("/query", methods=["POST"])
def handle_post():
    request_json = request.json
    context = retrieve(request_json["query"], 4)
    print(context)
    return jsonify({"context": context})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
