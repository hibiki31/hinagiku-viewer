# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

hinagiku-viewer is a web application for managing and viewing books (zip files containing images). This `vue/` directory contains the Vue 3 + Vite frontend, which is the modern rewrite of the original Vue 2 (`web/`) frontend. The backend is a FastAPI app (`api/`), with PostgreSQL for storage. The full stack is deployed via Docker Compose with Nginx serving the SPA and reverse-proxying `/api` requests.

## Commands

```bash
pnpm install          # Install dependencies
pnpm dev              # Dev server at http://localhost:3000
pnpm build            # Parallel type-check + vite build
pnpm build-only       # Vite build only (skip type-check)
pnpm type-check       # vue-tsc --build --force
pnpm lint             # ESLint with --fix
```

### Regenerate API types from the OpenAPI spec

```bash
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
```

## Architecture

### Routing (file-based)

Routes are auto-generated from `src/pages/` via `unplugin-vue-router`. Dynamic segments use bracket syntax (e.g., `src/pages/books/[uuid].vue` → `/books/:uuid`). Layouts live in `src/layouts/` and are applied via `vite-plugin-vue-layouts`.

The router (`src/router/index.ts`) has a `beforeEach` guard that redirects unauthenticated users to `/login` and logged-in users away from `/login`.

### State Management (Pinia)

- **`stores/userData.ts`** — Auth state: `isAuthed`, `accessToken` (stored in cookie), `username`. Handles login/logout/token validation.
- **`stores/readerState.ts`** — Book listing and reading state: `booksList`, `booksCount`, `readerPage`, `showListMode` (table vs thumbnails), `openBook`, `searchQuery` (persisted to localStorage). Contains `serachBooks()` action for fetching from API.
- **`stores/auth.ts`** — Auth configuration (baseURL, token state).

### API Layer

- **`func/axios.ts`** — Axios instance configured with `VITE_APP_API_HOST` from `.env.local`.
- **`func/client.ts`** — `openapi-fetch` client with Bearer token middleware. Use this for type-safe API calls.
- **`src/api.d.ts`** — Auto-generated TypeScript types from FastAPI's OpenAPI spec. Key types: `BookBase`, `GetLibrary`, `AuthorGet`, `SearchQuery`.

### Authentication Flow

1. `App.vue` on mount: checks `accessToken` cookie → validates via `/api/auth/validate` → updates store.
2. Login: POST `/api/auth` with `URLSearchParams` (form-encoded) → store token in cookie + axios headers.
3. Axios interceptor in `App.vue`: on 401 response → logout and reload.

### Auto-imports

Vue APIs (`ref`, `computed`, `watch`, etc.) and `useRoute`/`useRouter` are auto-imported via `unplugin-auto-import`. Vuetify and custom components are auto-imported via `unplugin-vue-components`. The generated declaration files (`auto-imports.d.ts`, `components.d.ts`, `typed-router.d.ts`) are committed to the repo.

### Composables

- **`composables/utility.ts`** — `useConvertNumFormat()` (Japanese number formatting like "1.0万"), `useConvertDateFormat()`, `usePushNotice()` (toast notifications), `useApiErrorHandler()`, `useGetCoverURL()`, `useFitByte()`.
- **`composables/rules.ts`** — Form validation rules.

### Styling

Vuetify 3 with custom theme in `src/plugins/vuetify.ts` (primary: `#082240`, success: `#22663f`). SCSS settings in `src/styles/settings.scss` using the modern-compiler API. `@` is aliased to `src/`.

## Conventions

- Git commit messages in Japanese.
- Code comments in Japanese.
- Components use `<script setup lang="ts">` with Composition API.
- The `@` path alias resolves to `src/`.
- Environment variable for API host: `VITE_APP_API_HOST` (set in `.env.local`).
