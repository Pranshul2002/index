# Custom US Stock Index Dashboard

## Overview

This project involves the creation of a custom index comprising the top 100 US stocks based on market capitalization. The index is updated daily to maintain equal-weighted contributions from each stock. A dashboard is developed to visualize the index's performance and composition over the past month, highlighting any days with changes in the composition. Additionally, functionality is provided to export both performance and composition data to well-formatted Excel.

## Features

- **Custom Index Construction**: Tracks the top 100 US stocks based on their market capitalization and ensures each stock has an equal nominal contribution to the index.
- **Daily Updates**: The index is updated daily to reflect changes in market capitalization, adjusting the stock weights accordingly.
- **Dashboard Visualization**: A dashboard built with Dash to visualize the performance and composition of the index over the past month.
  - Highlights days with composition changes.
- **Export Functionality**: Allows users to export the index performance and composition data to well-formatted Excel and PDF files.

## Project Structure

├── data/ # Folder containing data-related files 
├── pycache/ # Compiled Python files (auto-generated) 
├── helper.py # Helper functions for data processing 
├── constants.py # Constants used throughout the project 
├── db.py # Database connection and query handling (DuckDB) 
├── index.py # Logic for constructing and updating the custom index 
├── main.py # Main entry point for running the application 
├── requirements.txt # List of Python dependencies 
├── run.ksh # Shell script for running the project 
└── readme.md # This README file


## Dependencies

The following dependencies are required to run the project:

- `dash`: For creating the interactive dashboard.
- `duckdb`: Used as the database for storing stock data and index calculations.
- `pandas`: For data manipulation and processing.

To run the project just run the following command:

```bash
chmod 777 run.ksh; ksh run.ksh
```

## Database

The project uses DuckDB for storing and querying the stock market data and index information. The database is handled in the db.py file, where queries are executed to pull in stock data, calculate the market cap, and update the index.

## Folder and File Descriptions

- data/: Contains any raw or processed data files used in the project.
helper.py: Contains helper functions for processing stock data and managing index calculations.
- constants.py: Stores constants such as API keys, file paths, or configuration settings.
- db.py: Handles database connections, queries, and stores the stock data in DuckDB.
index.py: Implements the logic for constructing and updating the custom index.
- main.py: The entry point for the application, running the Dash server and visualizing the index.
- run.ksh: A shell script for running the project.
- readme.md: This file, providing an overview of the project.
