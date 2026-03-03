"""
Simple HTTP API for AI agents to connect to Biological Chaos
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from src.main import AgentServer


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for agent API"""
    
    server = None
    
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            state = self.server.get_state()
            self.wfile.write(json.dumps({
                'status': 'running',
                'generation': state['generation'],
                'population': state['population'],
                'alive': state['alive']
            }).encode())
            
        elif self.path == '/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            state = self.server.get_state()
            self.wfile.write(json.dumps(state).encode())
            
        elif self.path.startswith('/agent/'):
            agent_id = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            perception = self.server.agent_see(agent_id)
            self.wfile.write(json.dumps(perception).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        if self.path == '/agent/register':
            data = json.loads(body) if body else {}
            agent_id = data.get('agent_id', f'agent_{id(self)}')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            result = self.server.register_agent(agent_id)
            self.wfile.write(json.dumps(result).encode())
            
        elif self.path.startswith('/agent/'):
            parts = self.path.split('/')
            agent_id = parts[2]
            action = parts[3] if len(parts) > 3 else 'act'
            
            if action == 'act' and body:
                act_data = json.loads(body)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                result = self.server.agent_act(agent_id, act_data)
                self.wfile.write(json.dumps(result).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[API] {args[0]}")


def start_api_server(server: AgentServer, port=8080):
    """Start HTTP API server"""
    APIHandler.server = server
    
    httpd = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🌐 API server running on http://localhost:{port}")
    httpforever()


# Exampled.serve_ agent connection
def example_agent(agent_id: str, server_url: str = "http://localhost:8080"):
    """
    Example AI agent connecting to the simulation
    """
    import requests
    
    # Register
    resp = requests.post(f"{server_url}/agent/register", json={'agent_id': agent_id})
    if not resp.json().get('success'):
        print(f"Failed to register: {resp.json()}")
        return
    
    print(f"Registered as {agent_id}")
    
    # Main loop
    while True:
        # See what the agent perceives
        perception = requests.get(f"{server_url}/agent/{agent_id}/see").json()
        
        if 'error' in perception:
            print(f"Error: {perception['error']}")
            break
        
        # Make decision
        nearby_food = perception.get('nearby        nearby_threats = perception.get_food', [])
('nearby_threats', [])
        
        thrust = (0, 0)
        contract = 0.0
        
        # Hunt food
        if nearby_food:
            nearest = min(nearby_food, key=lambda f: f['distance'])
            pos = perception['position']
            thrust = (
                (nearest['x'] - pos['x']) / max(1, nearest['distance']),
                (nearest['y'] - pos['y']) / max(1, nearest['distance'])
            )
            
            if nearest['distance'] < 3:
                contract = 1.0
        
        # Avoid threats
        elif nearby_threats:
            nearest = min(nearby_threats, key=lambda t: t['distance'])
            pos = perception['position']
            thrust = (
                -(nearest['x'] - pos['x']) / max(1, nearest['distance']),
                -(nearest['y'] - pos['y']) / max(1, nearest['distance'])
            )
        
        # Send action
        requests.post(
            f"{server_url}/agent/{agent_id}/act",
            json={'thrust': thrust, 'contract': contract}
        )


if __name__ == "__main__":
    # Run with: python -m src.api
    # Then connect agents from other processes
    
    # Start simulation
    server = AgentServer()
    server.evolution.generation_time = 30  # 30 seconds per generation
    
    # Start API in background
    api_thread = threading.Thread(target=start_api_server, args=(server, 8080), daemon=True)
    api_thread.start()
    
    # Run simulation
    server.start()
