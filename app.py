from flask import Flask, jsonify, request
from config import Config
from soap_client import WorkdaySOAPClient

app = Flask(__name__)
app.config['DEBUG'] = True  # For development; disable in production

# Initialize the Workday SOAP client with credentials and WSDL URL from config
soap_client = WorkdaySOAPClient(
    wsdl_url=Config.WORKDAY_WSDL,
    username=Config.WORKDAY_USERNAME,
    password=Config.WORKDAY_PASSWORD,
    tenant=Config.WORKDAY_TENANT  # Not used for authentication in this option
)

@app.route('/', methods=['GET'])
def index():
    """Welcome message at the root endpoint."""
    return jsonify({
        "message": "Welcome to the Workday REST API Wrapper.",
        "endpoints": {
            "health": "/health",
            "get_workers": "/get_workers"
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "OK", "message": "Workday REST wrapper is running"}), 200

@app.route('/get_workers', methods=['GET'])
def get_workers():
    """REST endpoint to retrieve a list of workers."""
    try:
        workers_data = soap_client.get_workers()
        return jsonify({"workers": workers_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Custom error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

