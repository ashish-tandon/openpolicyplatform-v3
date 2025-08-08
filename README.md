# Open Policy Platform - Unified Repository

This repository contains a comprehensive open policy platform that merges multiple specialized repositories into a unified codebase for managing, analyzing, and presenting policy data.

## 🏗️ Repository Structure

### Core Applications
- **`apps/open-policy-main/`** - Main React Native application
- **`apps/open-policy-app/`** - Policy application components
- **`apps/open-policy-web/`** - Web interface (React/Vite)
- **`apps/admin-open-policy/`** - Administrative interface

### Backend & Infrastructure
- **`backend/OpenPolicyAshBack/`** - Main backend API and services
- **`infrastructure/open-policy-infra/`** - Infrastructure configuration and deployment

### Data Sources & Scrapers
- **`scrapers/openparliament/`** - Parliamentary data scraping
- **`scrapers/scrapers-ca/`** - Canadian government data scrapers
- **`scrapers/civic-scraper/`** - Civic data collection tools

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (v3.8+)
- Docker
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd open-policy-platform
   ```

2. **Backend Setup**
   ```bash
   cd backend/OpenPolicyAshBack
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **Frontend Setup**
   ```bash
   # Web Interface
   cd apps/open-policy-web
   npm install
   npm run dev
   
   # Mobile App
   cd apps/open-policy-main
   npm install
   npx expo start
   ```

## 📁 Detailed Component Documentation

### Core Applications
- [Open Policy Main App](./apps/open-policy-main/README.md)
- [Open Policy App](./apps/open-policy-app/README.md)
- [Open Policy Web](./apps/open-policy-web/README.md)
- [Admin Interface](./apps/admin-open-policy/README.md)

### Backend Services
- [Backend API](./backend/OpenPolicyAshBack/README.md)
- [Infrastructure](./infrastructure/open-policy-infra/README.md)

### Data Collection
- [Parliamentary Data](./scrapers/openparliament/README.md)
- [Canadian Scrapers](./scrapers/scrapers-ca/README.md)
- [Civic Scraper](./scrapers/civic-scraper/README.md)

## 🔧 Development

### Architecture Overview
This platform follows a microservices architecture with:
- **Frontend**: React Native (mobile) + React (web)
- **Backend**: Django/Python API
- **Data Collection**: Specialized scrapers for different data sources
- **Infrastructure**: Docker-based deployment

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📊 Features

- **Policy Analysis**: Comprehensive policy data collection and analysis
- **Multi-Platform**: Web and mobile interfaces
- **Data Integration**: Multiple government data sources
- **Real-time Updates**: Live policy tracking
- **Administrative Tools**: Full admin interface for data management

## 📄 License

This project is open source. See individual component directories for specific licenses.

## 🤝 Support

For questions or support, please refer to the documentation in each component directory or create an issue in this repository.

---

**Note**: This is a unified repository created by merging multiple specialized repositories. Each component maintains its original structure and documentation within its respective directory.
