# SwellSense Mobile App - 3-Week Launch Plan
**Goal:** Native iOS app with HealthKit-style background sync + smart alerts  
**Target Launch:** TestFlight beta in 21 days  
**Differentiator:** Personalized AI surf coach that learns from every session

---

## 🎯 The Fastest Path to Launch

### Why This Approach Wins

**HealthKit-Style Background Sync = No Manual Work**
- User grants permission once → app syncs sessions automatically
- Works with Apple Watch, iPhone fitness tracking, Dawn Patrol (if they log to HealthKit)
- Zero friction after initial setup

**Smart Alerts = Immediate Value**
- Daily brief at user's chosen time (6 AM default)
- Breaking news when conditions suddenly improve
- Location-based "you're near a firing spot" alerts

**No Need for Partnerships Yet**
- HealthKit API is free and built-in
- Can add Dawn Patrol OAuth integration later (Phase 2)
- MVP works standalone

---

## 📅 3-Week Implementation Timeline

### **Week 1: Backend Foundation** (Nov 18-24)

#### Day 1-2: Database Schema ✅ COMPLETED
- [x] Created 4 new tables:
  - `alert_preferences` - User notification settings
  - `favorite_spots` - Saved surf spots with coordinates
  - `alert_history` - Track sent alerts, engagement, conversion to sessions
  - `surf_sessions` - Session logging (manual or imported)

#### Day 3: Backend Endpoints
```bash
POST   /api/alerts/preferences          # Set user alert preferences
GET    /api/alerts/preferences          # Get current preferences
POST   /api/spots/favorites             # Add favorite spot
GET    /api/spots/favorites             # List user's favorites
DELETE /api/spots/favorites/:id         # Remove favorite

POST   /api/sessions                    # Log session manually
GET    /api/sessions                    # List user's sessions
POST   /api/sessions/import-healthkit   # Import from HealthKit
```

#### Day 4-5: Daily Brief Logic
```python
# /api/alerts/daily-brief endpoint
def calculate_daily_brief(user_id):
    # 1. Get user's favorite spots
    favorites = get_favorite_spots(user_id)
    
    # 2. Get current conditions for each spot
    conditions = []
    for spot in favorites:
        buoy = find_nearest_buoy(spot.lat, spot.lon)
        current = get_current_conditions(buoy)
        conditions.append({
            "spot": spot,
            "conditions": current,
            "quality_score": score_conditions(current, user_skill_level)
        })
    
    # 3. Rank by quality score
    ranked = sorted(conditions, key=lambda x: x["quality_score"], reverse=True)
    
    # 4. Return top 3 with AI reasoning
    return {
        "spots": ranked[:3],
        "briefing": generate_ai_briefing(ranked[:3], user_preferences)
    }
```

#### Day 6-7: Push Notification System
```bash
# Set up background jobs
- Celery or Railway Cron Jobs
- Every 15 minutes: check breaking news conditions
- Every morning at user's time: send daily brief

# Expo Push Notifications
- Store push tokens in alert_preferences table
- Send notifications via Expo Push API
```

---

### **Week 2: React Native App** (Nov 25-Dec 1)

#### Day 8-9: Expo Setup
```bash
# Initialize project
npx create-expo-app swellsense-mobile --template blank-typescript
cd swellsense-mobile

# Install dependencies
npx expo install expo-notifications
npx expo install expo-location
npx expo install @react-native-async-storage/async-storage
npx expo install expo-health
npx expo install @supabase/supabase-js

# Dev dependencies
npm install --save-dev @types/react @types/react-native
```

**Core Screens:**
1. Onboarding (1-2-3 swipe through)
2. Login/Signup (Supabase)
3. Alert Settings
4. Favorite Spots (map view)
5. Session Log
6. Profile

