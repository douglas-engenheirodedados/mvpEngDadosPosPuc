# mvpEngDadosPosPuc
Projeto MVP de Engenharia de Dados para o curso de Pós Graduação de Ciência de Dados e Advanced Analytics da PUC - RJ. 

# Data Engineering MVP for Cryptocurrency Crawler

## Overview
This project is a Minimum Viable Product (MVP) for a data engineering pipeline focused on collecting and processing cryptocurrency data. The main component of the project is a web crawler that fetches data from various cryptocurrency sources, cleans it, and stores it for further analysis.

## Project Structure
```
data-engineering-mvp
├── .venv                  # Virtual environment for Python dependencies
├── src                    # Source code for the project
│   ├── crawler            # Crawler module
│   │   └── main.py       # Main logic for the crawler
│   └── utils             # Utility functions
│       └── helpers.py    # Helper functions for data processing
├── data                   # Data storage
│   ├── raw               # Raw data collected by the crawler
│   └── processed         # Processed data ready for analysis
├── notebooks              # Jupyter notebooks for analysis
│   └── analysis.ipynb    # Data analysis and visualization notebook
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
└── .gitignore             # Git ignore file
```

## Setup Instructions
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd data-engineering-mvp
   ```

2. **Create a virtual environment:**
   ```
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage Guidelines
- To run the crawler, execute the `main.py` file located in the `src/crawler` directory.
- Use the Jupyter notebook in the `notebooks` directory for data analysis and visualization.
- Store raw data in the `data/raw` directory and processed data in the `data/processed` directory.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License.