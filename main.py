import tensorflow as tf
import pandas as pd
from Preprocessor import Preprocessor
from rank_bm25 import BM25Okapi
import json
from time_estimation import query_time_scope_estimation, document_temporal_data, query_time_scope_estimation_implicit
from calculations import distance, probability_of_time

TIME_SPAN = 38  # Months
LAMBDA = 0.0625
DOCUMENT_NUMBER = 10
FOR_ANSWER = 2
H = 0.75
ALPHA = 0.5

json_dataset = open("/home/cendien/PycharmProjects/IR_Project/dataset/preprocessed.json")
documents = json.load(json_dataset)

prep = Preprocessor()

global graph
graph = tf.get_default_graph()


def process_query(query: str, model):
    prep_query = prep.preprocess(query)
    print(query, prep_query)

    texts = [doc["text"] for doc in documents.values()]
    prep_texts = [doc["preprocessed_text"] for doc in documents.values()]
    dates = [pd.to_datetime(doc["date"]) for doc in documents.values()]
    titles = [doc["title"] for doc in documents.values()]
    links = [doc["link"] for doc in documents.values()]

    bm25 = BM25Okapi(prep_texts)
    bm25_scores = bm25.get_scores(prep_query)
    max_bm25_score = max(bm25_scores)
    bm25_scores = [(i/max_bm25_score) for i in bm25_scores]

    query_documents = zip(texts, prep_texts, dates, bm25_scores, titles, links)
    query_documents = sorted(query_documents, key=lambda x: x[3], reverse=True)[:DOCUMENT_NUMBER]

    query_texts = [doc[0] for doc in query_documents]
    query_prep_texts = [doc[1] for doc in query_documents]
    query_doc_dates = [doc[2] for doc in query_documents]
    query_doc_bm25 = [doc[3] for doc in query_documents]
    query_titles = [doc[4] for doc in query_documents]
    query_links = [doc[5] for doc in query_documents]

    query_time_scope = query_time_scope_estimation(query)
    print(query_time_scope)

    if not query_time_scope["explicit"]:
        query_time_scope = query_time_scope_estimation_implicit(query_doc_dates)

    if query_time_scope["explicit"]:
        timestamp_temporal_scores = []
        content_temporal_scores = []
        temporal_scores = []
        final_scores = []
        temporal_data = []

        for i in range(len(query_documents)):
            timestamp_temporal_score = 0
            if query_time_scope["start"] <= query_doc_dates[i]:
                D = distance(query_time_scope, query_doc_dates[i], TIME_SPAN)
                timestamp_temporal_score = LAMBDA**D
            timestamp_temporal_scores.append(timestamp_temporal_score)
        print(timestamp_temporal_scores)

        for i in range(len(query_documents)):
            print(query_texts[i])
            temporal_data.append(document_temporal_data(query_texts[i], query_doc_dates[i]))

        for i in temporal_data:
            probability_of_start = probability_of_time(len(i[0]), query_time_scope["start"], i[0], H)
            probability_of_end = probability_of_time(len(i[0]), query_time_scope["end"], i[1], H)
            content_temporal_scores.append((probability_of_start + probability_of_end)/2)
        print(content_temporal_scores)

        max_timestamp_score = max(timestamp_temporal_scores)
        max_content_score = max(content_temporal_scores)
        temporal_scores = [(1/2)*(score[0]/max_timestamp_score + score[1]/max_content_score) for score in zip(timestamp_temporal_scores, content_temporal_scores)]
        print(temporal_scores)
        final_scores = [((1 - ALPHA)*sc[0] + ALPHA*sc[1]) for sc in zip(query_doc_bm25, temporal_scores)]
        print(final_scores)

        re_ranked_documents = zip(query_texts, query_prep_texts, query_doc_dates, final_scores, query_titles, query_links)
        re_ranked_documents = sorted(re_ranked_documents, key=lambda x: x[3], reverse=True)
    else:
        re_ranked_documents = query_documents

    text_for_answering_question = ""
    for i in range(FOR_ANSWER):
        text_for_answering_question += " " + re_ranked_documents[i][0].lower()

    with graph.as_default():
        answer = model.predict_ans(text_for_answering_question, query.lower())

    return answer, re_ranked_documents, query_time_scope

