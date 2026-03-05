import pandas as pd
df = pd.read_csv("Datasource/airbnb_clean.csv")
print("Price > 500:", len(df[df["Price"]>500]))
print("Price > 1000:", len(df[df["Price"]>1000]))
print("P90:", df["Price"].quantile(0.90))
print("P95:", df["Price"].quantile(0.95))
print("P99:", df["Price"].quantile(0.99))
print("Reviews > 6:", len(df[df["Number Of Reviews"]>6]))