#### Day 10-11: HealthKit Integration
```typescript
// src/services/healthkit.ts
import * as Health from 'expo-health';

export async function requestHealthKitPermission() {
  const { status } = await Health.requestPermissionsAsync([
    Health.HealthDataTypes.WORKOUT,
    Health.HealthDataTypes.LOCATION,
  ]);
  return status === 'granted';
}

export async function syncSurfingSessions() {
  // Get workouts of type "Surfing" since last sync
  const lastSync = await AsyncStorage.getItem('last_healthkit_sync');
  const workouts = await Health.getWorkoutsAsync({
    activityType: Health.WorkoutActivityType.SURFING,
    startDate: new Date(lastSync || 0),
  });

  // Send to backend
  for (const workout of workouts) {
    await api.post('/api/sessions/import-healthkit', {
      session_date: workout.startDate,
      duration_minutes: workout.duration / 60,
      spot_name: await reverseGeocode(workout.startLocation),
      latitude: workout.startLocation?.latitude,
      longitude: workout.startLocation?.longitude,
      import_source: 'healthkit',
    });
  }

  await AsyncStorage.setItem('last_healthkit_sync', new Date().toISOString());
}

// Background sync every 6 hours
import * as BackgroundFetch from 'expo-background-fetch';
import * as TaskManager from 'expo-task-manager';

const HEALTHKIT_SYNC_TASK = 'healthkit-sync';

TaskManager.defineTask(HEALTHKIT_SYNC_TASK, async () => {
  try {
    await syncSurfingSessions();
    return BackgroundFetch.BackgroundFetchResult.NewData;
  } catch (error) {
    return BackgroundFetch.BackgroundFetchResult.Failed;
  }
});

await BackgroundFetch.registerTaskAsync(HEALTHKIT_SYNC_TASK, {
  minimumInterval: 60 * 60 * 6, // 6 hours
  stopOnTerminate: false,
  startOnBoot: true,
});
```

#### Day 12-13: Push Notifications
```typescript
// src/services/notifications.ts
import * as Notifications from 'expo-notifications';

export async function registerForPushNotifications() {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') {
    return null;
  }

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id',
  });

  // Save to backend
  await api.post('/api/alerts/preferences', {
    push_token: token.data,
  });

  return token.data;
}

// Handle notification taps
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

Notifications.addNotificationResponseReceivedListener(response => {
  const { spot_name, latitude, longitude } = response.notification.request.content.data;
  
  // Navigate to spot detail
  navigation.navigate('SpotDetail', { spot_name, latitude, longitude });
  
  // Track engagement
  api.post('/api/alerts/opened', {
    alert_id: response.notification.request.content.data.alert_id,
  });
});
```

#### Day 14: Alert Settings Screen
```typescript
// src/screens/AlertSettings.tsx
export function AlertSettingsScreen() {
  const [preferences, setPreferences] = useState({
    daily_brief_enabled: true,
    daily_brief_time: '06:00',
    breaking_news_enabled: true,
    alert_for_favorites: true,
    alert_for_current_location: false,
    alert_radius_miles: 25,
    minimum_quality_score: 7,
  });

  return (
    <ScrollView>
      <Section title="Daily Brief">
        <Toggle
          label="Morning surf report"
          value={preferences.daily_brief_enabled}
          onChange={(v) => update({ daily_brief_enabled: v })}
        />
        {preferences.daily_brief_enabled && (
          <TimePicker
            label="Send at"
            value={preferences.daily_brief_time}
            onChange={(v) => update({ daily_brief_time: v })}
          />
        )}
      </Section>

      <Section title="Breaking News">
        <Toggle
          label="Alert when conditions are perfect"
          value={preferences.breaking_news_enabled}
          onChange={(v) => update({ breaking_news_enabled: v })}
        />
        <Slider
          label="Minimum quality (1-10)"
          value={preferences.minimum_quality_score}
          min={1}
          max={10}
          onChange={(v) => update({ minimum_quality_score: v })}
        />
      </Section>

      <Section title="Location-Based">
        <Toggle
          label="Alert for favorite spots"
          value={preferences.alert_for_favorites}
          onChange={(v) => update({ alert_for_favorites: v })}
        />
        <Toggle
          label="Alert when near good spots"
          value={preferences.alert_for_current_location}
          onChange={(v) => update({ alert_for_current_location: v })}
        />
        {preferences.alert_for_current_location && (
          <Slider
            label="Check within (miles)"
            value={preferences.alert_radius_miles}
            min={5}
            max={50}
            step={5}
            onChange={(v) => update({ alert_radius_miles: v })}
          />
        )}
      </Section>
    </ScrollView>
  );
}
```

