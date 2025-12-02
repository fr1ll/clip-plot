# Feature Flags in clip-plot

This document describes the feature flags available in the viewer and how to enable them.

## Location

All feature flags are set in `/src/clip_plot/web/assets/js/tsne.js` in the `Config()` constructor (around line 43).

## Available Flags

### 1. **useMipmaps** (default: `true`)
Controls which image detail system to use:
- `true`: Use GPU mipmaps for image detail (recommended, better performance)
- `false`: Use the legacy LOD (Level of Detail) system

**How to change:**
```javascript
function Config() {
  // ...
  this.useMipmaps = false;  // Enable LOD system
  // ...
}
```

**Notes:**
- Mipmaps provide hardware-accelerated image detail at all zoom levels
- LOD dynamically loads high-res images for nearby cells (more complex)
- Both systems work with the same `imagelist.json` manifest

### 2. **debug** (default: `false`)
Controls diagnostic console logging:
- `true`: Enable detailed logging for debugging
- `false`: Disable all diagnostic logs (cleaner console)

**How to enable:**

**Method 1: URL parameter ( runtime, no code changes):**
```
https://your-viewer-url/?debug=1
```

**Method 2: Console ( runtime, no code changes):**
```javascript
// Open browser console and type:
config.debug = true;
```

**Method 3: Source code change:**
```javascript
function Config() {
  // ...
  this.debug = true;  // Enable diagnostic logging
  // ...
}
```

**What gets logged when enabled:**
- Cell creation details (atlas positions, filenames, sizes)
- Atlas/texture loading and mapping information
- GPU picker mesh cloning and color attributes
- Draw call grouping information
- Color encoding for GPU picking
- Click detection and cell index mapping

## Quick Reference

```javascript
// In src/clip_plot/web/assets/js/tsne.js, Config() constructor:

function Config() {
  this.data = {
    dir: 'data',
    file: 'manifest.json',
    gzipped: false,
  }
  this.mobileBreakpoint = 600;
  this.isTouchDevice = 'ontouchstart' in document.documentElement;
  
  // FEATURE FLAGS
  this.useMipmaps = true;   // Set to false to use LOD system
  this.debug = new URLSearchParams(window.location.search).get('debug') === '1';  // Enable via ?debug=1
  
  // ... rest of config
}
```

## Testing Combinations

1. **Production (default):** `useMipmaps: true, debug: false`
   - Best performance, clean console

2. **Debug mipmaps:** `useMipmaps: true, debug: true`
   - Debug the mipmap system with detailed logs
   - Enable via: `?debug=1` or `config.debug = true`

3. **Test LOD:** `useMipmaps: false, debug: false`
   - Test the legacy LOD system

4. **Debug LOD:** `useMipmaps: false, debug: true`
   - Debug the LOD system with detailed logs
   - Enable via: `?debug=1` or `config.debug = true`
