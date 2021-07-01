import os
import requests
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response
import sys
import json
import meraki
import re
import Main as main

bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

# Agent ID to Meraki device mapping
# Add these in. E.g.: agent_dict={"001":['seri-alnu-mber','5'],"002":['seri-alnu-mber','6'],"003":['seri-alnu-mber','7'],"004":['','8']}

# Email addresses that the bot will action on messages from, and reply to
approved_users = [
    # Add what emails should be able to message the bot. Others will be ignored.
]

# If any of the bot environment variables are missing, terminate the app
if not bot_email or not teams_token or not bot_url or not bot_app_name:
    print(
        "Missing Environment Variable. Please see the 'Usage' section in the README."
    )
    if not bot_email:
        print("TEAMS_BOT_EMAIL")
    if not teams_token:
        print("TEAMS_BOT_TOKEN")
    if not bot_url:
        print("TEAMS_BOT_URL")
    if not bot_app_name:
        print("TEAMS_BOT_APP_NAME")
    sys.exit()

dashboard = meraki.DashboardAPI()

bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
    approved_users=approved_users,
    webhook_resource_event=[
        {"resource": "messages", "event": "created"},
    ],
)

# A command that returns a string that's sent as a reply
def lte(incoming_msg):
    agent_id = re.sub(r'.*lte\ ', '',incoming_msg.text)
    serial = agent_dict[agent_id][0]
    port_id = agent_dict[agent_id][1]
    message = switch_lte(serial,port_id,agent_id)
    main.updateCCAgentState(f'Agent{agent_id}', "Agent001", "READY")
    return message

def switch_lte(serial,port_id,agent_id):
    response = dashboard.switch.updateDeviceSwitchPort(serial,port_id,enabled=False)
    if response['enabled']==False:
        message = f"LTE Failover Process Started for Agent {agent_id}"
    return message

bot.add_command("/lte", "Switch an agent to LTE", lte)

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=5000)