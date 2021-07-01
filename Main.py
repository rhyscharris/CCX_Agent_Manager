import json
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as et
import urllib3

# Variables
grafanaData = {}
connectedtoSandbox = False #Change to True when on VPN
# Add TE Test ID JSON variable here, e.g: testID = "56125.json"
teBaseUrl = "https://api.thousandeyes.com/v6/endpoint-data/tests/net/metrics/"
wbxBaseUrl = "https://api.ciscospark.com/v1/messages"
# Add multiple ID to Email mappings, e.g: agentDataEmail = {"6c36e1988-1m7p-190p-94031jkl513421 : "jobloggs@cisco.com"} and so on.
# Add multilpe ID to Agent Number mappings, e.g.: agentDataBoxID = {"6c36e1988-1m7p-190p-94031jkl513421 : "Agent001"} and so on.
# Add multiple ID to MX port number mappings, e.g.: agentDataMX = {"6c36e1988-1m7p-190p-94031jkl513421 : "001"} and so on.

# Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # dCloud has no cert so this disables a very annoying warning

# Method to retrieve the test results from Thousand Eyes
def getEndpointMetrics(testID):

    headers = {
      'Content-Type': 'application/json',
      # Add TE authorisation key. E.g.: Authorization': 'Basic ipi128u9fjkldj5k31j364909012jlkjvds'
    }

    response = requests.request("GET", teBaseUrl + testID, headers=headers, data={})
    data = json.loads(response.text)
    return data

# Method to update the State of a single agent
def updateCCAgentState(agent, supervisor, new_state):
    # Example way to call is updateCCAgentState('Agent002', 'Agent001', 'NOT_READY')

    ("Attempting to change agent state to: " + new_state + "...") # for debugging

    if getCCAgentState(agent) == new_state:
        #print("You're trying to change it to the state they're already in!")
        return # end the function, do no more (ie don't change state)
    elif getCCAgentState(agent) == "LOGOUT":
        #print("The agent is logged out, what are ya doing?!")
        return # end the function, do no more (ie don't change state)


    headers = {'Content-Type': 'application/xml'}
    xml = ("""<User>
        <id>"""+ agent + """</id>
        <state>""" + new_state + """</state>
        </User>"""
        )
    http_response = requests.put(
        ("https://hq-uccx.abc.inc:8445/finesse/api/User/" + agent), # May need to change this URL if not using Cisco sandbox!
        verify=False,
        headers=headers,
        data=xml,
        auth=HTTPBasicAuth(supervisor, 'ciscopsdt') # hardcoded password. If not using DevNet Sandbox, may need to change.
        )
    #print(http_response)

    # for printing xml returned errors (if applicable)
    if http_response.content: # if there is actually an XML response, do the following
        response_xml = et.fromstring(http_response.content) # requests library doesn't do XML. ET creates a dict so we can read XML
        for child in response_xml.iter('ErrorMessage'): # loop through all XML children that match ErrorMessage
            #print(str(child.tag) + ": " + str(child.text))
            continue

# Method to retrieve the State of a single agent
def getCCAgentState(agent):
    # Example of calling this is getCCAgentState(Agent002)

    #print("Displaying agent state...")

    http_response = requests.get(
        ("https://hq-uccx.abc.inc:8445/finesse/api/User/" + agent), # May need to change this URL if not using Cisco sandbox!
        verify=False, # since dCloud has no cert
        auth=HTTPBasicAuth(agent, 'ciscopsdt') # hardcoded password. If not using DevNet Sandbox, may need to change.
        )

    #print(http_response) # Prints the response code e.g. 400


    # for printing xml returned errors (if applicable)
    if http_response.content: # if there is actually an XML response, do the following
        response_xml = et.fromstring(http_response.content) # requests library doesn't do XML. ET creates a dict so we can read XML
        for child in response_xml.iter('ErrorMessage'): # loop through all XML children that match ErrorMessage
            #print(str(child.tag) + ": " + str(child.text))
            continue
        for child in response_xml.iter('state'): # loop through all XML children that match state
            #print(str(child.tag) + ": " + str(child.text)) # print the text (not tag/content/attribute as common in tutorials)
            current_state = str(child.text)
            return current_state


def getQueueMetrics():
    http_response = requests.get(
        ("https://hq-uccx.abc.inc:8445/realtime/VoiceIAQStats"), # May need to change this URL if not using Cisco sandbox!
        verify=False, # since dCloud has no cert
        )
    data = json.loads(http_response.text)
    return data

def notifyManagers(agent):

    payload = "{\r\n  \"roomId\" : \"AddRoomIDHere\",\r\n  \"" \
              "text\": \r\n    \"CCX agent: " + agentDataEmail[agent] + ". With agentID: " + agentDataBotID[agent] + ". Has a home broadband issue, I have moved them out of the available agent pool to preserve call quality. " \
              "You can check the current CCX metrics here http://localhost:3000/d/EZvGqYEGk/q3-hack?orgId=1&from=now-2d&to=now " \
              "If you would like to enable their LTE failover. Please type: /lte " + agentDataMX[agent] + "\",\r\n  \"markdown\": \r\n      \"" \
              "CCX agent: " + agentDataEmail[agent] + ". With agentID: ```" + agentDataBotID[agent] + "```. Has a home broadband issue, I have moved them out of the available agent pool to preserve call quality. " \
              "You can check the current CCX metrics [here](http://localhost:3000/d/EZvGqYEGk/q3-hack?orgId=1&from=now-2d&to=now). " \
              "If you would like to enable their LTE failover. Please type: ```/lte " + agentDataMX[agent] + "```\"\r\n}" # Add the Room ID and change URLs

    headers = {
        # Add Authorisation key here e.g.: 'Authorization': 'Bearer ipi128u9fjkldj5k31j364909012jlkjvds',
        'Content-Type': 'application/json'
    }

    return requests.request("POST", wbxBaseUrl, headers=headers, data=payload)

