# Emergency Interim Housing Site Scorer

An AI-powered tool to help the City of San Jose optimize the placement of Emergency Interim Housing (EIH) sites by analyzing neighborhood suitability based on multiple factors.

## Features

- Neighborhood scoring based on:
  - Proximity to essential services (healthcare, public transit, grocery stores)
  - Infrastructure availability (utilities, road access)
  - Demographic risk factors
  - Environmental considerations
- Interactive map visualization with click-to-add locations
- Real-time scoring and analysis
- Beautiful data visualizations using Plotly
- User-friendly Streamlit interface

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run src/app.py
   ```
2. The app will automatically open in your default web browser
3. Use the interactive map to select potential EIH sites:
   - Click on the map to add locations
   - Enter coordinates manually
   - Clear selections as needed
4. Click "Analyze Selected Locations" to see detailed scoring results
5. Review the analysis through interactive charts and tables

## Data Sources

- Census Bureau API
- OpenStreetMap
- City of San Jose Open Data Portal
- CalEnviroScreen
- Local infrastructure data

## Scoring Methodology

The site scoring algorithm considers multiple weighted factors:

1. Access to Services (40%)
   - Public transportation (10%)
   - Healthcare facilities (10%)
   - Grocery stores (10%)
   - Social services (10%)

2. Infrastructure (30%)
   - Utility access (10%)
   - Road connectivity (10%)
   - Emergency service response times (10%)

3. Community Impact (30%)
   - Population density (10%)
   - Demographic risk factors (10%)
   - Environmental justice considerations (10%)

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 