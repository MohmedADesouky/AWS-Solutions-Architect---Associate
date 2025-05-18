import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import paho.mqtt.client as mqtt
import threading
import json
import boto3
from botocore.exceptions import ClientError

# DynamoDB Setup
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MachineStackLights')  # Your DynamoDB table name

# MQTT Setup
MQTT_BROKER = "18.185.31.17"
mqtt_data = {
    "factory0": {
        "line0": {
            "machine0": {"status": "Running", "temperature": 25, "pressure": 100},
            "machine1": {"status": "Idle", "temperature": 23, "pressure": 98},
            "machine2": {"status": "Running", "temperature": 26, "pressure": 102},
        },
        "line1": {
            "machine0": {"status": "Running", "temperature": 24, "pressure": 99},
            "machine1": {"status": "Maintenance", "temperature": 22, "pressure": 97},
            "machine2": {"status": "Running", "temperature": 25, "pressure": 101},
        },
    },
    "factory1": {
        "line0": {
            "machine0": {"status": "Running", "temperature": 25, "pressure": 100},
            "machine1": {"status": "Idle", "temperature": 23, "pressure": 98},
            "machine2": {"status": "Running", "temperature": 26, "pressure": 102},
        },
        "line1": {
            "machine0": {"status": "Running", "temperature": 24, "pressure": 99},
            "machine1": {"status": "Maintenance", "temperature": 22, "pressure": 97},
            "machine2": {"status": "Running", "temperature": 25, "pressure": 101},
        },
    },
    "OPC": {
        "stack_light": {"red": True, "yellow": False},
    },
}

# Callback function for MQTT messages
def on_message(client, userdata, msg):
    try:
        message = json.loads(msg.payload.decode())
        factory = message.get("factory", "Unknown Factory")
        line = message.get("line", "Unknown Line")
        machine_id = message.get("machineId", "Unknown Machine")
        status = message.get("status", "Unknown Status")
        temperature = message.get("measurements", {}).get("temperature", "N/A")
        pressure = message.get("measurements", {}).get("pressure", "N/A")
        stack_light = message.get("stack_light", "N/A")
        
        # Update the data structure
        if factory in mqtt_data:
            if line in mqtt_data[factory]:
                if machine_id in mqtt_data[factory][line]:
                    mqtt_data[factory][line][machine_id] = {
                        "status": status,
                        "temperature": temperature,
                        "pressure": pressure,
                        "stack_light": stack_light,
                    }

    except Exception as e:
        print(f"Error decoding message: {e}")

def start_mqtt_client():
    """Start the MQTT client to listen for messages."""
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.subscribe("#")  # Subscribe to all topics
    client.loop_start()

# Start MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt_client)
mqtt_thread.daemon = True
mqtt_thread.start()

# Dash App
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H1("Factory Hierarchy Visualization", style={"textAlign": "center", "color": "#2e3d49"}),
        dcc.Interval(id="interval-component", interval=5000, n_intervals=0),
        html.Div(id="mqtt-visualization", style={"marginTop": "20px"}),
    ]
)

def get_stack_light_status(machine_id):
    """Fetch stack light status from DynamoDB for the latest item"""
    try:
        response = table.query(
            KeyConditionExpression="machineId = :machineId",
            ExpressionAttributeValues={":machineId": machine_id},
            ScanIndexForward=False,  # Ensure we get the latest item
            Limit=1  # Only get the most recent item
        )
        
        if response['Items']:
            item = response['Items'][0]
            return {
                "L1_state": item.get("L1_state", False),
                "L2_state": item.get("L2_state", False),
                "L3_state": item.get("L3_state", 0),  # Assuming it's 0 or 1
            }
        else:
            return {"L1_state": False, "L2_state": False, "L3_state": 0}
    except ClientError as e:
        print(f"Error fetching stack light status: {e}")
        return {"L1_state": False, "L2_state": False, "L3_state": 0}

def get_status_color(status):
    """Helper function to assign color based on machine status"""
    if status.lower() == "running":
        return "#4CAF50"  # Green
    elif status.lower() == "idle":
        return "#FFC107"  # Yellow
    elif status.lower() == "maintenance":
        return "#F44336"  # Red
    else:
        return "#9E9E9E"  # Gray

