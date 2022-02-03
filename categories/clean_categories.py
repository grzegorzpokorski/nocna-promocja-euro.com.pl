import pandas as pd

# wczytuje dane
df = pd.read_csv('./categories.csv', header=0)

# usuwam powtórzenia
df.drop_duplicates(inplace=True)

# pozbywam się 'kategorii', które nie mają ofert (jak się okazuje są to linki do konfiguratorów)
df.drop(df[df.offers_count.isnull()].index, inplace=True)

# konwertuje kolumnę offers_count do typu liczbowego
df.offers_count = pd.to_numeric(df.offers_count)
df.to_csv('./categories.csv', index=False)