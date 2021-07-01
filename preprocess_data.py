import pandas as pd
from Preprocessor import Preprocessor
import json
from tqdm import tqdm
from time_estimation import document_temporal_data

prep = Preprocessor()

dataset = pd.read_csv("dataset/aninewsdata.csv", header=0)

id = 1
preprocessed_dataset = dict()
for i in tqdm(dataset.values):
    preprocessed_dataset[id] = dict()
    preprocessed_dataset[id]["date"] = i[4]
    preprocessed_dataset[id]["text"] = i[3]
    preprocessed_dataset[id]["title"] = i[1]
    preprocessed_dataset[id]["link"] = i[2]
    preprocessed_dataset[id]["preprocessed_text"] = prep.preprocess(preprocessed_dataset[id]["text"])
    id += 1

file = open('dataset/preprocessed.json', 'w')
json.dump(preprocessed_dataset, file)
