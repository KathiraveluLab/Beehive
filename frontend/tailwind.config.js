/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#facc15', // yellow-400
          dark: '#eab308', // yellow-500
        }
      }
    },
  },
  plugins: [],
} 