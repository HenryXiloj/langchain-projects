# Google Safe Browsing API Key Setup

This project uses `GOOGLE_SAFE_BROWSING_API_KEY` to check whether a scanned website appears on Google's malware, phishing, or unwanted software threat lists.

Without this key, the app cannot complete the malware/phishing blacklist check.

## Cost

Google Safe Browsing API is free for appropriate non-commercial use, but it has quotas and usage rules.

Official docs:

- https://developers.google.com/safe-browsing/v4/get-started
- https://developers.google.com/safe-browsing/v4/pricing
- https://developers.google.com/safe-browsing/reference/Appropriate.Usage

For commercial or high-volume malicious URL detection, Google recommends Web Risk instead of Safe Browsing.

## Create The Key

1. Open Google Cloud Console:

   https://console.cloud.google.com/

2. Select your project.

   Example: `Default Gemini Project`

3. Go to:

   `APIs & Services` -> `Library`

4. Search for:

   ```text
   Safe Browsing API
   ```

5. Click the card named:

   ```text
   Safe Browsing API
   ```

   Do not choose:

   ```text
   Safe Browsing API (Legacy)
   BeyondCorp API
   ```

6. Click `Enable`.

7. Go to:

   `APIs & Services` -> `Credentials`

8. Click:

   `Create credentials` -> `API key`

9. In the key creation screen:

   - Name: `Safe Browsing API Key`
   - API restrictions: select `Safe Browsing API`
   - Service account authentication: leave unchecked
   - Application restrictions for local development: `None`

10. Click `Create`.

11. Copy the generated key.

## Add It To The Project

Open `.env` in the project root and set:

```env
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key_here
```

Your full `.env` should look like this:

```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-5-mini
GOOGLE_SAFE_BROWSING_API_KEY=your_google_safe_browsing_key_here
```

Restart the server after changing `.env`:

```bash
uv run uvicorn security_checker.main:app --reload
```

## Recommended Security

For local development, `Application restrictions: None` is acceptable.

For production, restrict the key:

- Choose `IP addresses` if the app runs from a fixed server.
- Add only your production server IP address.
- Keep API restrictions set to `Safe Browsing API`.

Do not put this key in frontend JavaScript. Keep it only in `.env` on the backend server.
