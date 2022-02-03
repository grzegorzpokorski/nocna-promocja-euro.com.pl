import pandas as pd

# wczytuje dane
df = pd.read_csv('./categories.csv', header=0)

# usuwam powtórzenia
df.drop_duplicates(inplace=True)

# usówam kategorie powtarzające się w kategoriach głównych
df.drop_duplicates(subset=['link_to_category', 'offers_count'] ,inplace=True)

# pozbywam się 'kategorii', które nie mają ofert (jak się okazuje są to linki do konfiguratorów)
df.drop(df[df.offers_count.isnull()].index, inplace=True)

# konwertuje kolumnę offers_count do typu liczbowego
df.offers_count = pd.to_numeric(df.offers_count)
df.to_csv('./categories_C.csv', index=False)