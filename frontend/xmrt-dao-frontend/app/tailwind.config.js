/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'xmrt-dark': '#151520',
        'xmrt-purple': '#7C3AED',
        'xmrt-teal': '#0D9488',
      },
    },
  },
  plugins: [],
}
