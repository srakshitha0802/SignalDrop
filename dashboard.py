"""
Simple Dashboard Interface for SignalDrop AI

Provides a web-based dashboard for viewing alerts, risk timelines,
and system statistics using FastAPI and HTML templates.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime, timedelta
import uvicorn

from signal_drop import SignalDropSystem
from data_generator import SyntheticDataGenerator
from evaluation import SignalDropEvaluator

app = FastAPI(title="SignalDrop AI Dashboard", description="Early Warning Risk Detection System")

# Initialize system components
signal_drop_system = SignalDropSystem()
data_generator = SyntheticDataGenerator(num_students=50, days_back=30)
evaluator = SignalDropEvaluator(signal_drop_system)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Data models
class AlertRequest(BaseModel):
    student_id: Optional[str] = None

class DataUploadRequest(BaseModel):
    lms_activity: List[Dict] = []
    assignments: List[Dict] = []
    messages: List[Dict] = []
    attendance: List[Dict] = []

# Global data storage (in production, use a proper database)
current_data = {}
current_alerts = []
system_stats = {}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/alerts")
async def get_alerts(student_id: Optional[str] = None):
    """Get current alerts."""
    if not current_alerts:
        return {"alerts": [], "message": "No data processed yet"}
    
    if student_id:
        filtered_alerts = [alert for alert in current_alerts if alert.get('student_id') == student_id]
        return {"alerts": filtered_alerts}
    
    return {"alerts": current_alerts}

@app.post("/api/process-data")
async def process_data(data: DataUploadRequest):
    """Process new data and generate alerts."""
    global current_data, current_alerts, system_stats
    
    try:
        # Convert to dict format
        raw_data = {
            "lms_activity": data.lms_activity,
            "assignments": data.assignments,
            "messages": data.messages,
            "attendance": data.attendance
        }
        
        # Process data
        current_alerts = signal_drop_system.process_student_data(raw_data)
        current_data = raw_data
        system_stats = signal_drop_system.get_system_statistics(raw_data)
        
        return {
            "message": f"Processed data and generated {len(current_alerts)} alerts",
            "alerts_count": len(current_alerts),
            "alerts": current_alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.post("/api/generate-sample-data")
async def generate_sample_data():
    """Generate synthetic sample data."""
    global current_data, current_alerts, system_stats
    
    try:
        # Generate synthetic data
        raw_data = data_generator.generate_all_data()
        
        # Process data
        current_alerts = signal_drop_system.process_student_data(raw_data)
        current_data = raw_data
        system_stats = signal_drop_system.get_system_statistics(raw_data)
        
        return {
            "message": f"Generated sample data for {data_generator.num_students} students",
            "data_summary": data_generator.get_summary_statistics(),
            "alerts_count": len(current_alerts),
            "alerts": current_alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sample data: {str(e)}")

@app.get("/api/student/{student_id}")
async def get_student_details(student_id: str):
    """Get detailed information for a specific student."""
    if not current_data:
        raise HTTPException(status_code=404, detail="No data available")
    
    try:
        profile = signal_drop_system.get_student_profile_summary(student_id, current_data)
        timeline = signal_drop_system.get_risk_timeline(student_id)
        
        # Find student's alert
        student_alert = next((alert for alert in current_alerts if alert.get('student_id') == student_id), None)
        
        return {
            "student_id": student_id,
            "profile": profile,
            "timeline": timeline,
            "alert": student_alert
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting student details: {str(e)}")

@app.get("/api/statistics")
async def get_statistics():
    """Get system-wide statistics."""
    if not system_stats:
        return {"message": "No statistics available"}
    
    return system_stats

@app.get("/api/anomalies")
async def get_anomalies():
    """Get detected anomalies."""
    if not current_data:
        return {"anomalies": [], "message": "No data available"}
    
    try:
        anomalies = signal_drop_system.detect_anomalies(current_data)
        return {"anomalies": anomalies}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")

@app.get("/api/weak-signals")
async def get_weak_signals():
    """Get clustered weak signals."""
    if not current_data:
        return {"weak_signals": {}, "message": "No data available"}
    
    try:
        weak_signals = signal_drop_system.cluster_weak_signals(current_data)
        return {"weak_signals": weak_signals}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clustering weak signals: {str(e)}")

@app.get("/api/export-alerts")
async def export_alerts():
    """Export alerts as JSON."""
    if not current_alerts:
        raise HTTPException(status_code=404, detail="No alerts to export")
    
    try:
        filename = signal_drop_system.export_alerts_json(current_alerts)
        return {"message": f"Alerts exported to {filename}", "filename": filename}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting alerts: {str(e)}")

@app.get("/api/evaluation")
async def run_evaluation():
    """Run comprehensive evaluation."""
    if not current_data:
        raise HTTPException(status_code=404, detail="No data available for evaluation")
    
    try:
        # Generate ground truth for evaluation (in practice, this would be real data)
        ground_truth = _generate_sample_ground_truth()
        
        # Run evaluation
        results = evaluator.run_comprehensive_evaluation(current_data, ground_truth)
        
        # Generate plots
        plot_files = evaluator.plot_evaluation_results(results)
        
        return {
            "evaluation_results": results,
            "plot_files": plot_files
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running evaluation: {str(e)}")

def _generate_sample_ground_truth() -> Dict[str, Dict]:
    """Generate sample ground truth for evaluation."""
    ground_truth = {}
    
    # Create ground truth for students with declining patterns
    for i in range(10, 20):  # Students S1010-S1019
        ground_truth[f"S{1000 + i}"] = {
            "at_risk": True,
            "risk_start_date": (datetime.now() - timedelta(days=15)).isoformat(),
            "risk_type": "academic_decline"
        }
    
    # Create ground truth for stable students
    for i in range(1, 10):  # Students S1001-S1009
        ground_truth[f"S{1000 + i}"] = {
            "at_risk": False,
            "risk_start_date": None,
            "risk_type": None
        }
    
    return ground_truth

# Create templates directory and basic HTML template
def create_templates():
    """Create basic HTML templates for the dashboard."""
    
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    # Dashboard HTML template
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignalDrop AI Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid; }
        .alert-high { border-left-color: #e74c3c; background-color: #fdf2f2; }
        .alert-medium { border-left-color: #f39c12; background-color: #fef9e7; }
        .alert-low { border-left-color: #27ae60; background-color: #f2f9f4; }
        .button { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #5a6fd8; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .loading { text-align: center; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 SignalDrop AI Dashboard</h1>
            <p>Early Warning Risk Detection System for Education</p>
        </div>

        <div class="card">
            <h2>System Controls</h2>
            <button class="button" onclick="generateSampleData()">Generate Sample Data</button>
            <button class="button" onclick="processData()">Process Current Data</button>
            <button class="button" onclick="exportAlerts()">Export Alerts</button>
            <button class="button" onclick="runEvaluation()">Run Evaluation</button>
        </div>

        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalStudents">-</div>
                <div>Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalAlerts">-</div>
                <div>Active Alerts</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="highRisk">-</div>
                <div>High Risk</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="mediumRisk">-</div>
                <div>Medium Risk</div>
            </div>
        </div>

        <div class="card">
            <h2>📊 Risk Distribution</h2>
            <canvas id="riskChart" width="400" height="200"></canvas>
        </div>

        <div class="card">
            <h2>🚨 Recent Alerts</h2>
            <div id="alertsList" class="loading">Loading alerts...</div>
        </div>

        <div class="card">
            <h2>📈 System Statistics</h2>
            <div id="systemStats" class="loading">Loading statistics...</div>
        </div>
    </div>

    <script>
        let currentAlerts = [];
        let riskChart = null;

        async function generateSampleData() {
            try {
                const response = await fetch('/api/generate-sample-data', { method: 'POST' });
                const data = await response.json();
                alert(data.message);
                loadAlerts();
                loadStatistics();
            } catch (error) {
                alert('Error generating sample data: ' + error.message);
            }
        }

        async function processData() {
            try {
                const response = await fetch('/api/process-data', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                alert(data.message);
                loadAlerts();
                loadStatistics();
            } catch (error) {
                alert('Error processing data: ' + error.message);
            }
        }

        async function loadAlerts() {
            try {
                const response = await fetch('/api/alerts');
                const data = await response.json();
                currentAlerts = data.alerts || [];
                displayAlerts();
                updateStats();
                updateRiskChart();
            } catch (error) {
                console.error('Error loading alerts:', error);
            }
        }

        async function loadStatistics() {
            try {
                const response = await fetch('/api/statistics');
                const stats = await response.json();
                displayStatistics(stats);
            } catch (error) {
                console.error('Error loading statistics:', error);
            }
        }

        function displayAlerts() {
            const alertsList = document.getElementById('alertsList');
            
            if (currentAlerts.length === 0) {
                alertsList.innerHTML = '<p>No alerts at this time.</p>';
                return;
            }

            const alertsHtml = currentAlerts.slice(0, 10).map(alert => {
                const riskClass = alert.risk_level === 'high' ? 'alert-high' : 
                                 alert.risk_level === 'medium' ? 'alert-medium' : 'alert-low';
                
                return `
                    <div class="alert ${riskClass}">
                        <strong>Student: ${alert.student_id}</strong> - 
                        Risk Level: ${alert.risk_level.toUpperCase()} - 
                        Momentum: ${alert.risk_momentum}
                        <br><em>${alert.explanation}</em>
                        <br><small>Confidence: ${alert.confidence} | 
                        Key Signals: ${alert.key_signals.join(', ')}</small>
                    </div>
                `;
            }).join('');

            alertsList.innerHTML = alertsHtml;
        }

        function updateStats() {
            const totalAlerts = currentAlerts.length;
            const highRisk = currentAlerts.filter(a => a.risk_level === 'high').length;
            const mediumRisk = currentAlerts.filter(a => a.risk_level === 'medium').length;

            document.getElementById('totalAlerts').textContent = totalAlerts;
            document.getElementById('highRisk').textContent = highRisk;
            document.getElementById('mediumRisk').textContent = mediumRisk;
        }

        function updateRiskChart() {
            const ctx = document.getElementById('riskChart').getContext('2d');
            
            const riskCounts = {
                high: currentAlerts.filter(a => a.risk_level === 'high').length,
                medium: currentAlerts.filter(a => a.risk_level === 'medium').length,
                low: currentAlerts.filter(a => a.risk_level === 'low').length
            };

            if (riskChart) {
                riskChart.destroy();
            }

            riskChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['High Risk', 'Medium Risk', 'Low Risk'],
                    datasets: [{
                        data: [riskCounts.high, riskCounts.medium, riskCounts.low],
                        backgroundColor: ['#e74c3c', '#f39c12', '#27ae60']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        function displayStatistics(stats) {
            const systemStats = document.getElementById('systemStats');
            
            if (!stats.total_students) {
                systemStats.innerHTML = '<p>No statistics available.</p>';
                return;
            }

            document.getElementById('totalStudents').textContent = stats.total_students;

            const coverageHtml = Object.entries(stats.data_source_coverage || {}).map(([source, data]) => 
                `<p><strong>${source}:</strong> ${data.coverage}/${stats.total_students} students (${data.percentage.toFixed(1)}%)</p>`
            ).join('');

            systemStats.innerHTML = `
                <h3>Data Coverage</h3>
                ${coverageHtml}
                <h3>Risk Distribution</h3>
                <p>High Risk: ${stats.risk_distribution?.high || 0}</p>
                <p>Medium Risk: ${stats.risk_distribution?.medium || 0}</p>
                <p>Low Risk: ${stats.risk_distribution?.low || 0}</p>
            `;
        }

        async function exportAlerts() {
            try {
                const response = await fetch('/api/export-alerts');
                const data = await response.json();
                alert(data.message);
            } catch (error) {
                alert('Error exporting alerts: ' + error.message);
            }
        }

        async function runEvaluation() {
            try {
                const response = await fetch('/api/evaluation');
                const data = await response.json();
                alert('Evaluation completed! Check console for results.');
                console.log('Evaluation Results:', data.evaluation_results);
            } catch (error) {
                alert('Error running evaluation: ' + error.message);
            }
        }

        // Load data on page load
        window.onload = function() {
            loadAlerts();
            loadStatistics();
        };
    </script>
</body>
</html>
    """
    
    with open("templates/dashboard.html", "w") as f:
        f.write(dashboard_html)

if __name__ == "__main__":
    create_templates()
    uvicorn.run(app, host="0.0.0.0", port=8000)
