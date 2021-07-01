import datetime
from typing import Tuple, Dict
from python_sutime.sutime.sutime import SUTime
import json
import pandas as pd
import aniso8601
import numpy as np


st = SUTime(mark_time_ranges=True, include_range=True)


def query_time_scope_estimation(query: str) -> Dict:
    dates = st.parse(query)
    # dates = json.loads(json_string)
    # print(json.dumps(dates))
    # for i in dates:
    #     print(datetime.datetime.fromtimestamp(i['value']))
    time_estimation = dict()
    if is_explicit(dates):
        time_estimation["explicit"] = True
        all_dates = []
        for d in dates:
            if d["type"] == "DATE" or d["type"] == "TIME":
                if d["value"] == "PRESENT_REF":
                    all_dates.append(datetime.datetime.now().date())
                    continue
                try:
                    if d["value"].split("-")[1] in ("SU", "WI", "SP", "FA"):
                        if d["value"].split("-")[1] == "SU":
                            all_dates.append(pd.to_datetime(d["value"].split("-")[0] + "-" + "07"))
                        elif d["value"].split("-")[1] == "WI":
                            all_dates.append(pd.to_datetime(d["value"].split("-")[0] + "-" + "01"))
                        elif d["value"].split("-")[1] == "SP":
                            all_dates.append(pd.to_datetime(d["value"].split("-")[0] + "-" + "04"))
                        elif d["value"].split("-")[1] == "FA":
                            all_dates.append(pd.to_datetime(d["value"].split("-")[0] + "-" + "10"))
                        continue
                except Exception as e:
                    print(e)
                try:
                    all_dates.append(pd.to_datetime(d["value"]).date())
                except Exception as e:
                    print(e)
            elif d["type"] == "DURATION":
                try:
                    time_estimation["start"] = pd.to_datetime(d["value"]["begin"]).date()
                    time_estimation["end"] = pd.to_datetime(d["value"]["end"]).date()
                    return time_estimation
                except Exception as e:
                    print(e)
        if len(all_dates) == 0:
            time_estimation["explicit"] = False
            return time_estimation
        all_dates.sort()
        time_estimation["start"] = all_dates[0]
        time_estimation["end"] = all_dates[-1]
    else:
        time_estimation["explicit"] = False
    return time_estimation


def is_explicit(dates) -> bool:
    return len(dates) > 0


