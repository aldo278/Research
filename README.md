# Research

This project aims to extract risk factors from 10-K filings of public companies.

### Setup
There are several scripts here that are used to extract risk factors from 10-K filings of public companies.
Edit the companies.csv file to add the companies you want to extract risk factors from.
The scripts will do everything for you, including downloading the 10-K filings organizing the folder structure, and extracting the risk factors.

This will go over the order in which to run the scripts.

Run `npm install requirements.txt` to install the dependencies.

### Order of execution

1. Run `python downloader.py` to download the 10-K filings.
2. Run `python organizer.py` to organize the downloaded files.
3. Run `python metadata.py` to get metadata and store them as json
4. Run `python convert.py` to convert all the txt files to html for readibility

## Notes
- A script using beautiful soup was created to extract the 1A risk factors. It failed for some companies and it also seems to extracting too much text.
- Might have to manually extract the 1A sections and store them in a txt file

After manual extraction, I discovered that the reason the scripts were not working is because the structure of the 10-K filings is not consistent across all companies.
- Some companies include '1A' in their heading while others don't
- Some companies do not have the '1B' Section right after the 1A section the script could not find where the 1A section began, and had a much harder time finding where it ended


### Basic Stats and AI Mentions
Identify how many times AI is mentioned in the 1A section for each company. Identify whether there was an increase in the number of times AI was mentioned as the year progressed. Add the following columns to the metadata.json file:
- ai_mentions: number of times AI is mentioned in the 1A section
- ai_mentions_increase: difference between current year and last years number of AI mentions (first year will be 0)
- words_in_1a: number of words in the 1A section


### Dataset
added a "section" field to the metadata. Removed the "AI_mention_increase" from metadata.
Created script to create one large master dataset.
- The section for the Deere and Co corporation did not return the correct industry so I manually corrected it, only 3 fields