---

### **Week 3: Polish & TestFlight** (Dec 2-8)

#### Day 15-17: Favorite Spots Map
```typescript
// src/screens/FavoriteSpots.tsx
import MapView, { Marker } from 'react-native-maps';

export function FavoriteSpotsScreen() {
  const [spots, setSpots] = useState([]);
  const [adding, setAdding] = useState(false);

  return (
    <View>
      <MapView
        initialRegion={{
          latitude: 18.4663,
          longitude: -66.1057,
          latitudeDelta: 0.5,
          longitudeDelta: 0.5,
        }}
        onPress={(e) => {
          if (adding) {
            addSpot(e.nativeEvent.coordinate);
          }
        }}
      >
        {spots.map(spot => (
          <Marker
            key={spot.id}
            coordinate={{ latitude: spot.latitude, longitude: spot.longitude }}
            title={spot.spot_name}
            description={`Priority: ${spot.priority}`}
            pinColor={getColorForQuality(spot.current_quality_score)}
          />
        ))}
      </MapView>

      <Button
        title={adding ? "Tap map to add spot" : "Add Favorite Spot"}
        onPress={() => setAdding(!adding)}
      />
    </View>
  );
}
```

#### Day 18-19: Session Logger
```typescript
// src/screens/LogSession.tsx
export function LogSessionScreen() {
  const [session, setSession] = useState({
    spot_name: '',
    rating: 5,
    waves_caught: 10,
    duration_minutes: 90,
    board_type: 'shortboard',
    notes: '',
  });

  return (
    <ScrollView>
      <SpotPicker
        value={session.spot_name}
        favorites={favoriteSpotsautocomplete}
        onChange={(v) => update({ spot_name: v })}
      />

      <StarRating
        label="How was it?"
        value={session.rating}
        onChange={(v) => update({ rating: v })}
      />

      <NumberInput
        label="Waves caught"
        value={session.waves_caught}
        onChange={(v) => update({ waves_caught: v })}
      />

      <DurationPicker
        label="Session length"
        value={session.duration_minutes}
        onChange={(v) => update({ duration_minutes: v })}
      />

      <BoardTypePicker
        value={session.board_type}
        onChange={(v) => update({ board_type: v })}
      />

      <TextArea
        label="Notes"
        placeholder="Conditions, crowd, highlights..."
        value={session.notes}
        onChange={(v) => update({ notes: v })}
      />

      <Button title="Save Session" onPress={saveSession} />
    </ScrollView>
  );
}
```

#### Day 20-21: TestFlight Submission
```bash
# 1. Configure app.json
{
  "expo": {
    "name": "SwellSense",
    "slug": "swellsense",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "app.swellsense",
      "buildNumber": "1",
      "supportsTablet": true,
      "infoPlist": {
        "NSHealthShareUsageDescription": "SwellSense syncs your surf sessions to provide personalized recommendations",
        "NSHealthUpdateUsageDescription": "SwellSense can log surf sessions to HealthKit",
        "NSLocationWhenInUseUsageDescription": "SwellSense uses your location to find nearby surf spots",
        "NSLocationAlwaysAndWhenInUseUsageDescription": "SwellSense alerts you when you're near good surf spots"
      }
    }
  }
}

# 2. Build for TestFlight
eas build --platform ios

# 3. Submit to App Store Connect
eas submit --platform ios

# 4. Create TestFlight group
- Add 10 beta testers (friends, local surfers)
- Send invite links

# 5. Beta test for 1 week
- Fix critical bugs
- Gather feedback
- Iterate on alert timing/quality
```

---

## 📊 Success Metrics (Beta Phase)

**Week 1 Targets:**
- 10 beta testers
- 50+ sessions logged (5 per user average)
- 100+ alerts sent
- 40%+ notification open rate

**Red Flags to Watch:**
- < 20% notification open rate → alerts not valuable
- Users disable daily brief → timing or quality issues
- No sessions logged after 1 week → onboarding problem

