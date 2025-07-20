import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import timeit
from data_loader import (
    load_preop_data,
    load_oper_data,
    load_discharge_data,
    load_followup_data
)

def benchmark(func, name, number=10):
    duration = timeit.timeit(func, number=number)
    print(f"{name:<25}: {duration/number:.4f} sec (avg over {number} runs)")

if __name__ == "__main__":
    benchmark(load_preop_data, "Preoperative Data")
    benchmark(load_oper_data, "Operative Data")
    benchmark(load_discharge_data, "Discharge Data")
    benchmark(load_followup_data, "Follow-up Data")
