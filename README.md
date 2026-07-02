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