**Green Lights:**
- Users add 3+ favorite spots → engagement
- Users log sessions within 2 hours of alert → conversion
- Users invite friends → viral potential

---

## 🚀 Launch Checklist

### Backend (Railway)
- [ ] Run database migrations (create new tables)
- [ ] Deploy alert endpoints
- [ ] Set up background jobs (Celery or Railway Cron)
- [ ] Configure Expo Push Notifications credentials
- [ ] Add environment variable: `EXPO_PUSH_TOKEN`

### Mobile App (Expo)
- [ ] Request HealthKit permissions in onboarding
- [ ] Request notification permissions
- [ ] Request location permissions (always)
- [ ] Test background sync (leave app, wait 6 hours, check sessions)
- [ ] Test push notifications (send test from backend)
- [ ] Test on 3+ devices (iPhone 12+, iOS 16+)

### App Store
- [ ] Apple Developer account ($99/year)
- [ ] Create app in App Store Connect
- [ ] Upload screenshots (6.5", 5.5" displays)
- [ ] Write App Store description
- [ ] Add privacy policy URL
- [ ] Submit for TestFlight review (24-48 hour approval)

---

## 🎯 Post-Launch (Week 4+)

### Phase 2 Features (Month 2)
1. **Spot Discovery**
   - Interactive map with all PR spots
   - "Find spots" search with filters
   - Community ratings

2. **Buddy System**
   - Invite friends
   - See where buddies are surfing
   - Session invites ("Domes tomorrow 7 AM?")

3. **Dawn Patrol Integration**
   - Reach out to founder with partnership proposal
   - OAuth integration for session import
   - Co-marketing campaign

### Phase 3 Features (Month 3-4)
1. **AI Learning Engine**
   - Analyze session history vs alerts
   - Personalize quality scoring
   - Improve daily brief ranking

2. **Widgets**
   - Home screen widget with top spot
   - Lock screen live activity during sessions

3. **Apple Watch**
   - Glanceable conditions
   - Session tracking
   - Quick log after session

---

## 💰 Acquisition Roadmap

**Month 1-2:** Get to 100 active users in Puerto Rico
- Local surf shops
- Facebook groups
- Instagram ads ($500 budget)

**Month 3-4:** Expand to Florida + SoCal (500 users)
- Partner with Dawn Patrol (if possible)
- Surf magazine features (Stab, Surfer)
- Reddit /r/surfing

**Month 5-6:** Reach 5,000 users across US
- 8% conversion to Pro ($4.99/month) = 400 paying
- $2,000 MRR = $24K ARR
- Approach Surfline with acquisition discussion

**Acquisition Pitch:**
> "We have 5,000 engaged surfers with 25,000+ logged sessions. Our AI knows what each user prefers based on real data, not just pageviews. Our users open push notifications 45% of the time (industry average: 10%). We're the personalization layer you need. Acquire us for $2-5M and integrate into Surfline Premium."

---

## 🛠 Tech Stack Summary

**Backend (Keep Existing):**
- FastAPI + PostgreSQL (Neon)
- Supabase auth
- OpenAI GPT-4
- Railway hosting

**Mobile (New):**
- React Native + Expo
- Expo Push Notifications
- Expo HealthKit
- Expo Location
- Expo BackgroundFetch

**Key Advantages:**
- One codebase for iOS + Android
- Free push notifications (Expo)
- No Xcode required for development
- Fast iteration cycle (OTA updates)

---

## ⚡ The TLDR: 3-Week Launch

1. **Week 1:** Backend (alerts API, daily brief logic, push notifications)
2. **Week 2:** Mobile app (Expo setup, HealthKit, screens)
3. **Week 3:** Polish + TestFlight (10 beta testers)

**Key Innovation:** HealthKit background sync = zero friction session tracking

**Differentiator:** AI learns from REAL sessions, not just browsing behavior

**Moat:** Network effects (buddy system) + data advantage (session history)

**Exit:** Surfline acquisition in 6-12 months at $2-5M valuation

---

**Ready to start building?** Want me to scaffold the Expo project structure first, or start with the backend alert endpoints?
