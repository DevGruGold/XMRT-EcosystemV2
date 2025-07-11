#!/bin/bash
# Nuclear solution for PNPM version issues
echo "Forcing PNPM 8 installation..."
npm install -g pnpm@8 > /dev/null 2>&1
pnpm -v
