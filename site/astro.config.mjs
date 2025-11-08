// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://danielrosehill.github.io',
  base: process.env.NODE_ENV === 'production' ? '/OR-Models-With-Tools-0811' : '/',
});