def document_temporal_data(document_text: str, publication_date):
    dates = st.parse(document_text, reference_date=str(publication_date))
    T_start = []
    T_end = []
    for d in dates:
        start_date: datetime.datetime
        end_date: datetime.datetime
        if d["type"] == "DATE" or d["type"] == "TIME":
            if d["value"] == "PRESENT_REF" or d["value"] == "FUTURE_REF":
                start_date = publication_date.date()
                T_start.append(start_date)
                continue
            if d["value"] == "PAST_REF":
                end_date = publication_date.date()
                T_end.append(end_date)
                continue
            try:
                if d["value"].split("-")[1] in ("SU", "WI", "SP", "FA"):
                    if d["value"].split("-")[1] == "SU":
                        start_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "06")
                        end_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "08")
                    elif d["value"].split("-")[1] == "WI":
                        start_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "01")
                        end_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "02")
                    elif d["value"].split("-")[1] == "SP":
                        start_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "03")
                        end_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "05")
                    elif d["value"].split("-")[1] == "FA":
                        start_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "09")
                        end_date = aniso8601.parse_date(d["value"].split("-")[0] + "-" + "11")
                    T_start.append(start_date)
                    T_end.append(end_date)
                    continue
            except Exception as e:
                # print(e)
                pass
            try:
                if len(d["value"]) == 4:
                    start_date = aniso8601.parse_date(d["value"] + "-" + "01" + "-" + "01")
                    end_date = aniso8601.parse_date(d["value"] + "-" + "12" + "-" + "31")
                    T_start.append(start_date)
                    T_end.append(end_date)
                    continue
            except Exception as e:
                # print(e)
                pass
            try:
                if d["type"] == "TIME":
                    start_date = aniso8601.parse_date(d["value"].split("T")[0])
                else:
                    start_date = aniso8601.parse_date(d["value"])
                T_start.append(start_date)
                continue
            except Exception as e:
                # print(e)
                pass
        elif d["type"] == "DURATION":
            if isinstance(d["value"], dict):
                if "end" in d["value"].keys() and "begin" in d["value"].keys():
                    try:
                        if d["value"]["begin"].find("XXXX") >= 0 and d["value"]["end"].find("XXXX") >= 0:
                            d["value"]["begin"] = d["value"]["begin"].replace("XXXX", str(publication_date.year))
                            d["value"]["end"] = d["value"]["end"].replace("XXXX", str(publication_date.year))
                            start_date = aniso8601.parse_date(d["value"]["begin"])
                            end_date = aniso8601.parse_date(d["value"]["end"])
                            T_start.append(start_date)
                            T_end.append(end_date)
                            continue
                        elif d["value"]["begin"].find("XXXX") >= 0:
                            d["value"]["begin"] = d["value"]["begin"].replace("XXXX", d["value"]["end"].split("-")[0])
                            start_date = aniso8601.parse_date(d["value"]["begin"])
                            end_date = aniso8601.parse_date(d["value"]["end"])
                            T_start.append(start_date)
                            T_end.append(end_date)
                            continue
                        elif d["value"]["end"].find("XXXX") >= 0:
                            d["value"]["end"] = d["value"]["end"].replace("XXXX", d["value"]["begin"].split("-")[0])
                            start_date = aniso8601.parse_date(d["value"]["begin"])
                            end_date = aniso8601.parse_date(d["value"]["end"])
                            T_start.append(start_date)
                            T_end.append(end_date)
                            continue
                        else:
                            start_date = aniso8601.parse_date(d["value"]["begin"])
                            end_date = aniso8601.parse_date(d["value"]["end"])
                            T_start.append(start_date)
                            T_end.append(end_date)
                            continue
                    except Exception as e:
                        # print(e)
                        pass
            else:
                if d["value"] in ("PXD", "PXW", "PXM", "PXY"):
                    if d["value"] == "PXD":
                        d["value"] = "P1D"
                    elif d["value"] == "PXW":
                        d["value"] = "P1W"
                    elif d["value"] == "PXM":
                        d["value"] = "P1M"
                    elif d["value"] == "PXY":
                        d["value"] = "P1Y"
                try:
                    duration = aniso8601.parse_duration(d["value"])
                    end_date = publication_date.date()
                    start_date = end_date - duration
                    T_start.append(start_date)
                    T_end.append(end_date)
                    continue
                except Exception as e:
                    # print(e)
                    pass
    # print(json.dumps(dates, indent=4))
    # print(T_start)
    # print(T_end)
    return T_start, T_end


def query_time_scope_estimation_implicit(document_dates):
    time_estimation = dict()

    month = aniso8601.parse_duration("P1M")
    dates_data = dict()
    curr_date = aniso8601.parse_date("2015-01-01")

    while curr_date < datetime.date.today():
        dates_data[curr_date] = 0
        curr_date += month

    for i in dates_data.keys():
        for j in document_dates:
            if i.year == j.year and i.month == j.month:
                dates_data[i] += 1

    dates = list(dates_data.keys())
    count = list(dates_data.values())
    avrg = sum(count)/len(count)
    count = [i - avrg for i in count]

    max_spike = 0
    curr_spike = 0
    maxIdx = 0
    currLen = 0
    currIdx = 0
    max_spike_len = 0
    for i in range(len(count)):
        if count[i] > 0:
            curr_spike += count[i]
            currLen += 1
            if currLen == 1:
                currIdx = i
        else:
            if curr_spike > max_spike:
                max_spike = curr_spike
                maxIdx = currIdx
                max_spike_len = currLen
            currLen = 0
            curr_spike = 0
    if max_spike > 0:
        start = dates[maxIdx]
        end = dates[maxIdx + max_spike_len - 1]
        time_estimation["start"] = start
        time_estimation["end"] = end
        time_estimation["explicit"] = True
    else:
        time_estimation["explicit"] = False
    return time_estimation

