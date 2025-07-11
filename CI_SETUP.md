# CI/CD Pipeline Setup

## Overview
This project uses a modern CI/CD pipeline with the following stack:
- **Package Manager**: pnpm 8.15.4
- **Node.js**: 20.x (LTS)
- **Framework**: React 19 + Vite
- **TypeScript**: Full type checking

## Pipeline Stages

### 1. Test & Build
- ✅ Dependency installation with pnpm
- ✅ TypeScript type checking
- ✅ ESLint code linting
- ✅ Unit tests execution
- ✅ Production build generation
- ✅ Build artifact upload

### 2. Deploy (main/master only)
- ✅ Artifact download
- ✅ Ready for deployment

## Local Development

### Prerequisites
```bash
# Install Node.js 20.x
nvm use 20.11.0

# Install pnpm globally
npm install -g pnpm@8.15.4
```

### Setup
```bash
# Navigate to app directory
cd app

# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Run type checking
pnpm run type-check

# Run linting
pnpm run lint

# Build for production
pnpm run build
```

## Troubleshooting

### Common Issues
1. **pnpm not found**: Install pnpm globally or use corepack
2. **Type errors**: Run `pnpm run type-check` to see TypeScript issues
3. **Build failures**: Check that all dependencies are installed with `pnpm install`

### React 19 Compatibility
- Using React 19 with TypeScript types v18.x for stability
- All peer dependencies are properly resolved
- Vite configuration optimized for React 19

## CI Configuration Files
- `.github/workflows/ci.yml` - Main CI pipeline
- `app/.nvmrc` - Node.js version specification
- `app/package.json` - Dependencies and scripts
- `app/pnpm-lock.yaml` - Dependency lock file
