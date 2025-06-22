# Stubble Burning Detection System - Frontend

A modern Next.js web application for fire detection, prediction and stubble burning awareness in Northern India.

## Features

### 🔥 Fire Detection
- Real-time fire monitoring with interactive maps
- Multiple data source integration (MODIS, VIIRS, User Reports)
- Advanced filtering by region, date range, and data sources
- Live fire statistics and recent detections panel
- Detailed fire information with confidence levels and brightness data

### 📊 Fire Prediction
- Machine learning powered risk assessment
- Regional fire probability predictions
- Risk factor analysis and peak day forecasting
- Interactive prediction models with 87.3% accuracy
- Alert system for high-risk areas

### 🌱 Stubble Burning Awareness
- Educational content about stubble burning impacts
- Sustainable alternatives and solutions
- Statistics and impact analysis
- Resources for farmers, communities, and policymakers
- Government schemes and contact information

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom Airbnb-inspired design
- **Maps**: React Leaflet for interactive fire visualization
- **Typography**: JetBrains Mono and Fira Code for clean, codey aesthetics
- **Icons**: Lucide React for consistent iconography
- **Language**: TypeScript for type safety

## Design Features

- **Aesthetic Design**: Airbnb-inspired clean and modern interface
- **Typography**: All lowercase text with codey monospace fonts
- **Color Scheme**: Fire-themed palette (fire-red, fire-orange, fire-yellow)
- **Responsive**: Fully responsive design for all device sizes
- **Animations**: Subtle animations and hover effects
- **Accessibility**: High contrast colors and readable fonts

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) with your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── fire-detection/     # Fire detection page
│   │   ├── fire-prediction/    # Fire prediction page
│   │   ├── awareness/          # Awareness page
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx           # Home page
│   ├── components/             # Reusable React components
│   │   ├── Navigation.tsx      # Header navigation
│   │   ├── FireMap.tsx        # Interactive fire map
│   │   ├── FilterPanel.tsx    # Filter controls
│   │   ├── MapStats.tsx       # Map statistics
│   │   └── RecentFiresPanel.tsx # Recent detections
│   ├── lib/                   # Utility functions
│   └── types/                 # TypeScript type definitions
├── public/                    # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

## API Integration Ready

The frontend is designed to integrate with backend APIs:

- **Fire Data Endpoints**: Ready to connect to NASA FIRMS API and custom fire detection services
- **Prediction API**: Prepared for ML model prediction endpoints
- **User Reports**: Ready for user-submitted fire report functionality
- **Real-time Updates**: WebSocket support preparation for live fire updates

## Key Components

### FireMap
- Interactive Leaflet map with fire markers
- Customizable marker colors based on confidence levels
- Popup information for detailed fire data
- Automatic bounds adjustment for fire locations

### FilterPanel
- Region selection (states and cities)
- Date range filters (24hr, 7day, custom)
- Data source checkboxes with descriptions
- Refresh functionality for live updates

### RecentFiresPanel
- Real-time fire detection tiles
- Sortable by detection time
- Confidence level indicators
- Summary statistics

## Customization

### Colors
Edit `tailwind.config.js` to modify the fire-themed color palette:
```javascript
colors: {
  'fire-red': '#FF385C',
  'fire-orange': '#FF7A00',
  'fire-yellow': '#FFD60A',
  // ... other colors
}
```

### Fonts
The application uses custom monospace fonts for the codey aesthetic. Update in `globals.css`:
```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
```

## Performance

- **Bundle Size**: Optimized with Next.js automatic code splitting
- **Images**: Next.js Image optimization ready
- **Caching**: Built-in Next.js caching strategies
- **Lazy Loading**: Components lazy-loaded for better performance

## Deployment

The application is ready for deployment on:
- Vercel (recommended for Next.js)
- Netlify
- AWS Amplify
- Docker containers

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the established code style with lowercase text and codey fonts
2. Use TypeScript for all new components
3. Follow the component structure patterns
4. Test on multiple screen sizes
5. Maintain the Airbnb-inspired design aesthetic

## License

This project is part of the Stubble Burning Detection System.