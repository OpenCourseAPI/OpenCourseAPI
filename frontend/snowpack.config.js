module.exports = {
  plugins: [
    '@snowpack/plugin-dotenv',
    // Optimize production builds with Webpack
    ['@snowpack/plugin-webpack', {}]
  ]
}
