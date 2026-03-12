/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          blue: '#0071e3',
          blueLight: '#42a5f5',
          gray: '#1d1d1f',
          grayMuted: '#86868b',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 2px 12px rgba(0,0,0,0.06)',
        'soft-lg': '0 4px 24px rgba(0,0,0,0.08)',
      },
    },
  },
  plugins: [],
}
