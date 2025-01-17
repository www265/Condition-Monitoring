/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./public/index.html", // 包含 public 文件夹中的 HTML 文件
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 包括 src 文件夹中的所有 .vue、.js、.ts 等文件
    "./src/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}