# Facebook App Integration - SwellSense

## Required URLs for Facebook App Dashboard

### Privacy Policy URL
```
https://swellsense.app/privacy
```

### Terms of Service URL
```
https://swellsense.app/terms
```

### Data Deletion URLs (Choose ONE)

**Option 1: Callback URL (Recommended)**
```
https://api.swellsense.app/api/facebook/data-deletion
```
Facebook will automatically POST to this endpoint when users delete the app.

**Option 2: Instructions URL**
```
https://swellsense.app/data-deletion
```
Users will be directed to this page with instructions on how to request deletion.

## App Icon Requirements

### File Location
- **Source SVG**: `frontend/app-icon.svg`
- **Required Format**: PNG, 1024x1024 pixels
- **Background**: Must be opaque (no transparency for Facebook)

### Converting SVG to PNG

**Option 1: Online (Easiest)**
1. Go to https://svgtopng.com or https://cloudconvert.com/svg-to-png
2. Upload `frontend/app-icon.svg`
3. Set dimensions to 1024x1024
4. Download PNG
5. Upload to Facebook App Dashboard

**Option 2: Command Line (Mac/Linux)**
```bash
cd frontend
convert -background white -resize 1024x1024 app-icon.svg app-icon-1024.png
```

## Icon Design Details
- **Background**: Ocean blue gradient (#0EA5E9 to #0369A1)
- **Waves**: Three-layer wave design (cyan/turquoise)
- **AI Symbol**: Neural network circuit in gold/amber (#F59E0B, #FBBF24)
- **Text**: "SwellSense" + "AI Surf Forecasts" tagline
- **Style**: Modern, professional, instantly recognizable

## Facebook App Setup Checklist

### Basic Settings
- [ ] App Name: SwellSense
- [ ] App Icon: 1024x1024 PNG (converted from app-icon.svg)
- [ ] Privacy Policy URL: https://swellsense.app/privacy
- [ ] Terms of Service URL: https://swellsense.app/terms
- [ ] Category: Weather / Sports / Entertainment

### App Domains
- [ ] Add domain: `swellsense.app`
- [ ] Add domain: `vercel.app` (if using Vercel preview URLs)

### Facebook Login Settings
- [ ] Valid OAuth Redirect URIs:
  - `https://swellsense.app/api/auth/callback/facebook`
  - `http://localhost:3000/api/auth/callback/facebook` (for development)
- [ ] Data Deletion Callback URL: `https://api.swellsense.app/api/facebook/data-deletion`
  - OR Data Deletion Instructions URL: `https://swellsense.app/data-deletion`

### Permissions to Request
- `email` (required for account creation)
- `public_profile` (name, profile picture)

### App Review (if needed)
- Most apps only need `email` and `public_profile` which don't require review
- If requesting additional permissions, prepare:
  - Screenshots showing how each permission is used
  - Step-by-step usage instructions
  - Privacy policy explaining data usage

## Environment Variables

Add these to your Vercel environment variables:

```bash
FACEBOOK_APP_ID=your_facebook_app_id_here
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
```

## Testing

### Development Testing
1. Add test users in Facebook App Dashboard → Roles → Test Users
2. Use test users to log in during development
3. Test data deletion flow

### Production Testing
1. Keep app in Development Mode initially
2. Add real accounts as Developers/Testers in Roles section
3. Test all authentication flows
4. Test on mobile devices
5. Switch to Live Mode when ready

## Compliance Notes

### Privacy Policy Covers
✅ Data collection (email, name, location searches)
✅ Third-party data sources (NOAA, OpenWeather, etc.)
✅ AI/ML processing disclosure
✅ User rights (access, deletion, portability)
✅ Cookie usage
✅ International data transfers
✅ Children's privacy (COPPA - age 13+)
✅ Contact information

### Terms of Service Covers
✅ Service description (AI surf forecasts)
✅ Forecast disclaimer (safety warning)
✅ User account terms
✅ Acceptable use policy
✅ Intellectual property rights
✅ Limitation of liability
✅ Dispute resolution / Arbitration
✅ Governing law (California)

## Deployment Status

✅ Privacy policy deployed at `/privacy`
✅ Terms of service deployed at `/terms`
✅ App icon SVG created (needs PNG conversion)
✅ All changes committed and pushed to GitHub
✅ Vercel will auto-deploy updated pages

## Next Steps

1. **Convert Icon**: Use one of the methods above to create 1024x1024 PNG
2. **Facebook Dashboard**: Create/configure your Facebook App
3. **Add URLs**: Input privacy/terms URLs in Facebook settings
4. **Upload Icon**: Add the 1024x1024 PNG icon
5. **Get Credentials**: Copy App ID and App Secret
6. **Update Vercel**: Add FACEBOOK_APP_ID and FACEBOOK_APP_SECRET
7. **Test**: Try Facebook login in development mode
8. **Go Live**: Switch Facebook app to Live mode when ready

## Support Resources

- Facebook App Setup Guide: https://developers.facebook.com/docs/apps/
- Facebook Login Integration: https://developers.facebook.com/docs/facebook-login/web
- App Review Guidelines: https://developers.facebook.com/docs/app-review/

---

**Created**: October 16, 2025
**Status**: Ready for Facebook App submission
**URLs**: Live at swellsense.app
