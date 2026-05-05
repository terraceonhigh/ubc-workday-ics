# UBC Workday → ICS

Convert your UBC Workday class schedule into an `.ics` file you can import into Apple Calendar, Google Calendar, Proton Calendar, Outlook, or any other iCalendar-compatible app.

Two ways to use it:

- **Web app (no install):** [https://terraceonhigh.github.io/ubc-workday-ics/](https://terraceonhigh.github.io/ubc-workday-ics/) — drag in your Workday Excel, get back an `.ics`. Everything runs in your browser; your schedule never leaves your computer.
- **Command line (Python):** see below.

## Getting your Workday schedule file

1. Go to [myworkday.ubc.ca](https://myworkday.ubc.ca) and log in.
2. Open the **Academics** section, then the **Registration & Courses** tab.
3. In the **Current Schedule** block, click the settings wheel and download the Excel file (`Current_Schedule.xlsx`).

Once you have that file, use either the web app above or the CLI below.

## Web app

Visit [the page](https://terraceonhigh.github.io/ubc-workday-ics/), drop your `.xlsx` in, optionally add reminder times (e.g. `10,30` for 10 and 30 minutes before each class), and click **Convert**. A `.ics` file downloads. Import it into your calendar.

> Tip: import into a *new* calendar in your calendar app, not your main one. That way if anything looks wrong, you can delete the whole calendar in one click.

## Command line

Clone the repo and set up a virtual environment:

```
git clone https://github.com/terraceonhigh/ubc-workday-ics.git
cd ubc-workday-ics
python3 -m venv venv
```

Activate the virtual environment.

On Windows:

```
.\venv\Scripts\activate
```

On macOS or Linux:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run:

```
python workday_ics.py Current_Schedule.xlsx calendar.ics --reminder 30,10
```

### Options

```
--help                    show help
--reminder MINUTES,...    comma-separated reminder times in minutes before each event
--author NAME             calendar PRODID (defaults to "DEFAULT")
```

### Troubleshooting

If `pip install` complains about NumPy failing to build with a Meson / `c++` not found error, install a C++ compiler (e.g. `build-essential` on Debian/Ubuntu, Xcode command-line tools on macOS) and retry. See [this comment](https://github.com/grpc/grpc/issues/24556#issuecomment-727745067) for the original fix.

## License

Copyright © 2026 Chayce Ross and contributors.

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License version 3 or any later version** as published by the Free Software Foundation. See [LICENSE](LICENSE) for the full text. This program is distributed without any warranty.

Not affiliated with the University of British Columbia.

## For maintainers: enabling GitHub Pages

The web app is served straight from the repo root (`index.html` + `workday_ics.py`). To enable it on a fork:

1. Go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to *Deploy from a branch*.
3. Choose branch **`master`** and folder **`/ (root)`**, then **Save**.
4. Wait ~1 minute, then visit `https://<your-username>.github.io/ubc-workday-ics/`.

The empty `.nojekyll` file in the repo tells GitHub Pages to skip Jekyll processing.
