# SwellSense Project Structure

This document outlines the recommended folder structure for the SwellSense project, designed to maintain clean separation of concerns and follow industry best practices.

## 📁 Root Structure

```
swellsense/
├── README.md                    # Project documentation
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Multi-container Docker setup
├── Makefile                     # Common development commands
├── LICENSE                      # Project license
├── CONTRIBUTING.md              # Contribution guidelines
│
├── backend/                     # FastAPI Python backend
├── frontend/                    # Next.js React frontend
├── data/                        # Data science and ML assets
├── shared/                      # Shared code and schemas
├── config/                      # Environment configurations
├── scripts/                     # Utility and deployment scripts
├── docs/                        # Additional documentation
├── docker/                      # Docker configuration files
└── .github/                     # GitHub workflows and templates
```

## 🐍 Backend Structure (`/backend/`)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── api/                     # API route handlers
│   │   ├── __init__.py
│   │   ├── v1/                  # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication endpoints
│   │   │   ├── forecast.py      # Surf forecast endpoints
│   │   │   ├── spots.py         # Surf spot endpoints
│   │   │   ├── users.py         # User management endpoints
│   │   │   └── sessions.py      # Surf session endpoints
│   │   └── deps.py              # Common dependencies
│   │
│   ├── core/                    # Core application logic
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # Security utilities (JWT, hashing)
│   │   ├── database.py          # Database connection setup
│   │   └── celery_app.py        # Celery configuration
│   │
│   ├── models/                  # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model class
│   │   ├── user.py              # User model
│   │   ├── surf_spot.py         # Surf spot model
│   │   ├── forecast.py          # Forecast data model
│   │   └── session.py           # Surf session model
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── forecast_service.py  # Forecast generation
│   │   ├── data_collector.py    # External data collection
│   │   ├── notification_service.py  # Push notifications
│   │   └── ai_assistant.py      # AI chat functionality
│   │
│   └── ml/                      # Machine learning modules
│       ├── __init__.py
│       ├── models/              # ML model definitions
│       ├── training/            # Training scripts
│       ├── inference.py         # Model inference
│       └── preprocessing.py     # Data preprocessing
│
├── tests/                       # Backend tests
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── test_api/                # API endpoint tests
│   ├── test_services/           # Service layer tests
│   └── test_ml/                 # ML module tests
│
├── alembic/                     # Database migrations
│   ├── versions/                # Migration files
│   ├── env.py                   # Alembic environment
│   └── alembic.ini              # Alembic configuration
│
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml              # Python project configuration
├── Dockerfile                  # Backend Docker image
└── .env.example                # Environment variables template
```

## ⚛️ Frontend Structure (`/frontend/`)

```
frontend/
├── src/
│   ├── components/              # Reusable React components
│   │   ├── common/              # Generic UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Layout.tsx
│   │   ├── forecast/            # Forecast-specific components
│   │   │   ├── ForecastCard.tsx
│   │   │   ├── WaveChart.tsx
│   │   │   └── ConditionsMap.tsx
│   │   └── navigation/          # Navigation components
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── TabBar.tsx
│   │
│   ├── pages/                   # Next.js pages
│   │   ├── _app.tsx             # App wrapper
│   │   ├── _document.tsx        # HTML document
│   │   ├── index.tsx            # Home page
│   │   ├── forecast/            # Forecast pages
│   │   ├── spots/               # Surf spot pages
│   │   ├── profile/             # User profile pages
│   │   └── auth/                # Authentication pages
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.ts           # Authentication hook
│   │   ├── useForecast.ts       # Forecast data hook
│   │   ├── useGeolocation.ts    # Location services hook
│   │   └── useNotifications.ts  # Push notifications hook
│   │
│   ├── utils/                   # Utility functions
│   │   ├── api.ts               # API client configuration
│   │   ├── constants.ts         # Application constants
│   │   ├── helpers.ts           # Helper functions
│   │   └── formatters.ts        # Data formatting utilities
│   │
│   ├── types/                   # TypeScript type definitions
│   │   ├── api.ts               # API response types
│   │   ├── forecast.ts          # Forecast data types
│   │   ├── user.ts              # User data types
│   │   └── global.ts            # Global type definitions
│   │
│   ├── styles/                  # CSS and styling
│   │   ├── globals.css          # Global styles
│   │   ├── components.css       # Component styles
│   │   └── tailwind.css         # Tailwind imports
│   │
│   └── lib/                     # Third-party library configurations
│       ├── auth.ts              # Auth provider setup
│       ├── analytics.ts         # Analytics setup
│       └── notifications.ts     # Push notification setup
│
├── public/                      # Static assets
│   ├── images/                  # Image assets
│   ├── icons/                   # Icon files
│   ├── manifest.json            # PWA manifest
│   └── favicon.ico              # Site favicon
│
├── package.json                 # Node.js dependencies
├── package-lock.json            # Locked dependency versions
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── .eslintrc.json              # ESLint configuration
├── Dockerfile                  # Frontend Docker image
└── .env.local.example          # Environment variables template
```

## 📊 Data Structure (`/data/`)

```
data/
├── raw/                         # Raw data files
│   ├── buoy_data/              # NOAA buoy data
│   ├── tide_data/              # Tide information
│   ├── weather_data/           # Weather data
│   └── historical/             # Historical surf data
│
├── processed/                   # Cleaned and processed data
│   ├── features/               # Feature engineered datasets
│   ├── training/               # Training datasets
│   └── validation/             # Validation datasets
│
├── models/                     # Trained ML models
│   ├── forecast_models/        # Surf forecasting models
│   ├── recommendation_models/  # Recommendation system models
│   └── archived/               # Previous model versions
│
└── scripts/                    # Data processing scripts
    ├── collect_data.py         # Data collection automation
    ├── clean_data.py           # Data cleaning utilities
    ├── train_models.py         # Model training scripts
    └── evaluate_models.py      # Model evaluation scripts
