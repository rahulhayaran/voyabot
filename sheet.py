import pandas as pd
from glob import glob

class Sheet:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        if self.filename not in glob('*.xlsx'):
            pd.DataFrame().to_excel(self.filename, index=False, engine='openpyxl')

    def read(self) -> pd.DataFrame:
        return pd.read_excel(self.filename, engine='openpyxl', converters={'Firm':str,'Roles':str})

    def write(self, append_df: pd.DataFrame) -> None:
        curr_df = self.read()
        curr_df = pd.concat([curr_df, append_df])
        curr_df.drop_duplicates().to_excel(self.filename, index=False, engine='openpyxl')

    def clear(self) -> None:
        curr_df = self.read()
        curr_df.iloc[0:0].to_excel(self.filename, index=False, engine='openpyxl')


class Queries(Sheet):
    def __init__(self, filename: str):
        super().__init__(filename)

    def get_queries(self) -> pd.Series:
        sheet = self.read()
        return zip(sheet.index, sheet['Firm'], sheet['Roles'])