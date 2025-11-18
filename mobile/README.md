# SwellSense Mobile App

Native iOS/Android app for SwellSense - Your AI Surf Coach

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your phone (for testing)
- iOS Simulator (Mac only) or Android Emulator

### Installation

```bash
cd mobile
npm install
```

### Configuration

1. **Update Supabase credentials** in `services/auth.ts`:
```typescript
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key';
```

2. **Backend API** automatically points to:
   - Development: `http://localhost:8000`
   - Production: `https://api.swellsense.app`

### Run the App

```bash
# Start Expo dev server
npx expo start

# Then press:
# - 'i' for iOS Simulator
# - 'a' for Android Emulator  
# - Scan QR code with Expo Go app on your phone
```

## 📱 Features Implemented

### ✅ Phase 1 (Current)
- [x] Authentication (Supabase)
- [x] Manual session logging
- [x] Session history
- [x] Session statistics
- [x] Home dashboard

### 🚧 Phase 2 (Next)
- [ ] HealthKit background sync
- [ ] Push notifications
- [ ] Alert preferences
- [ ] Favorite spots (map view)
- [ ] Daily brief
- [ ] Breaking news alerts

### 🔮 Phase 3 (Future)
- [ ] AI chat integration
- [ ] Dawn Patrol import
- [ ] Apple Watch app
- [ ] Widgets
- [ ] Buddy system

## 🗂️ Project Structure

```
mobile/
├── App.tsx                 # Main app with navigation
├── app.json               # Expo configuration
├── services/
│   ├── api.ts            # Backend API client
│   └── auth.ts           # Supabase authentication
└── screens/
    ├── LoginScreen.tsx       # Login/signup
    ├── HomeScreen.tsx        # Dashboard with stats
    ├── LogSessionScreen.tsx  # Manual session entry
    ├── SessionsScreen.tsx    # Session history
    └── ProfileScreen.tsx     # Settings (coming soon)
```

## 🔧 Backend Integration

All API calls go to your FastAPI backend:

**Endpoints used:**
- `POST /api/sessions` - Log new session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/stats` - Get statistics

**Authentication:**
- Supabase JWT token sent in `Authorization: Bearer <token>` header
- Token managed automatically by `api.ts`

## 📦 Building for Production

### iOS (TestFlight)

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Login to Expo:
```bash
eas login
```

3. Configure project:
```bash
eas build:configure
```

4. Build for iOS:
```bash
eas build --platform ios
```

5. Submit to TestFlight:
```bash
eas submit --platform ios
```

### Android (Google Play)

```bash
eas build --platform android
eas submit --platform android
```

## 🧪 Testing

### Run on iOS Simulator (Mac only)
```bash
npx expo start
# Press 'i'
```

### Run on Android Emulator
```bash
npx expo start
# Press 'a'
```

### Test on Physical Device
1. Install Expo Go from App Store/Play Store
2. Run `npx expo start`
3. Scan QR code with Expo Go app

## 🔐 Environment Variables

Create `.env` file (git-ignored):

```env
EXPO_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 📱 Permissions

### iOS (app.json)
- **HealthKit**: Sync surf sessions
- **Location (Always)**: Geofence alerts
- **Notifications**: Push alerts

### Android (app.json)
- **Location**: Find nearby spots
- **Notifications**: Push alerts
- **Activity Recognition**: Detect surfing

## 🐛 Troubleshooting

**"Cannot connect to backend"**
- Development: Make sure FastAPI is running on `localhost:8000`
- Production: Check Railway deployment status

**"Supabase auth error"**
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `services/auth.ts`
- Check Supabase dashboard for project status

**"Module not found"**
```bash
rm -rf node_modules
npm install
```

**iOS build fails**
- Update Xcode to latest version
- Run `npx pod-install` (if using bare workflow)

## 🎨 Design System

**Colors:**
- Primary: `#0EA5E9` (Sky blue)
- Background: `#F8FAFC` (Slate 50)
- Text: `#1E293B` (Slate 800)
- Secondary text: `#64748B` (Slate 500)

**Typography:**
- Titles: 28px, bold
- Body: 16px, regular
- Small: 14px, regular

## 📚 Tech Stack

- **React Native** - Cross-platform mobile framework
- **Expo** - Development platform and build service
- **TypeScript** - Type-safe JavaScript
- **React Navigation** - Screen navigation
- **Supabase** - Authentication
- **AsyncStorage** - Local data persistence
- **Expo Notifications** - Push notifications (Phase 2)
- **Expo Location** - Geolocation (Phase 2)
- **Expo HealthKit** - Workout sync (Phase 2)

## 🚢 Deployment Checklist

Before submitting to App Store/Play Store:

- [ ] Update version in `app.json`
- [ ] Update app icon (`assets/icon.png`)
- [ ] Update splash screen (`assets/splash-icon.png`)
- [ ] Test on multiple devices
- [ ] Set production API URL
- [ ] Add privacy policy URL
- [ ] Add terms of service URL
- [ ] Test all permissions
- [ ] Prepare App Store screenshots
- [ ] Write App Store description

## 📄 License

Proprietary - SwellSense 2024
