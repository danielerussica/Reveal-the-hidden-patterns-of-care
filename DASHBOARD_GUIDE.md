# 🏥 Healthcare Network Dashboard User Guide

## 🚀 Quick Start

### Launch the Dashboard
```bash
# Method 1: Direct launch
streamlit run healthcare_network_dashboard.py

# Method 2: Using launcher script
./launch_dashboard.sh

# Method 3: Test components first
python test_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 🎯 Dashboard Overview

The Healthcare Network Dashboard provides an interactive way to explore treatment flows and patient journeys through a dynamic network visualization. You can filter, query, and analyze healthcare provider relationships in real-time.

### 🔗 Core Features

**Interactive Network Graph**
- **Nodes**: Healthcare providers (size = patient volume, color = provider group)
- **Edges**: Patient transitions between providers (width = transition frequency)
- **Interactivity**: Click, drag, zoom, and hover for details

**Real-time Filtering**
- Demographics (age, gender)
- Treatment reasons (illness, accident, maternity)
- Provider types and groups
- Network complexity (minimum transitions)

**Analytics Dashboard**
- Key metrics (patients, providers, transitions)
- Top connections ranking
- Provider activity statistics
- Distribution visualizations

## 📊 Using the Dashboard

### 1. Data Loading
```
Sidebar → Data Loading
├── Sample Size: 10,000 - 200,000 records
├── Number of Files: 1-5 CSV files
└── Click "Load Data" to start
```

**Recommendations:**
- **Small exploration**: 10K-30K records, 1-2 files
- **Detailed analysis**: 50K-100K records, 3-5 files
- **Full analysis**: 200K+ records, all files (may be slow)

### 2. Network Filtering

#### Demographic Filters
- **Age Group**: Focus on specific age ranges (0-10 Jahre, 60-70 Jahre, etc.)
- **Gender**: Male/Female analysis
- **Treatment Reason**: 
  - `Krankheit` (Illness) - 95% of cases
  - `Unfall` (Accident) - Emergency care patterns
  - `Mutterschaft` (Maternity) - Women's health journeys

#### Provider Filters
- **Provider Group**: Filter by main categories
  - `Spitäler` (Hospitals) - Institutional care
  - `Ärzte und Ärztinnen` (Physicians) - Primary/specialty care
  - `Laboratorien` (Laboratories) - Diagnostic services
  - `Pflegeheime` (Care Homes) - Long-term care

#### Network Settings
- **Minimum Transitions**: Filter weak connections (1-50)
  - `1-5`: Include all connections (dense network)
  - `5-15`: Focus on common pathways (balanced)
  - `15+`: Only major care flows (simplified)

### 3. Visualization Modes

#### Interactive Network (Recommended)
- **Full interactivity**: Drag nodes, zoom, pan
- **Node selection**: Click for detailed information
- **Dynamic physics**: Self-organizing layout
- **Best for**: Exploration and discovery

#### Plotly Network
- **Static layout**: Pre-calculated positions
- **Hover details**: Rich tooltips
- **Better performance**: For large networks
- **Best for**: Analysis and screenshots

### 4. Network Analysis

#### Understanding Node Properties
- **Size**: Larger nodes = more unique patients
- **Color**: Provider group classification
- **Position**: Network algorithms determine centrality

#### Understanding Edge Properties  
- **Width**: Thicker edges = more patient transitions
- **Direction**: Arrow shows transition flow
- **Color**: Consistent styling for clarity

#### Key Network Patterns to Look For
1. **Hub Nodes**: Large, central providers (e.g., major hospitals)
2. **Chains**: Sequential care pathways (e.g., diagnosis → treatment → pharmacy)
3. **Clusters**: Specialized care networks (e.g., pediatric, geriatric)
4. **Outliers**: Unusual or rare connections

## 🔍 Analysis Scenarios

### Scenario 1: Pediatric Care Analysis
```
Filters:
├── Age Group: "0-10 Jahre"
├── Min Transitions: 3
└── Visualization: Interactive Network

Expected Insights:
├── Pediatric specialists as hubs
├── School health connections
├── Family medicine pathways
└── Vaccination/prevention patterns
```

### Scenario 2: Emergency Care Flows
```
Filters:
├── Treatment Reason: "Unfall"
├── Provider Group: "Spitäler"
├── Min Transitions: 5
└── Visualization: Plotly Network

