const path = require('path')
const express = require('express')

const BUILD_DIR = path.resolve(__dirname, '../build')
const PORT = process.env.PORT || 8080

express()
  .use(express.static(BUILD_DIR))
  .get('*', function (req, res) {
    res.sendFile(path.resolve(BUILD_DIR, 'index.html'))
  })
  .listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`)
  })
