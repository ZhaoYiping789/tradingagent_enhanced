#!/usr/bin/env python3
"""
TradingAgents Enterprise Edition - Web UI
Real-time monitoring interface for WatsonX trading analysis
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import queue
import sys
import os
from datetime import datetime
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tradingagents-watsonx-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
analysis_running = False
analysis_thread = None
log_queue = queue.Queue()
current_status = {
    'stage': 'Idle',
    'progress': 0,
    'ticker': '',
    'start_time': None,
    'decision': None,
    'confidence': None
}


class WebUILogger:
    """Custom logger that emits to web UI"""
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.log_file = None

    def write(self, text):
        # Write to original stdout
        self.original_stdout.write(text)
        self.original_stdout.flush()

        # Emit to web UI
        if text.strip():
            socketio.emit('log', {'message': text}, namespace='/')

        # Write to log file
        if self.log_file:
            self.log_file.write(text)
            self.log_file.flush()

    def flush(self):
        self.original_stdout.flush()
        if self.log_file:
            self.log_file.flush()


def run_analysis_thread(ticker, analysis_date):
    """Run analysis in background thread"""
    global analysis_running, current_status

    try:
        start_time = datetime.now()
        current_status['stage'] = 'Initializing'
        current_status['progress'] = 5
        current_status['ticker'] = ticker
        current_status['start_time'] = start_time.isoformat()
        socketio.emit('status', current_status, namespace='/')

        # Import here to avoid circular imports
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # Set WatsonX credentials
        watsonx_api_key = os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "1NlP-L5h1DDEZFKkvJ92uTuMFNbkk0pmGJ4lMutJ44w2"
        watsonx_project_id = os.getenv("WATSONX_PROJECT_ID") or "394811a9-3e1c-4b80-8031-3fda71e6dce1"
        watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "dummy-key-for-testing"

        # Create config
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "watsonx"
        config["watsonx_url"] = watsonx_url
        config["watsonx_project_id"] = watsonx_project_id
        config["watsonx_api_key"] = watsonx_api_key
        config["deep_think_llm"] = "meta-llama/llama-3-3-70b-instruct"
        config["quick_think_llm"] = "ibm/granite-3-3-8b-instruct"
        config["max_tokens"] = 32768
        config["temperature"] = 0.7
        config["max_debate_rounds"] = 2
        config["max_risk_discuss_rounds"] = 2
        config["online_tools"] = True
        config["lightweight_quantitative"] = False
        config["enterprise_mode"] = True
        config["use_comprehensive_quantitative"] = True
        config["include_optimization_results"] = True

        selected_analysts = [
            "market",
            "social",
            "news",
            "fundamentals",
            "comprehensive_quantitative",
            "portfolio",
            "enterprise_strategy"
        ]

        current_status['stage'] = 'Loading Analysts'
        current_status['progress'] = 10
        socketio.emit('status', current_status, namespace='/')

        # Initialize TradingAgents
        ta = TradingAgentsGraph(
            selected_analysts=selected_analysts,
            debug=True,
            config=config
        )

        current_status['stage'] = 'Running Analysis'
        current_status['progress'] = 20
        socketio.emit('status', current_status, namespace='/')

        # Run analysis
        final_state, decision = ta.propagate(ticker, analysis_date)

        current_status['stage'] = 'Completed'
        current_status['progress'] = 100
        current_status['decision'] = decision
        current_status['confidence'] = final_state.get('decision_confidence', 'Medium')
        socketio.emit('status', current_status, namespace='/')

        # Get result paths
        results_dir = f"results/{ticker}/{analysis_date}"
        socketio.emit('complete', {
            'decision': decision,
            'confidence': current_status['confidence'],
            'results_dir': results_dir,
            'elapsed_time': (datetime.now() - start_time).total_seconds()
        }, namespace='/')

    except Exception as e:
        current_status['stage'] = 'Error'
        current_status['progress'] = 0
        socketio.emit('error', {'message': str(e)}, namespace='/')
        import traceback
        traceback.print_exc()
    finally:
        analysis_running = False


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_analysis():
    """Start analysis"""
    global analysis_running, analysis_thread

    if analysis_running:
        return jsonify({'error': 'Analysis already running'}), 400

    data = request.json
    ticker = data.get('ticker', 'NVDA')
    analysis_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    analysis_running = True
    analysis_thread = threading.Thread(
        target=run_analysis_thread,
        args=(ticker, analysis_date)
    )
    analysis_thread.start()

    return jsonify({'status': 'started', 'ticker': ticker, 'date': analysis_date})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    return jsonify(current_status)


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', current_status)


@socketio.on('request_status')
def handle_status_request():
    """Handle status request"""
    emit('status', current_status)


if __name__ == '__main__':
    # Set console encoding for Windows
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

    # Redirect stdout to web UI logger
    original_stdout = sys.stdout
    sys.stdout = WebUILogger(original_stdout)

    print("🚀 TradingAgents Enterprise Web UI Starting...")
    print(f"📊 Access the UI at: http://localhost:5000")
    print(f"🎯 WatsonX integration ready")
    print("")

    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
