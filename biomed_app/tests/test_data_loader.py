import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_loader import (
    load_preop_data,
    load_oper_data,
    load_discharge_data,
    load_followup_data
)

def test_load_preop_data():
    df = load_preop_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Preop_Restrict_Score' in df.columns
    assert 'Preop_Pain_Score' in df.columns

def test_load_oper_data():
    df = load_oper_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Operation_Type' in df.columns

def test_load_discharge_data():
    df = load_discharge_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Intra_Complications' in df.columns

def test_load_followup_data():
    df = load_followup_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Followup_Complications' in df.columns
