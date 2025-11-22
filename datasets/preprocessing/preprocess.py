import pandas as pd
import re

# Load dataset
df = pd.read_csv("../scraping/scrapedDataset.csv")

# 🧹 Step 1: Drop duplicates and empty rows
df.drop_duplicates(inplace=True)
df.dropna(subset=["scheme_name","description"], inplace=True)

# 🧽 Step 2: Clean whitespace and newlines
df["scheme_name"] = df["scheme_name"].str.strip()
df["description"] = df["description"].str.replace(r'\s+', ' ', regex=True).str.strip()

# 🕵️ Step 3: Remove unwanted characters or HTML remnants
def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"<.*?>", "", text)    # remove HTML tags
    text = re.sub(r"[^\w\s\u0900-\u097F.,-]", "", text)  # keep Marathi, English, punctuation
    return text.strip()

df["scheme_name"] = df["scheme_name"].apply(clean_text)
df["description"] = df["description"].apply(clean_text)

# 🌐 Step 4: Ensure valid URLs in OfficialLink
df["scheme_link"] = df["scheme_link"].apply(lambda x: x if x.startswith("http") else None)
df.dropna(subset=["scheme_link"], inplace=True)

# 🏷 Step 5: Reset index
df.reset_index(drop=True, inplace=True)

# 🆔 Step 6: Add sequential scheme_id column (starting from 1)
df.insert(0, "scheme_id", range(1, len(df) + 1))

# ✅ Save cleaned version
cleaned_path = "preprocessed_Dataset.csv"
df.to_csv(cleaned_path, index=False)

print("✅ Cleaning done. Cleaned file saved as:", cleaned_path)
print(df.head())
