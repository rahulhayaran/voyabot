import pandas as pd
from sheet import Queries

inputs = Queries('queries.xlsx')
inputs.clear()
inputs.write(pd.DataFrame([''], columns=['Queries']))