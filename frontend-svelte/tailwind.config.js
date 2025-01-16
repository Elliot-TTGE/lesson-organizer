/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,svelte,js,ts}"],
  theme: {
    extend: {},
  },
  plugins: [
    require('daisyui'),
  ],

  daisyui: {
    themes: [
      {
        "light": {
        "primary": "#ab8cc0",
        "secondary": "#483248",
        "accent": "#80cac3",
        "neutral": "#e7f1f3",
        "base-100": "#572b7a"
      }}
    ]
  }
}

