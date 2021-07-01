# Q3Hack
Q3 Hack for the SE Commercial Team with the hardcoded mappings, API Keys, and passwords removed.

This uses ThousandEyes APIs to monitor Contact Centre Agent's home broadband connections (loss, latency, jitter). If thresholds are hit, they are made not available for calls, and their supervisors are alerted via a Webex bot. Supervisors can then view the data via a URL, and assess whether to send a command into Webex which fails that agent over to 4G.

To set up, git clone the repo to your local environment.

After that, set up the virtual environment by navigating to the Q3Hack directory then run, 'source venv/bin/activate' install the dependencies (haven't made a requirements.txt as of yet!)

Then in Main.py:
* Add the ThousandEyes Test ID JSON to line 10
* Add the ID to Email mappings on line 13
* Add the ID to Agent Number mappings on line 14
* Add the ID to MX port number mappings on line 15
* Add your TE auth key on line 25
* Edit the URL on line 53/75/97 if applicable
* Change the password on line 57/77 if applicable
* Change the Webex Room ID and change URLs in the payload on line 105-111
* Add the Authorisation key on line 114
* Add your Meraki MX API URL on line 121
* Add your Meraki API Key on line 124

Then in cc_bot.py:
* Add Agent ID to Meraki device mappings on line 17
* Add approved user's emails into line 21

The Grafana config and containers must also then be setup, and the bot hosted with an NGROK address. Running the bot includes adding credentials in the .sh file.


## Bot Details:

Access Token: Redacted
Email: ccagent@webex.bot

Will only take action and reply if the configured email addresses message it.
Currently script does not handle re-enabling the MS switch port in the event that the link status raises above the set TE threshold.
