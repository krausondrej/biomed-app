# data_loader.py
import os
import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))

def load_oper_data(fname="mock_oper_data.csv"):
    path = os.path.join(BASE, fname)
    df   = pd.read_csv(path, parse_dates=["OperationDate"])
    df["OperationDate"] = df["OperationDate"].dt.year
    return df

def load_preop_data(fname="mock_preop_data.csv"):
    path = os.path.join(BASE, fname)
    df   = pd.read_csv(path)
    return df

def load_discharge_data(fname="mock_discharge_data.csv"):
    path = os.path.join(BASE, fname)
    df   = pd.read_csv(path)
    return df

def load_followup_data(fname="mock_followup_data.csv"):
    path = os.path.join(BASE, fname)
    df   = pd.read_csv(path)
    return df
