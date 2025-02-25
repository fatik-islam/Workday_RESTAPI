from flask import Flask, jsonify, request
from config import Config
from soap_client import WorkdaySOAPClient
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import xmltodict
import json

app = Flask(__name__)
app.config['DEBUG'] = True

# Configure JWT settings.
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_IDENTITY_CLAIM'] = 'identity'
jwt = JWTManager(app)

def transform_xml_dict(d):
    """
    Recursively transforms an XML dict produced by xmltodict:
      - Renames keys starting with '@' by removing the '@'
      - Renames '#text' to '_value_1'
    """
    if isinstance(d, dict):
        new_dict = {}
        for key, value in d.items():
            if key.startswith('@'):
                new_key = key[1:]
            elif key == '#text':
                new_key = '_value_1'
            else:
                new_key = key
            new_dict[new_key] = transform_xml_dict(value)
        return new_dict
    elif isinstance(d, list):
        return [transform_xml_dict(item) for item in d]
    else:
        return d

def parse_request_data():
    """
    Parses incoming request data based on the Content-Type header.
    If XML is provided, converts it to a Python dict, extracts the inner object
    (if present, e.g., GetWorkersRequest), and transforms keys.
    Returns a Python dictionary.
    """
    if request.content_type and ('xml' in request.content_type):
        try:
            data = xmltodict.parse(request.data)
            if "GetWorkersRequest" in data:
                data = data["GetWorkersRequest"]
            return transform_xml_dict(data)
        except Exception as e:
            raise Exception(f"Failed to parse XML: {str(e)}")
    else:
        return request.get_json()

def clean_empty(d):
    """
    Recursively removes dictionary keys with empty dict or empty list values.
    """
    if isinstance(d, dict):
        return {k: clean_empty(v) for k, v in d.items() if v not in [None, {}, []]}
    elif isinstance(d, list):
        return [clean_empty(item) for item in d if item not in [None, {}, []]]
    else:
        return d

def get_soap_client_from_token():
    """
    Creates and returns a new SOAP client using credentials stored in the JWT token.
    """
    identity = get_jwt_identity()  # Expected to be a dict with "username" and "password"
    return WorkdaySOAPClient(
        wsdl_url=Config.WORKDAY_WSDL,
        username=identity.get("username"),
        password=identity.get("password"),
        tenant=Config.WORKDAY_TENANT
    )

@app.route('/', methods=['GET'])
def index():
    """Welcome message with available endpoints."""
    return jsonify({
        "message": "Welcome to the Workday REST API Wrapper.",
        "endpoints": {
            "login": "/login (POST) - supports JSON or XML",
            "health": "/health (GET)",
            "get_workers": "/get_workers (POST) - filtering parameters in JSON or XML",
            "get_worker": "/get_worker/<worker_id> (GET)"
        }
    }), 200

@app.route('/login', methods=['POST'])
def login():
    """
    POST endpoint for login.
    Expects credentials in JSON or XML format with 'username' and 'password'.
    If valid, returns a JWT token containing the provided credentials.
    """
    try:
        data = parse_request_data()
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"msg": "Username and password required"}), 400

    try:
        temp_client = WorkdaySOAPClient(
            wsdl_url=Config.WORKDAY_WSDL,
            username=username,
            password=password,
            tenant=Config.WORKDAY_TENANT
        )
        # Validate credentials by attempting a simple call with an empty filter.
        temp_client.get_workers({})
    except Exception as e:
        return jsonify({"msg": "Invalid Workday credentials", "error": str(e)}), 401

    identity = {"username": username, "password": password}
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token), 200

@app.route('/health', methods=['GET'])
@jwt_required()
def health_check():
    """Protected health check endpoint."""
    current_identity = get_jwt_identity()
    return jsonify({
        "status": "OK",
        "message": "Workday REST wrapper is running",
        "credentials_used": current_identity  # For debugging; remove in production.
    }), 200

@app.route('/get_workers', methods=['POST'])
@jwt_required()
def get_workers():
    """
    Protected endpoint to retrieve workers.
    Accepts filtering parameters in JSON or XML that mirror the full SOAP XML structure.
    To retrieve all workers, send an empty body ({} in JSON or an empty <GetWorkersRequest/> in XML).
    """
    try:
        filters = parse_request_data() or {}
        filters = clean_empty(filters)  # Remove any empty keys that might cause issues.
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    try:
        soap_client = get_soap_client_from_token()
        workers_data = soap_client.get_workers(filters)
        return jsonify({"workers": workers_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_worker/<string:worker_id>', methods=['GET'])
@jwt_required()
def get_worker(worker_id):
    """
    Protected endpoint to retrieve a single worker by Employee_ID.
    """
    try:
        soap_client = get_soap_client_from_token()
        worker_data = soap_client.get_worker_by_reference(worker_id)
        return jsonify({"worker": worker_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
