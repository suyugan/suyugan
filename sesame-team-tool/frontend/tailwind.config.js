/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        grayBtn: '#E5E5EA',
        textGray: '#8A8A8E',
        stepBlue: '#007AFF',
        greenBtn: '#06C160',
        cardBg: '#FFFFFF',
        bgPage: '#F5F5F7',
      },
      fontFamily: {
        apple: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
