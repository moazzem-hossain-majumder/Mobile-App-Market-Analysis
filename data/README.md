# Data notes

Two public datasets of real app listings.

googleplaystore.csv is the Google Play Store Apps dataset shared on Kaggle by Lavanya Gupta. It has 10,841 rows and 13 columns: app name, category, rating, reviews, size, installs, type, price, content rating, genres, last updated, current version and Android version. The latest update date in the file is 8 August 2018.

AppleStore.csv is the Apple App Store dataset shared on Kaggle by ramamet4. It has 7,197 rows and 16 columns, including size in bytes, price, rating counts, user rating, age rating, genre, supported devices and languages. It dates from around 2017.

Both files are kept exactly as downloaded, from a public GitHub copy of the two datasets. Check the original Kaggle pages for collection details and licence terms.

clean_data.py holds the cleaning steps. Run it with Python to print the step counts that appear on the Cleaning_Log sheet. The workbook itself contains the raw rows on the Raw sheets and the cleaned rows on the Clean sheets.
