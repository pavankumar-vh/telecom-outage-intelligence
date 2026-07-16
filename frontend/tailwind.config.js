/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0f0f0f',
          800: '#1a1a1a',
          700: '#2d2d2d',
          600: '#404040',
        },
        brand: {
          primary: '#ff6b6b',
          secondary: '#4ecdc4',
        }
      }
    },
  },
  plugins: [],
}
