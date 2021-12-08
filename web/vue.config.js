module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  pwa: {
    name: 'HinaV',
    themeColor: '#ffffff',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    manifestOptions: {
      display: 'standalone',
      background_color: "#ffffff"
    },
    iconPaths: {
      favicon32: 'favicon.ico',
      favicon16: 'favicon.ico',
      appleTouchIcon: 'icon-apple.png',
      msTileImage: 'icon-512x512.png'
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
