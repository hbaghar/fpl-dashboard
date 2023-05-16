# fpl-dashboard

Working with Fantasy Premier League API to create a better player statistics view.

This repository contains code to load data from the FPL API into a SQLite Database and visualize and explore it using Dash

The app is live at: https://fpl-dashboard.onrender.com
## Steps to run the app locally

1. Clone this repo
2. Navigate to root directory of repo
3. Run the following

   ```{bash}
    pip install -r requirements.txt && pip install -e .
   ```

4. Run the app:
    ```{bash}
    gunicorn --chdir src app:server
    ```