Expected Insights:
├── Emergency room centrality
├── Trauma surgery pathways
├── Rehabilitation connections  
└── Follow-up care patterns
```

### Scenario 3: Chronic Disease Management
```
Filters:
├── Age Group: "60-70 Jahre"
├── Min Transitions: 10
└── Gender: All

Expected Insights:
├── Complex care journeys
├── Specialist coordination
├── Long-term care transitions
└── Medication management (pharmacy connections)
```

### Scenario 4: Provider Network Analysis
```
Filters:
├── Provider Group: "Ärzte und Ärztinnen"
├── Min Transitions: 2
└── Sample Size: 100K+

Expected Insights:
├── Referral patterns between specialists
├── Primary care gatekeeping
├── Diagnostic pathway efficiency
└── Care coordination opportunities
```

## 📈 Interpreting Results

### Network Metrics
- **Total Patients**: Unique individuals in filtered dataset
- **Provider Types**: Number of different healthcare providers
- **Transitions**: Total patient movements between providers
- **Avg Transitions/Patient**: Care journey complexity indicator

### Top Connections Analysis
Look for:
- **High-frequency pathways**: Standard care protocols
- **Unexpected connections**: Potential inefficiencies
- **Missing links**: Care gaps or coordination issues
- **Bidirectional flows**: Collaborative relationships

### Provider Activity Rankings
Identify:
- **Volume leaders**: Highest patient counts
- **Specialization patterns**: Unique patient populations
- **Care coordination hubs**: Providers with many connections
- **Outlier services**: Low volume, high specialization

## 💡 Advanced Tips

### Optimization Strategies
1. **Start broad, then narrow**: Begin with "All" filters, then focus
2. **Balance complexity**: Too few transitions = sparse, too many = oversimplified
3. **Use both visualizations**: Interactive for exploration, Plotly for analysis
4. **Export insights**: Download network data for external analysis

### Performance Considerations
- **Large datasets**: Use Plotly visualization for >100 nodes
- **Complex filters**: Apply gradually to understand impact
- **Memory management**: Restart dashboard if performance degrades
- **Data caching**: Streamlit caches loaded data for faster filtering

### Troubleshooting
- **Empty network**: Reduce minimum transitions or broaden filters
- **Slow performance**: Reduce sample size or use fewer files
- **Visualization errors**: Switch between network types
- **Data issues**: Run `python test_dashboard.py` for diagnostics

## 📊 Export and Sharing

### Data Export Options
- **Network Edges**: CSV file with all connections and weights
- **Node Statistics**: Provider details with patient counts
- **Filtered Results**: Current view parameters preserved

### Sharing Insights
1. **Screenshots**: Use browser tools to capture visualizations
2. **Network Analysis**: Export data for Gephi, Cytoscape, or other tools
3. **Reproducible Analysis**: Document filter settings for colleagues
4. **Dashboard Sharing**: Share URL (local) or deploy to cloud

## 🔮 Future Enhancements

### Planned Features
- **Temporal Analysis**: Time-slider for network evolution
- **Geographic Mapping**: Regional care pattern analysis
- **Cost Integration**: Economic impact visualization
- **Outcome Correlation**: Link network patterns to health outcomes
- **Machine Learning**: Predictive pathway modeling
- **Collaborative Features**: Multi-user analysis sessions

### Integration Opportunities
- **EHR Systems**: Real-time data feeds
- **Quality Metrics**: Provider performance correlation
- **Policy Tools**: Healthcare planning integration
- **Research Platforms**: Academic collaboration features

## 🆘 Support

### Getting Help
- **Test Script**: `python test_dashboard.py` for diagnostics
- **Documentation**: README.md for technical details
- **Analysis Guide**: ANALYSIS_INSIGHTS.md for domain knowledge

### Common Issues
- **Import Errors**: Run `pip install -r requirements.txt`
- **Data Not Found**: Ensure CSV files are in `data/` directory
- **Performance Issues**: Reduce sample size or minimum transitions
- **Visualization Problems**: Clear browser cache and restart

This dashboard transforms complex healthcare data into actionable insights through intuitive network visualization and interactive analysis capabilities. 