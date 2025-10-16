# SwellSense App Icon

## Files
- `app-icon.svg` - Vector source file (1024x1024)
- Convert this to PNG for Facebook app submission

## Converting SVG to PNG (1024x1024)

### Option 1: Using Online Tools
1. Go to https://svgtopng.com or https://cloudconvert.com/svg-to-png
2. Upload `app-icon.svg`
3. Set dimensions to 1024x1024
4. Download PNG

### Option 2: Using ImageMagick (Mac/Linux)
```bash
# Install ImageMagick if needed
brew install imagemagick

# Convert to PNG
convert -background none -resize 1024x1024 app-icon.svg app-icon-1024.png
```

### Option 3: Using Inkscape
1. Open `app-icon.svg` in Inkscape
2. File → Export PNG Image
3. Set width/height to 1024px
4. Export

### Option 4: Using GIMP
1. Open `app-icon.svg` in GIMP
2. Set import size to 1024x1024
3. File → Export As → PNG

## Icon Design
- **Background**: Ocean blue gradient (#0EA5E9 to #0369A1)
- **Waves**: Three-layer wave design representing surf conditions
- **AI Symbol**: Neural network circuit design in gold/amber
- **Branding**: "SwellSense" text with "AI Surf Forecasts" tagline

## Usage
- Facebook App Icon: 1024x1024 PNG
- iOS App Icon: Use various sizes (see Apple guidelines)
- Android App Icon: Use various sizes (see Android guidelines)
- Web Favicon: Create smaller versions (16x16, 32x32, 192x192, 512x512)
