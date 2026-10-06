# Handoff Description & Future Expansion Guide

## Project Architecture
This project is built using Python, Streamlit, and Plotly. 

- **`app.py`**: The main entry point for the Streamlit application. It handles the data ingestion (`data.csv`), app layout, custom HTML/CSS injections, and interactivity.
- **`data.csv`**: A static dataset based on the schema mapping Khon Kaen University's TCAS admission metrics and graduate outcomes.
- **`assets/style.css`**: Contains all custom styling to match the requested "Cute Cartoon Retro Style." This includes custom fonts (`Fredoka`, `Mali`), soft card shadows, border radii (`16px` - `24px`), and the primary brand color (`#A73B24`).

## Key Implementations
1. **Data Integration**: Successfully loads CSV based on the required schema. Added a `Demand_Index` calculation mapped from `Demand_Status` for the dual bar chart.
2. **Interactive Callbacks**: The dropdown filter (`id='cluster-filter'`) triggers a callback that updates all KPI cards and the two main charts simultaneously, demonstrating full cross-filtering capabilities.
3. **Visual Design**: The UI layout utilizes custom CSS classes (`.kpi-card`, `.chart-container`, `.filter-container`) to strictly adhere to the requested styling constraints.
4. **Citations/Sources**: Each component includes an explicitly styled `.data-source` class underneath to satisfy the mandatory verification requirement.

## Future Expansion Recommendations
- **Database Integration**: Migrate `data.csv` to a SQL Database (e.g., PostgreSQL) or NoSQL document store to handle real-time data from KKU APIs.
- **Additional Filtering**: Expand the filter criteria to allow multi-select by `Faculty` or `Major`, and filter by academic year.
- **Advanced Visualizations**:
  - Implement a Radar chart for skill gaps / mismatch visualization if additional survey data is obtained.
  - Implement a Sunburst or Donut chart for a deeper dive into the employment ratio (e.g., Employed, Further Studies, Unemployed).
- **Responsive Layout**: Currently structured using CSS flexbox; consider migrating to `dash-bootstrap-components` for more robust responsive behavior on mobile devices.
- **Caching**: Implement `flask-caching` for the dataset if the dataset grows larger, to prevent the Dash app from reloading the CSV on every callback for heavy queries.
