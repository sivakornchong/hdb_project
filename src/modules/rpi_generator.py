import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from collections import defaultdict
from modules.utils.logging_fn import logger

RPI_dict_location = "data/RPI_dict.csv"


def format_index_df(df):
    df["Year"] = df["Year"].bfill()  # Backward-fill missing years
    roman_to_number = {"I": "1", "II": "2", "III": "3", "IV": "4"}  # Convert Roman quarters to numeric
    df["Quarter"] = df["Quarter"].map(roman_to_number)
    df["Period"] = df["Quarter"] + "Q" + df["Year"].astype(int).astype(str)
    df["Index"] = df["Index"].astype(float)

    return df[["Period", "Index"]]


def webscrapping():
    url = "https://www.hdb.gov.sg/residential/selling-a-flat/overview/resale-statistics"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "lxml")
    tables = soup.find_all("table")

    # Check tables for the one with column "% Change from Previous Quarter"
    for i, table in enumerate(tables):
        if "% Change from Previous Quarter" in table.text:
            # print(f"Found potential RPI table at index {i}")
            html_str = str(table)
            df = pd.read_html(StringIO(html_str))[0]

            return df


# I will get 5 data points for RPI, this function is to extrapolate it.
def extrapolate_future_quarters(df, num_periods=2):
    df = df.copy()
    df = df[::-1].reset_index(drop=True)  # Flip the order so the latest date is last
    df["Pct_Change"] = df["Index"].pct_change()
    pct_changes = df["Pct_Change"].dropna()
    avg_change = pct_changes.mean()

    # Start extrapolating from the latest known index
    last_index = df.loc[len(df) - 1, "Index"]
    last_period = df.loc[len(df) - 1, "Period"]

    # Extract numeric quarter and year
    last_q, last_y = int(last_period[0]), int(last_period[2:])

    # Generate future periods
    extrapolated_periods = []
    extrapolated_values = []

    for _ in range(num_periods):
        # Increment quarter and possibly year
        if last_q == 4:
            last_q = 1
            last_y += 1
        else:
            last_q += 1

        # New period string
        new_period = f"{last_q}Q{last_y}"
        last_index *= 1 + avg_change

        extrapolated_periods.append(new_period)
        extrapolated_values.append(round(last_index, 1))

    results = pd.DataFrame({"Period": extrapolated_periods, "Index": extrapolated_values})
    return results


def merge_on_shared_rows(base_df, new_df, key="Period"):
    base_df = base_df.set_index(key)
    new_df = new_df.set_index(key)
    base_df.update(new_df, join="left")
    return base_df.reset_index()


def collate_tables(df_formatted, extrapolated_table):
    original_table = pd.read_csv(RPI_dict_location, names=["Period", "Index"])
    # print("Here is the original", original_table)

    row_dict = defaultdict(float)

    df_priority = [df_formatted, extrapolated_table, original_table]
    for df in df_priority:
        for _, row in df.iterrows():
            row_key = row["Period"]
            row_data = row["Index"]
            if row_key not in row_dict.keys():
                # print(f"Updated with {row}")
                row_dict[row_key] = row_data

    return pd.DataFrame(list(row_dict.items()), columns=["Period", "Index"])


def sort_chrono(df):
    df["Quarter"] = df["Period"].str.extract(r"(\d)Q")[0].astype(int)
    df["Year"] = df["Period"].str.extract(r"Q(\d{4})")[0].astype(int)
    df = df.sort_values(by=["Year", "Quarter"], ascending=False).reset_index(drop=True)
    df = df[["Period", "Index"]]
    return df


def main_rpi():
    df = webscrapping()
    df_formatted = format_index_df(df)
    # print("Formatted table from webscrapping", df_formatted)

    extrapolated_table = extrapolate_future_quarters(df_formatted)

    # print("Extrapolated table", extrapolated_table)
    merged_table = collate_tables(df_formatted, extrapolated_table)
    final_table = sort_chrono(merged_table)
    final_table.to_csv(RPI_dict_location, index=False, header=False)
    logger.info("Regenerated RPI data successfully")


if __name__ == "__main__":
    main_rpi()
