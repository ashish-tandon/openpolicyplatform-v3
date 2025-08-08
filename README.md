# 🏛️ Open Policy Platform

A unified platform for policy analysis, data collection, and public access to parliamentary information.

## 🎯 **Overview**

The Open Policy Platform is a comprehensive system that merges multiple specialized repositories into a unified codebase for managing, analyzing, and presenting policy data. It provides both public access to policy information and administrative tools for data management.

## 🏗️ **Architecture**

### **Unified Backend Service** (`backend/`)
- **FastAPI Application**: RESTful API with automatic documentation
- **PostgreSQL Database**: 6.5GB of parliamentary data
- **Integrated Scrapers**: Automated data collection pipeline
- **Admin API**: Built-in administrative functions
- **Authentication**: JWT-based role management

### **Unified Web Application** (`web/`)
- **React + TypeScript**: Modern web interface
- **Role-Based Access**: Public and admin interfaces
- **Responsive Design**: Works on all devices
- **Real-Time Updates**: Live data synchronization
- **Admin Dashboard**: Complete system management

### **Mobile Applications** (`mobile/`)
- **React Native Apps**: Preserved for future development
- **Cross-Platform**: iOS and Android support
- **Offline Capability**: Planned for future releases

## 🚀 **Quick Start**

### **1. Prerequisites**
- Node.js 18+
- Python 3.8+
- PostgreSQL 14+
- Git

### **2. Setup**
```bash
# Clone the repository
git clone <repository-url>
cd open-policy-platform

# Run unified setup
./scripts/setup-unified.sh
```

### **3. Start Services**
```bash
# Start all services
./scripts/start-all.sh
```

### **4. Access the Platform**
- **Web Interface**: http://localhost:5173
- **Admin Interface**: http://localhost:5173/admin
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

### **5. Default Credentials**
- **Username**: `admin`
- **Password**: `admin`

## 📊 **Features**

### **Public Features**
- **Policy Browsing**: Search and browse parliamentary policies
- **Bill Information**: Detailed bill information and status
- **Member Profiles**: MP information and voting records
- **Committee Data**: Committee information and activities
- **Debate Records**: Parliamentary debate transcripts

### **Admin Features**
- **Dashboard**: System overview and statistics
- **Data Management**: Policy and data administration
- **Scraper Control**: Manage data collection processes
- **System Monitoring**: Health checks and performance
- **User Management**: Role-based access control

### **API Features**
- **RESTful API**: Complete API for all data
- **Authentication**: JWT-based security
- **Documentation**: Automatic API documentation
- **Real-time Updates**: WebSocket support
- **Rate Limiting**: API usage protection

## 🔧 **Technology Stack**

### **Backend**
- **Framework**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL with 6.5GB data
- **Authentication**: JWT + Role-based access
- **Caching**: Redis
- **Documentation**: Automatic OpenAPI/Swagger

### **Frontend**
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **State Management**: React Context + Hooks

### **Infrastructure**
- **Containerization**: Docker
- **Web Server**: Nginx
- **Monitoring**: Health checks + logging
- **Deployment**: Production-ready configuration

## 📁 **Project Structure**

```
open-policy-platform/
├── 📁 backend/                    # Unified Backend Service
│   ├── 📁 api/                   # FastAPI Application
│   ├── 📁 config/                # Configuration
│   ├── 📁 models/                # Data Models
│   ├── 📁 services/              # Business Logic
│   ├── 📁 scrapers/              # Integrated Scrapers
│   └── requirements.txt          # Python Dependencies
│
├── 📁 web/                       # Unified Web Application
│   ├── 📁 src/                   # Source Code
│   ├── 📁 public/                # Static Assets
│   └── package.json              # Node.js Dependencies
│
├── 📁 mobile/                    # Mobile Applications (Future)
│   ├── 📁 open-policy-main/      # Main Mobile App
│   ├── 📁 open-policy-app/       # Mobile Components
│   └── README.md                 # Mobile Documentation
│
├── 📁 docs/                      # Platform Documentation
│   ├── 📁 architecture/          # Architecture Documentation
│   ├── 📁 api/                   # API Documentation
│   ├── 📁 deployment/            # Deployment Guides
│   └── 📁 development/           # Development Guides
│
├── 📁 scripts/                   # Platform Scripts
│   ├── setup-unified.sh          # Main Setup Script
│   ├── start-all.sh              # All Services Startup
│   └── README.md                 # Scripts Documentation
│
└── 📁 infrastructure/            # Infrastructure Configuration
    ├── 📁 docker/                # Docker Configuration
    ├── 📁 nginx/                 # Nginx Configuration
    └── 📁 monitoring/            # Monitoring Configuration
```

## 📚 **Documentation**

- **[Architecture](docs/architecture/)** - System architecture and design
- **[API Documentation](docs/api/)** - Complete API reference
- **[Development Guide](docs/development/)** - Development setup and guidelines
- **[Deployment Guide](docs/deployment/)** - Production deployment
- **[User Guides](docs/user-guides/)** - End user documentation

## 🔄 **Development Workflow**

### **Local Development**
```bash
# Start backend only
./scripts/start-backend.sh

# Start web application only
./scripts/start-web.sh

# Start all services
./scripts/start-all.sh
```

### **API Development**
- **API Documentation**: http://localhost:8000/docs
- **Interactive Testing**: Use the Swagger UI
- **Code Generation**: Automatic from FastAPI

### **Frontend Development**
- **Hot Reload**: Automatic with Vite
- **TypeScript**: Full type safety
- **Component Library**: Shared components

## 🚀 **Deployment**

### **Production Setup**
```bash
# Build and deploy
./scripts/deploy.sh
```

### **Docker Deployment**
```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d
```

### **Environment Configuration**
- Copy `.env.example` to `.env`
- Configure database and API settings
- Set production environment variables

## 🤝 **Contributing**

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

See [Contributing Guide](docs/development/contributing.md) for details.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [support@openpolicy.com]

## 📈 **Roadmap**

### **Current Version (1.0.0)**
- ✅ Unified platform architecture
- ✅ Database integration
- ✅ API and web interface
- ✅ Admin dashboard
- ✅ Role-based access

### **Future Versions**
- 🔄 Mobile application development
- 🔄 Advanced analytics features
- 🔄 Real-time notifications
- 🔄 Advanced search capabilities
- 🔄 Machine learning integration

---

**🎉 Open Policy Platform - Making Policy Data Accessible to Everyone**

*Last Updated: August 8, 2024*
*Version: 1.0.0*
