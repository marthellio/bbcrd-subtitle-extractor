# What this script is for

This script is designed to programatically retrieve subtitles from the PIP Inspector API, requiring only the episode PID as an input. The majority of subtitles are stored in a consistent location, however where the file system varies, this script may not work.

This has been roughly put together and feedback is very welcome.

# How to run

To run on an individual PID and have the subtitles printed to your terminal, run the following command:
```
python3 extract_subtitle_xml.py --pid \<insert PID here\>
```

Alternatively, to run on many PIDs at once, create a csv file with the PIDs in column A with the header 'episode'. Then run:
```
python3 extract_subtitle_xml.py --file \<input CSV file here\>
```
This will create a JSON file named 'output.csv' containing the PIDs and their associated subtitles.


