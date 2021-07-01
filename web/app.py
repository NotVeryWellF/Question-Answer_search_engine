from bidaf.models import BidirectionalAttentionFlow
from flask import Flask, request, render_template, redirect, url_for
from main import process_query


app = Flask(__name__)


@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        query = str(request.form["search"])
        return redirect(url_for('answer', query=query))
    return render_template('search.html')


@app.route("/answer", methods=['GET'])
def answer():
    query = request.args.get("query")
    data = process_query(query, app.model)
    query_answer = data[0]["answer"]
    docs = data[1]
    time_scope = data[2]
    if not time_scope["explicit"]:
        time_scope = "None"
    else:
        time_scope = "From " + str(time_scope["start"]) + " to " + str(time_scope["end"])
    return render_template("answer.html", docs=docs, answer=query_answer, question=query, scope=time_scope)


if __name__ == "__main__":
    bidaf_model = BidirectionalAttentionFlow(400)
    bidaf_model.load_bidaf("/home/cendien/PycharmProjects/IR_Project/model/bidaf_50.h5")
    app.model = bidaf_model
    app.run("0.0.0.0")
