#!/usr/bin/env python3
import subprocess
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Whitelisted values for security
ALLOWED_RECORD_TYPES = ['A', 'AAAA', 'MX', 'CNAME', 'TXT', 'NS', 'SOA', 'PTR', 'ANY', 'AXFR']
ALLOWED_DNS_SERVERS = {
    'default': None,
    '8.8.8.8': '8.8.8.8',
    '1.1.1.1': '1.1.1.1',
    '9.9.9.9': '9.9.9.9',
    '208.67.222.222': '208.67.222.222'  # OpenDNS
}

def is_valid_domain(domain):
    """Basic domain/IP validation"""
    # Allow domains, IPs (v4 and v6)
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
    
    return (re.match(domain_pattern, domain) or 
            re.match(ipv4_pattern, domain) or 
            re.match(ipv6_pattern, domain))

def build_dig_command(params):
    """Safely build dig command from parameters"""
    cmd = ['dig']
    
    # DNS server
    server = params.get('server', 'default')
    if server != 'default' and server in ALLOWED_DNS_SERVERS:
        cmd.append(f'@{ALLOWED_DNS_SERVERS[server]}')
    
    # Reverse lookup
    if params.get('reverse', False):
        cmd.append('-x')
    
    # Domain/IP
    domain = params.get('domain', '').strip()
    if not domain:
        raise ValueError('Domain/IP is required')
    if not is_valid_domain(domain):
        raise ValueError('Invalid domain or IP address')
    cmd.append(domain)
    
    # Record types (only if not reverse lookup)
    if not params.get('reverse', False):
        record_types = params.get('recordTypes', ['A'])
        if isinstance(record_types, str):
            record_types = [record_types]
        for rt in record_types:
            if rt.upper() in ALLOWED_RECORD_TYPES:
                cmd.append(rt.upper())
    
    # Options
    if params.get('short', False):
        cmd.append('+short')
    if params.get('trace', False):
        cmd.append('+trace')
    if params.get('tcp', False):
        cmd.append('+tcp')
    if params.get('norecurse', False):
        cmd.append('+norecurse')
    if params.get('stats', False):
        cmd.append('+stats')
    if params.get('dnssec', False):
        cmd.append('+dnssec')
    
    # Section filters
    if params.get('answerOnly', False):
        cmd.extend(['+noall', '+answer'])
    elif params.get('showAuthority', False):
        cmd.extend(['+noall', '+answer', '+authority'])
    elif params.get('showAdditional', False):
        cmd.extend(['+noall', '+answer', '+additional'])
    
    # Buffer size
    bufsize = params.get('bufsize')
    if bufsize and isinstance(bufsize, int) and 512 <= bufsize <= 4096:
        cmd.append(f'+bufsize={bufsize}')
    
    # Timeout (default 5s, max 30s)
    timeout = params.get('timeout', 5)
    if isinstance(timeout, int) and 1 <= timeout <= 30:
        cmd.append(f'+time={timeout}')
    
    # Retries (max 3)
    tries = params.get('tries', 1)
    if isinstance(tries, int) and 1 <= tries <= 3:
        cmd.append(f'+tries={tries}')
    
    return cmd

@app.route('/dig', methods=['POST'])
def run_dig():
    """Execute dig command with parameters"""
    try:
        params = request.get_json()
        if not params:
            return jsonify({'error': 'No parameters provided'}), 400
        
        # Build command
        cmd = build_dig_command(params)
        
        # Execute with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': True,
            'command': ' '.join(cmd),
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Query timed out (30s limit)'}), 408
    except Exception as e:
        return jsonify({'error': f'Failed to execute dig: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
