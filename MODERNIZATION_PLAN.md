# Modernization Plan: Web Assets Migration

## Overview
Transition the web assets from legacy JavaScript to modern tooling and practices while maintaining current functionality.

## 1. Dependency Management & Build System

### 1.1 Initialize Package Management
- **Action**: Create `package.json` with npm/yarn
- **Dependencies to add**:
  - `three` (latest stable version, currently ~0.160.x)
  - `tweenjs/tween.js` (modern version of TweenMax)
  - Dev dependencies: bundler, linter, type checker
- **Remove**: Direct CDN script tags from `index.html`

### 1.2 Build System Setup
- **Tool**: Vite or Webpack 5
- **Rationale**: 
  - Vite: Faster dev server, simpler config, native ES6 support
  - Webpack: More mature, better plugin ecosystem
- **Configuration**:
  - Entry point: Convert `tsne.js` to ES6 module
  - Output: Bundled `main.js` with source maps
  - Dev server with hot reload
  - Production build with minification

### 1.3 Security Scanning
- **Tools**:
  - `npm audit` (built-in, runs on install)
  - GitHub Dependabot (automated PRs for updates)
  - `snyk` or `socket.dev` for deeper scanning
- **Process**:
  - Add `npm audit` to CI/CD pipeline
  - Weekly automated dependency updates
  - Policy: No high/critical vulnerabilities in production

## 2. ES6 Module Migration

### 2.1 File Structure Reorganization
```
src/clip_plot/web/assets/js/
├── main.js              (entry point)
├── core/
│   ├── Config.js        (Config class)
│   ├── World.js         (World class)
│   └── Data.js          (Data class)
├── rendering/
│   ├── Texture.js       (Texture class)
│   ├── Atlas.js         (Atlas class)
│   ├── Cell.js          (Cell class)
│   └── shaders/
│       ├── vertex.js    (shader code)
│       └── fragment.js  (shader code)
├── layout/
│   ├── Layout.js        (Layout class)
│   └── Hotspots.js      (Hotspots class)
├── interaction/
│   ├── Picker.js        (Picker class)
│   └── Controls.js      (Controls wrapper)
└── utils/
    ├── api.js           (get, getPath, etc.)
    └── helpers.js       (utility functions)
```

### 2.2 Conversion Strategy
- **Phase 1**: Extract each "class" from `tsne.js` into separate files
- **Phase 2**: Convert function constructors to ES6 classes
  ```javascript
  // Before
  function Config() { this.data = {}; }
  Config.prototype.method = function() {}
  
  // After
  export class Config {
    constructor() { this.data = {}; }
    method() {}
  }
  ```
- **Phase 3**: Replace global variables with proper imports/exports
- **Phase 4**: Move shader code from `<script>` tags to `.glsl` or `.js` files

### 2.3 Import/Export Pattern
```javascript
// main.js
import { Config } from './core/Config.js';
import { World } from './core/World.js';
import { Layout } from './layout/Layout.js';

// Initialize application
const config = new Config();
const world = new World();
const layout = new Layout();
```

## 3. Three.js Modernization

### 3.1 Version Migration
- **Current**: Likely r90-r100 (several years old)
- **Target**: r160+ (latest stable)
- **Breaking Changes** to address:
  - `THREE.Geometry` → `THREE.BufferGeometry` (already using)
  - `THREE.TrackballControls` → Import from `three/examples/jsm/controls/TrackballControls.js`
  - Shader material API changes (likely minimal)
  - Texture handling updates

### 3.2 Import Strategy
```javascript
// Modern imports
import * as THREE from 'three';
import { TrackballControls } from 'three/addons/controls/TrackballControls.js';
import { FlyControls } from 'three/addons/controls/FlyControls.js';
```

### 3.3 Testing Approach
- Create visual regression tests (screenshots before/after)
- Test all layouts, transitions, and interactions
- Verify shader rendering is identical

## 4. Code Refactoring for Readability

