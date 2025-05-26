# Vue 2 -> Vue 3 Migration: TODO

This document outlines the first steps for migrating from vue2 to vue3.

---

## Setup & Branching

- [x] Create migration branch
    ``` 
    git checkout -b vue3-migration
    ```

---

## Dependency Audit

- [x] Audit current Vue-related dependencies
- [x] Identify incompatible packages:
  - `vue@2.7.16` -> needs `vue@3`
  - `vue-router@3` -> needs `vue-router@4`
  - `vuex@3` -> optional migration to `vuex@4`
  - `vuetify@2` -> major update to `vuetify@3`
  - `vue/test-utils@1.x` -> needs `@vue/test-utils@2`
  - `vue/vue2-jest` -> incompatible, needs `vue-jest@next`

---

## Clean Up

- [x] Remove old lock file and modules
    ```
    rm -rf node_modules package-lock.json
    ```

- [x] Uninstall Vue 2 packages:
    ```
    npm uninstall vue vue-router vuex vuetify vue-loader
    ```

---

## Install Vue 3 Stack

- [x] Install new core dependencies:
    ```
    npm install vue@3 vue-router@4 vuex@4
    npm install -D @vue/compiler-sfc vue-loader@^17
    ```

- [x] Fix SCSS errors by removing redundant @use "@/variables.scss"
- [x] Replace deprecated `::v-deep` with `:deep(...)`
- [x] Fix `template v-for` key warning (`key` moved to direct child)

---

## Update Testing Stack

- [ ] Uninstall legacy test packages:
    ```
    npm uninstall @vue/test-utils @vue/vue2-jest
    ```

- [ ] Install new test stack:
    ```
    npm install -D @vue/test-utils@2 vue-jest@next jest@latest babel-jest@latest
    ```

---

## Create New Entry Point

- [ ] Update `main.js` to use `createApp`
- [ ] Create test component with `<script setup>`

---

## First Run

- [ ] Run dev server and confirm basic Vue 3 component works:
    ```
    npm run serve
    ```

---

## Gradual Migration

- [x] Migrate multiple `.vue` components (cleanup plan, statistics)
- [x] Refactor deprecated syntax (v-for, scoped style, deep selectors)
- [ ] Replace options API with composition API (where applicable)
- [ ] Replace Vuetify 2 with Vuetify 3 (requires rewrite)

---

## Final Testing

- [ ] Run unit @ E2E tests
- [ ] Run full CodeChecker UI smoke test

---
