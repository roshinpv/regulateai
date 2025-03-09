/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#D71E2B',
          dark: '#B01823',
          light: '#E84C56',
        },
        secondary: {
          DEFAULT: '#FFCD00',
          dark: '#E6B800',
          light: '#FFD633',
        },
        neutral: {
          DEFAULT: '#333333',
          dark: '#1A1A1A',
          light: '#666666',
          lighter: '#E5E5E5',
        },
        background: {
          DEFAULT: '#F8F9FA',
          dark: '#E9ECEF',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      },
    },
  },
  plugins: [],
};