#!/bin/bash

echo "🏥 Launching Healthcare Network Dashboard..."
echo "📊 Loading healthcare claims data analysis..."
echo ""
echo "Dashboard Features:"
echo "  🔗 Interactive Network Visualization"
echo "  📊 Real-time Analytics & Filtering"
echo "  💾 Data Export Capabilities"
echo "  🎯 Treatment Flow Pattern Discovery"
echo ""
echo "The dashboard will open in your browser at http://localhost:8501"
echo ""
echo "To stop the dashboard, press Ctrl+C"
echo ""

# Launch Streamlit dashboard
streamlit run healthcare_network_dashboard.py --server.headless false 