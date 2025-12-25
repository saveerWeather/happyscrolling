/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#d97556',
          50: '#fef5f1',
          100: '#fce8df',
          200: '#f9d0c0',
          300: '#f4af96',
          400: '#ed866a',
          500: '#d97556',
          600: '#c96543',
          700: '#b55533',
          800: '#9e4628',
          900: '#7a3520',
        },
        cream: {
          DEFAULT: '#faf8f3',
          50: '#fdfcfa',
          100: '#faf8f3',
          200: '#f5f1e8',
          300: '#ebe6d8',
        },
        sage: {
          DEFAULT: '#8b9d83',
          400: '#9fb08f',
          500: '#8b9d83',
          600: '#778a6f',
          700: '#63765c',
        },
        warm: {
          100: '#f5f4f0',
          200: '#e8e6e0',
          300: '#d4d1c8',
          400: '#b8b5ac',
          500: '#938f84',
          600: '#6f6b62',
          700: '#504d45',
          800: '#3a3832',
          900: '#252320',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
