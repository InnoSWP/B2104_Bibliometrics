import pandas as pd


def quartile_of(a):
    df = pd.read_excel('CiteScore-2011-2020-new-methodology-October-2021.xlsb', sheet_name=1, engine='pyxlsb')
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


print(quartile_of(21100836108))
