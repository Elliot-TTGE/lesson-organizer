import { defineConfig } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    sveltekit(),
    tailwindcss()
  ],
  server: {
    allowedHosts: ['127.0.0.1:4000', 'lessonorganizer']
  }
});