def machine_card(machine_data, machine_id):
    """Generate the layout for machine card"""
    status_color = get_status_color(machine_data['status'])
    return html.Div(
        [
            html.H4(f"Machine {machine_id}", style={"marginBottom": "5px", "color": "#4f5b66"}),
            html.P(f"Status: {machine_data['status']}", 
                  style={"color": status_color, "fontWeight": "bold"}),
            html.P(f"Temp: {machine_data['temperature']}°C", 
                  style={"color": "#ff7f50"}),
            html.P(f"Pressure: {machine_data['pressure']} bar", 
                  style={"color": "#f39c12"}),
        ],
        style={
            "border": "1px solid #ccc",
            "borderRadius": "5px",
            "padding": "10px",
            "margin": "5px",
            "width": "150px",
            "textAlign": "center",
            "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
            "backgroundColor": "#f9fafb",
        },
    )

def opc_card():
    """Generate the layout for OPC card showing stack light status"""
    stack_light_data = get_stack_light_status("machine_4")

    return html.Div(
        [
            html.H4("OPC Machine", style={"marginBottom": "10px", "color": "#4f5b66"}),
            html.Div(
                [
                    # L1 Stack Light (Red)
                    html.Div(
                        style={
                            "width": "20px",
                            "height": "20px",
                            "borderRadius": "50%",
                            "backgroundColor": "#ff0000" if stack_light_data['L1_state'] else "#ffcccc",
                            "margin": "0 5px",
                            "boxShadow": "0 0 10px rgba(255,0,0,0.5)" if stack_light_data['L1_state'] else "none"
                        }
                    ),
                    # L2 Stack Light (Yellow)
                    html.Div(
                        style={
                            "width": "20px",
                            "height": "20px",
                            "borderRadius": "50%",
                            "backgroundColor": "#ffff00" if stack_light_data['L2_state'] else "#ffffcc",
                            "margin": "0 5px",
                            "boxShadow": "0 0 10px rgba(255,255,0,0.5)" if stack_light_data['L2_state'] else "none"
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginTop": "10px"
                },
            ),
        ],
        style={
            "border": "1px solid #ccc",
            "borderRadius": "5px",
            "padding": "10px",
            "margin": "5px",
            "width": "150px",
            "textAlign": "center",
            "boxShadow": "2px 2px 5px rgba(0,0,0,0.1)",
            "backgroundColor": "#f9fafb",
        },
    )

@app.callback(
    Output("mqtt-visualization", "children"),
    [Input("interval-component", "n_intervals")],
)
def update_visualization(n):
    factory_containers = []
    for factory_id, factory_data in mqtt_data.items():
        if factory_id == "OPC":
            continue
        line_containers = []
        for line_id, line_data in factory_data.items():
            machine_cards = [
                machine_card(machine_data, machine_id)
                for machine_id, machine_data in line_data.items()
            ]
            line_containers.append(
                html.Div(
                    [
                        html.H3(f"Line {line_id[-1]}", style={"color": "#2e3d49"}),
                        html.Div(
                            machine_cards,
                            style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-evenly"},
                        ),
                    ],
                    style={
                        "border": "1px solid #aaa",
                        "padding": "10px",
                        "marginBottom": "10px",
                        "backgroundColor": "#e4e9f2",
                        "borderRadius": "5px"
                    },
                )
            )
        factory_containers.append(
            html.Div(
                [
                    html.H2(f"Factory {factory_id[-1]}", style={"color": "#2e3d49"}),
                    html.Div(line_containers),
                ],
                style={
                    "border": "2px solid #007bff",
                    "padding": "15px",
                    "marginBottom": "20px",
                    "backgroundColor": "#e7f4ff",
                    "borderRadius": "8px"
                },
            )
        )

    # Add OPC card in its own container
    opc_container = html.Div(
        [
            html.H3("OPC Status", style={"color": "#2e3d49"}),
            opc_card()
        ],
        style={
            "border": "1px solid #aaa",
            "padding": "10px",
            "marginTop": "20px",
            "backgroundColor": "#e4e9f2",
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "borderRadius": "5px"
        }
    )

    return html.Div(factory_containers + [opc_container])

if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)