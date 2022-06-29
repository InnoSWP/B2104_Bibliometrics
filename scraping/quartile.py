import pandas as pd


def quartile_of(a: int, year: str):
    df = pd.read_excel('quartiles2020.xlsx', sheet_name="CiteScore " + year)
    low = 0
    high = df.shape[0] - 1
    h = high
    while low <= high:
        mid = (high + low) // 2
        if df.iloc[mid, 0] < a:
            low = mid + 1
        elif df.iloc[mid, 0] > a:
            high = mid - 1
        else:
            low, high = mid, mid
            while df.iloc[low, 0] == mid and low - 1 != -1:
                low -= 1
            while df.iloc[high, 0] == mid and high + 1 != h + 1:
                high += 1
            high += 1
            return df.loc[low:high, "Quartile"].min()
    return -1
