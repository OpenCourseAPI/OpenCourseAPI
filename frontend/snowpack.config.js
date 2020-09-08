// TODO: this is not an officially supported way of using the plugin
// and may break with an update
require('@snowpack/plugin-dotenv')()

let API_URL;

if (process.env.NODE_ENV == 'development') {
  API_URL = process.env.SNOWPACK_PUBLIC_API_URL || 'http://localhost:5001/'
  process.env.SNOWPACK_PUBLIC_API_URL = '/api'
}

module.exports = {
  mount: {
    'src': '/',
    'static': '/'
  },
  plugins: [
    // Optimize production builds with Webpack
    ['@snowpack/plugin-webpack', {}]
  ],
  proxy: {
    '/api': API_URL,
  }
}
