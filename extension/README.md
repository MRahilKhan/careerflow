# CareerFlow Job Capture (Chrome extension)

Save job postings from LinkedIn, Indeed, Glassdoor, or any job site straight into your
CareerFlow pipeline at https://careerflow-liart.vercel.app — no copy-pasting required.

## Install (unpacked, for now)

1. Open `chrome://extensions`.
2. Turn on **Developer mode** (top right).
3. Click **Load unpacked** and select this `extension/` folder.
4. Pin the CareerFlow icon to your toolbar for one-click access.

## Use it

1. Click the extension icon and log in with your CareerFlow account (same email/password
   as the website — no separate signup needed).
2. Open a job posting. Click the icon again: it auto-fills role, company, location, work
   mode, and salary when it can detect them (LinkedIn, Indeed, and Glassdoor have dedicated
   parsing; other sites get a best-effort guess from the page title).
3. Review/edit the fields, pick a status, and hit **Save to CareerFlow**.
4. Optional: leave **"Automatically save when I submit an application"** on, and the
   extension will detect Apply-button submissions on any site and save the job for you —
   you'll get a small confirmation toast in the corner of the page.

Duplicate job URLs are skipped automatically so re-visiting a posting won't create a
second entry.

## Privacy

The extension stores only your short-lived CareerFlow access token in Chrome's local
extension storage. It never stores your password. Job details are only read from the
page you're actively viewing when you open the popup, or right when an application form
is submitted.

## Publishing to the Chrome Web Store

This is currently load-as-unpacked only. To ship it to real users:

1. Zip the contents of this folder (not the folder itself).
2. Create a one-time $5 developer account at
   https://chrome.google.com/webstore/devconsole.
3. Upload the zip, add a description/screenshots, and submit for review
   (usually a few days).