### 4.1 Remove Legacy LOD System
- **Current state**: `config.useMipmaps = true` already uses mipmaps
- **Actions**:
  - Remove `LOD` class entirely (lines dealing with `lod.indexCells()`, etc.)
  - Remove `config.useMipmaps` flag (always use mipmaps)
  - Remove `lod.tex`, `lod.state`, `lod.clear()` references
  - Clean up `Cell.prototype.activate()` / `deactivate()` methods
  - Simplify texture index logic (no -1 for LOD texture)

### 4.2 General Refactoring

#### 4.2.1 Replace Callback Hell with Async/Await
```javascript
// Before
Data.prototype.load = function() {
  get(path, function(json) {
    get(path2, function(data) {
      this.parseManifest(data);
    }.bind(this))
  }.bind(this))
}

// After
async load() {
  const json = await fetch(path).then(r => r.json());
  const data = await fetch(path2).then(r => r.json());
  this.parseManifest(data);
}
```

#### 4.2.2 Modern DOM Queries
```javascript
// Replace custom getElem() with standard methods
// Use querySelector/querySelectorAll consistently
// Consider adding type hints with JSDoc
```

#### 4.2.3 Replace TweenMax with TWEEN.js
```javascript
// Before
TweenMax.to(animatable, duration, ease);

// After
import TWEEN from '@tweenjs/tween.js';
new TWEEN.Tween(animatable)
  .to({/* targets */}, duration)
  .easing(TWEEN.Easing.Power1.Out)
  .start();
```

#### 4.2.4 Event Listener Cleanup
- Move to ES6 class methods with arrow functions (no more `.bind(this)`)
- Add event listener cleanup in destructor/cleanup methods
- Consider event delegation where appropriate

#### 4.2.5 Configuration Management
- Separate feature flags from core config
- Use environment variables for debug mode
- Type-safe config object (consider TypeScript or JSDoc)

### 4.3 Code Quality Standards
- **Linting**: ESLint with modern ruleset
- **Formatting**: Prettier with consistent config
- **Documentation**: JSDoc comments for public APIs
- **Naming**: Use camelCase consistently, descriptive names

## 5. Implementation Phases

### Phase 1: Setup
- [ ] Initialize package.json
- [ ] Set up build system (Vite recommended)
- [ ] Configure ESLint, Prettier
- [ ] Set up security scanning

### Phase 2: Module Conversion
- [ ] Extract classes from tsne.js into separate files
- [ ] Convert to ES6 classes
- [ ] Set up proper import/export chain
- [ ] Move shaders to separate files
- [ ] Update index.html to load bundled JS

### Phase 3: Three.js Upgrade
- [ ] Upgrade Three.js dependency
- [ ] Update import statements
- [ ] Fix breaking changes
- [ ] Visual regression testing
- [ ] Performance testing

### Phase 4: Code Refactoring
- [ ] Remove LOD system completely
- [ ] Convert callbacks to async/await
- [ ] Replace TweenMax with TWEEN.js
- [ ] Modernize DOM queries
- [ ] Clean up event listeners

### Phase 5: Testing & Polish
- [ ] Comprehensive testing of all features
- [ ] Performance benchmarking
- [ ] Documentation updates
- [ ] Security audit

## 6. Risk Mitigation

### 6.1 Testing Strategy
- Keep old version running in parallel during migration
- A/B test with subset of users
- Comprehensive manual testing checklist
- Consider adding automated tests (Playwright/Cypress)

### 6.2 Rollback Plan
- Tag current version in git before starting
- Keep old HTML/JS files in separate directory
- Feature flag for new vs old code path
- Can revert by pointing HTML to old assets

### 6.3 Breaking Changes to Watch
- WebGL context handling changes
- Shader compilation differences between Three.js versions
- Browser compatibility (but ES6 modules widely supported now)
- Performance regressions (bundle size, runtime)

## 7. Success Metrics

- [ ] Zero high/critical security vulnerabilities
- [ ] Bundle size < 500KB (gzipped)
- [ ] All existing functionality works identically
- [ ] Code maintainability score improved (via linter metrics)
- [ ] Build time < 10 seconds
- [ ] Hot reload working in development

## 8. Out of Scope (Explicitly)
- UI/UX enhancements
- New features or capabilities
- Performance optimizations beyond refactoring
- Mobile-specific improvements
- Additional layouts or visualizations
