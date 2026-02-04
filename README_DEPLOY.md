# Deployment Guide for University HR Payroll Demo

This guide will help you deploy your Flask application to the cloud using **Render** (recommended for its ease of use and persistent storage support).

## Prerequisites
1.  A [GitHub](https://github.com/) account.
2.  A [Render](https://render.com/) account.

## Step 1: Push your code to GitHub
1.  Initialize a git repository in your project folder if you haven't already:
    ```bash
    git init
    git add .
    git commit -m "Prepare for deployment"
    ```
2.  Create a new repository on GitHub.
3.  Link your local repo and push:
    ```bash
    git remote add origin YOUR_GITHUB_REPO_URL
    git branch -M main
    git push -u origin main
    ```

## Step 2: Deploy to Render
1.  Log in to [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub repository.
4.  Configure the service:
    *   **Name**: `university-hr-payroll` (or any unique name).
    *   **Environment**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`.
    *   **Start Command**: `gunicorn --chdir app app:app`.
5.  Click **Create Web Service**.

## Step 3: Persistence (CRITICAL for SQLite)
By default, Render's disk is "ephemeral," meaning your database will reset every time the server restarts. To keep your data:
1.  In your Render Service settings, go to the **Disk** tab.
2.  Add a **Disk**:
    *   **Name**: `sqlite-data`.
    *   **Mount Path**: `/etc/data`.
    *   **Size**: `1 GB`.
3.  Go to the **Environment** tab and add an Environment Variable:
    *   **DB_PATH**: `/etc/data/mock_banner.db`.

> [!NOTE]
> If you add the `DB_PATH` variable, ensure your code is updated to read the database path from an environment variable. Currently, the app uses a local file `mock_banner.db`.

## Alternative: PythonAnywhere
1.  Create an account on [PythonAnywhere](https://www.pythonanywhere.com/).
2.  Upload your files or clone from GitHub.
3.  Configure a Web App using the "Manual Configuration" for Flask and Python 3.x.
4.  Update the WSGI configuration file to point to your `app.py`.
