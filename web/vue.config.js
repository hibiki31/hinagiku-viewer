module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  pwa: {
    iconPaths: {
      favicon32: 'favicon.ico',
      favicon16: 'favicon.ico',
      appleTouchIcon: 'icon-192x192.png'
    },
    workboxOptions: {
      skipWaiting: true
    },
    runtimeCaching: [
      {
        urlPattern: /.*\/api\/.*/,
        handler: 'staleWhileRevalidatet',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 300
          },
          cacheableResponse: {
            statuses: [0, 200]
          }
        }
      },
      {
        urlPattern: /.*\/media\/.*/,
        handler: 'cacheFirst',
        options: {
          cacheName: 'media-cache',
          expiration: {
            maxEntries: 10,
            maxAgeSeconds: 300
          },
          cacheableResponse: {
            statuses: [0, 200]
          }
        }
      }
    ]
  }
}
