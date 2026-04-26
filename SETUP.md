# OutreachOS Setup Guide

To run OutreachOS, you need two free API keys. Follow these steps:

## 1. Get a YouTube Data API Key (Free)
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  **Create a Project:** Click the project dropdown at the top and select "New Project". Name it `OutreachOS`.
3.  **Enable API:** In the search bar at the top, type **"YouTube Data API v3"** and click on it. Click **Enable**.
4.  **Create Credentials:**
    *   Go to the **Credentials** tab on the left sidebar.
    *   Click **+ CREATE CREDENTIALS** -> **API key**.
    *   Copy the key that appears.

## 2. Get a Gemini API Key (Free)
1.  Go to [Google AI Studio](https://aistudio.google.com/).
2.  Sign in with your Google account.
3.  On the left sidebar, click **"Get API key"**.
4.  Click **"Create API key in new project"**.
5.  Copy the generated key.

## 3. Configure the Project
1.  In your `OutreachOS` folder, you will see a file named `.env.example`.
2.  **Rename** it to simply `.env` (or create a new file named `.env`).
3.  Paste your keys into the file like this:

```env
YOUTUBE_API_KEY=AIzaSy... (your youtube key)
GEMINI_API_KEY=AIzaSy... (your gemini key)
```

## 4. Run the System
Open your terminal in the `OutreachOS` folder and run:
```powershell
python -m OutreachOS.main "CBSE math tricks"
```
