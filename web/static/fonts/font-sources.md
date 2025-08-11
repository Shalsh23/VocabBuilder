# Web Font Sources and Implementation

## Fonts Used

### 1. Avalon (Regular - used as Bold alternative)
- **Source**: CDNFonts
- **Weight**: Regular (400) - Note: Bold weight not available, using regular with CSS font-weight
- **Local Path**: `/web/static/fonts/avalon/avalon-regular.woff`
- **CDN Link**: `https://fonts.cdnfonts.com/css/avalon`
- **Direct WOFF URL**: `https://fonts.cdnfonts.com/s/18770/AVALON__.woff`

### 2. Cormorant Garamond Light
- **Source**: Google Fonts
- **Weight**: Light (300)
- **CDN Link**: `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300&display=swap`
- **Implementation**: Using Google Fonts CDN directly (no local download needed)

## CSS Implementation

### For Avalon (Local Font):
```css
@font-face {
    font-family: 'Avalon';
    font-style: normal;
    font-weight: 700; /* Define as bold even though file is regular */
    src: url('/static/fonts/avalon/avalon-regular.woff') format('woff');
}
```

### For Cormorant Garamond Light (Google Fonts CDN):
```html
<!-- Add to HTML <head> -->
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300&display=swap" rel="stylesheet">
```

Or in CSS:
```css
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300&display=swap');
```

## Usage in CSS:
```css
/* For headings or bold text */
.avalon-bold {
    font-family: 'Avalon', sans-serif;
    font-weight: 700;
}

/* For light body text */
.cormorant-light {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 300;
}
```

## Notes:
- Avalon Bold is not available as a separate font weight, so we're using the regular weight and applying CSS font-weight: 700
- Cormorant Garamond Light is readily available from Google Fonts
- The Avalon font is stored locally as a WOFF file for better performance and reliability
- Consider converting to WOFF2 format for better compression if needed
