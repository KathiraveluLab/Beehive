# Frontend Development Setup

## Prerequisites
- Node.js 18+ and npm
- Git configured properly

## Initial Setup

```bash
# Install dependencies (generates package-lock.json locally)
npm ci

# Start development server
npm run dev

# Run ESLint checks
npm run lint
```

## Important Notes

### Package Lock File
- `package-lock.json` is **NOT** committed to avoid merge conflicts
- Always use `npm ci` for consistent installs across environments
- Local `package-lock.json` will be generated automatically

### ESLint Configuration
- Uses modern flat config format (`eslint.config.js`)
- Includes React rules for duplicate prop detection
- Run `npm run lint` to check for code quality issues

### Development Workflow
1. `npm ci` (first time setup)
2. `npm run dev` (start development)
3. `npm run lint` (check code quality)
4. `npm run build` (production build)

## Troubleshooting

**If you see dependency conflicts:**
```bash
rm -f package-lock.json node_modules -rf
npm ci
```

**If ESLint fails:**
```bash
npm run lint --fix  # Auto-fix issues where possible
```
