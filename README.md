# fpl-dashboard

Working with Fantasy Premier League API to create a better player statistics view.

This repository contains code to load data from the FPL API into a SQLite Database and visualize and explore it using Dash

## Steps to run the app

1. Clone this repo
2. Navigate to root directory of repo

3. Setup `miniconda` environment from `environment.yml` file by running (requires [`miniconda`](https://docs.conda.io/en/latest/miniconda.html) installation):

    ```{bash}
    conda create -f environment.yml
    ```

4. Run the following to make all modules discoverable:

   ```{bash}
    pip install -e .
   ```

5. Fetch data from FPL API by running:

    ```{bash}
    python3 src/data_extraction/db_handler.py
    ```

6. Run the app:

    ```{bash}
    python3 src/app.py
    ```
