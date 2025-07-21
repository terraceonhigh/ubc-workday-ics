# UBC Workday Excel to ICS CLI Tool

## Installation

Clone this repo:

```
git clone https://github.com/terraceonhigh/ubc-workday-ics.git
```

To install run:

```
python3.XX -m venv venv
```

If on Windows run:

```
.\venv\Scripts\activate
```

If on Linux or Mac run:

```
source venv/bin/activate
```

Finally run

```
pip install -r requirements.txt
```

## Example

This script takes two filenames, the first is the workday excel file and the
second will be name of the .ics file (should end in .ics)

e.g.

1. Navigate to [UBC Workday](myworkday.ubc.ca) and login.
2. Go to the "Academics" section then click the "Registration" tab.
3. Finally click the settings wheel in the "Current Schedule" block and download
   the excel file.
4. Copy and paste it into the cloned directory.
5. Run:

```
python workday_ics.py Current_Schedule.xlsx calendar.ics --reminder 30,10
```

6. I woud reccomend making a new calendar in your calendar software incase this
   does not work. Then upload the ics file to there.

## Options

```
--help
--reminder (comma seperated, minute values for setting reminders)
```