def merakiStats():
    # Add your Meraki MX API URL here. E.g.: url = "https://api.meraki.com/api/v1/devices/6NTI-1G12-DJMNP/switch/ports/statuses"
    payload={}
    headers = {
    # Add your Meraki API Key E.g.: 'X-Cisco-Meraki-API-Key': 'ipi128u9fjkldj5k31j364909012jlkjvds',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)

#-----END OF METHODS-----

#Kick off the main process this will be ran by telgraf repeatedly.

#Set threshold values for what we deem to be good metrics
#Recommended numbers by Cisco & Microsoft for audio calls.
lossThreshold = 1.0
latencyThreshold = 200.0
jitterThreshold = 30.0

#Check if any of our active agents violate this
#Parse the  returned JSON and pull out the  LLJ statistics to check for violations
fullResponse = getEndpointMetrics(testID)
violatingAgents = []

for metric in fullResponse["endpointNet"]["metrics"]:
    if metric["loss"] > lossThreshold:
        if metric["agentId"] not in violatingAgents:
            violatingAgents.append(metric["agentId"])
            #print("User " + str(metric["agentId"]) + " has a loss of " + str(metric["loss"]))
        else:
            continue

    if metric["avgLatency"] > latencyThreshold:
        if metric["agentId"] not in violatingAgents:
            violatingAgents.append(metric["agentId"])
            #print("User " + str(metric["agentId"]) + " has a avgLatency of " + str(metric["avgLatency"]))
        else:
            continue

    if metric["jitter"] > jitterThreshold:
        if metric["agentId"] not in violatingAgents:
            violatingAgents.append(metric["agentId"])
            #print("User " + str(metric["agentId"]) + " has a jitter of " + str(metric["jitter"]))
        else:
            continue

#Gather stats for Grafana
#Build a JSON of only the data we wish to send to Grafana

#Gather the TE Metrics for Grafana
for metric in fullResponse["endpointNet"]["metrics"]:
    dataLabel = "user-"
    dataLabel = dataLabel + agentDataEmail[metric["agentId"]]
    grafanaData[dataLabel + "Loss"] = metric["loss"]
    grafanaData[dataLabel + "AvgLatency"] = metric["avgLatency"]
    grafanaData[dataLabel + "Jitter"] = metric["jitter"]

#Gather the CCX Metrics for Grafana
if connectedtoSandbox:
    ccxMetrics = getQueueMetrics()
    grafanaData["agentsLoggedOn"] = ccxMetrics[0]["VoiceIAQStats"]["nResourcesLoggedIn"]
    grafanaData["agentsNotReady"] = ccxMetrics[0]["VoiceIAQStats"]["nUnavailResources"]
    grafanaData["agentsReady"] = ccxMetrics[0]["VoiceIAQStats"]["nAvailResources"]
    grafanaData["callsInQueue"] = ccxMetrics[0]["VoiceIAQStats"]["nWaitingContacts"]
    grafanaData["startTimeOfLongestCallInQueue"] = ccxMetrics[0]["VoiceIAQStats"]["longestCurrentlyWaitingCallStartTime"]
else:
    grafanaData["agentsLoggedOn"] = 4
    grafanaData["agentsNotReady"] = 0
    grafanaData["agentsReady"] = 4
    grafanaData["callsInQueue"] = 5
    grafanaData["startTimeOfLongestCallInQueue"] = 10

#Gather Meraki data for Grafana
portStats = merakiStats()
agentsOnLTE = 0
for port in portStats:
    if 5 <= int(port["portId"]) <= 8:
        if port["enabled"] == False:
            agentsOnLTE = agentsOnLTE + 1
grafanaData["agentsOnLTE"] = agentsOnLTE   
#Automatically take the violating agents our of the queue.
if connectedtoSandbox:
    for agent in violatingAgents:
        updateCCAgentState(agentDataBotID[agent], "Agent001", "NOT_READY")
        #print(agentDataEmail[agent])


#Notify Managers about the violating agents to take action.
if violatingAgents:
    for agent in violatingAgents:
        notifyManagers(str(agent))

#Bot on Sams side will then handle the Meraki LTE state change.

#print("-------------------------BREAK Commencing Grafana DUMP (Remove for Prod)-------------------------\n\n")
#By printing the JSON to the command line this is picked up by Telegraf for any data we wish to display in Grafana
#TESTING - sending the whole TE JSON
#print(fullResponse)
#Demo/Prod - Sending our crafted JSON
grafanaData = json.dumps(grafanaData)
print(grafanaData)