```

## 🔄 Shared Structure (`/shared/`)

```
shared/
├── schemas/                     # Shared data schemas
│   ├── forecast_schema.py      # Forecast data schema
│   ├── user_schema.py          # User data schema
│   └── api_schema.py           # API request/response schemas
│
├── types/                      # Shared type definitions
│   ├── forecast_types.ts       # TypeScript forecast types
│   ├── user_types.ts           # TypeScript user types
│   └── common_types.ts         # Common type definitions
│
└── constants/                  # Shared constants
    ├── api_endpoints.py        # API endpoint constants
    ├── surf_conditions.py      # Surf condition mappings
    └── geographic_data.py      # Geographic constants
```

## ⚙️ Configuration Structure (`/config/`)

```
config/
├── development/                # Development environment
│   ├── database.yml
│   ├── redis.yml
│   └── api.yml
│
├── staging/                    # Staging environment
│   ├── database.yml
│   ├── redis.yml
│   └── api.yml
│
├── production/                 # Production environment
│   ├── database.yml
│   ├── redis.yml
│   └── api.yml
│
└── shared/                     # Shared configuration
    ├── logging.yml
    ├── security.yml
    └── monitoring.yml
```

## 🛠️ Scripts Structure (`/scripts/`)

```
scripts/
├── setup/                      # Setup and installation scripts
│   ├── install_dependencies.sh
│   ├── setup_database.sh
│   └── init_project.sh
│
├── deployment/                 # Deployment scripts
│   ├── deploy_staging.sh
│   ├── deploy_production.sh
│   └── rollback.sh
│
├── maintenance/                # Maintenance scripts
│   ├── backup_database.sh
│   ├── clean_logs.sh
│   └── update_dependencies.sh
│
└── data/                       # Data management scripts
    ├── seed_database.py
    ├── migrate_data.py
    └── export_data.py
```

## 🐳 Docker Structure (`/docker/`)

```
docker/
├── backend/
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── requirements.txt
│
├── frontend/
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   └── nginx.conf
│
├── nginx/
│   ├── nginx.conf
│   └── ssl/
│
└── compose/
    ├── docker-compose.dev.yml
    ├── docker-compose.prod.yml
    └── docker-compose.test.yml
```

## 📚 Documentation Structure (`/docs/`)

```
docs/
├── api/                        # API documentation
│   ├── authentication.md
│   ├── forecast_endpoints.md
│   └── user_endpoints.md
│
├── deployment/                 # Deployment guides
│   ├── aws_deployment.md
│   ├── docker_setup.md
│   └── environment_setup.md
│
├── development/                # Development guides
│   ├── getting_started.md
│   ├── coding_standards.md
│   └── testing_guide.md
│
└── architecture/               # System architecture
    ├── system_overview.md
    ├── database_schema.md
    └── ml_pipeline.md
```

## 🚀 GitHub Structure (`/.github/`)

```
.github/
├── workflows/                  # GitHub Actions
│   ├── ci.yml                  # Continuous integration
│   ├── cd.yml                  # Continuous deployment
│   ├── test.yml                # Test automation
│   └── security.yml            # Security scanning
│
├── ISSUE_TEMPLATE/             # Issue templates
│   ├── bug_report.md
│   ├── feature_request.md
│   └── question.md
│
├── PULL_REQUEST_TEMPLATE.md    # PR template
└── CODEOWNERS                  # Code ownership rules
```

## 🎯 Key Benefits of This Structure

### **Separation of Concerns**
- Clear boundaries between frontend, backend, and data science
- Shared code prevents duplication
- Environment-specific configurations

### **Scalability**
- Modular architecture supports team growth
- Easy to add new features without conflicts
- Independent deployment of services

### **Developer Experience**
- Intuitive folder naming and organization
- Comprehensive documentation
- Automated workflows and scripts

### **Best Practices**
- Follows industry standards for FastAPI and Next.js
- Includes testing, CI/CD, and deployment considerations
- Security and monitoring built-in

This structure provides a solid foundation for SwellSense that can grow with your team and user base while maintaining code quality and developer productivity.