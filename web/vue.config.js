module.exports = {
  transpileDependencies: [
    'vuetify'
  ],
  devServer: {
    port: 8080,
    host: 'localhost'
  },
  pwa: {
    name: 'HinaV',
    themeColor: '#ffffff',
    msTileColor: '#000000',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    iconPaths: {
      favicon32: 'favicon.ico',
      favicon16: 'favicon.ico',
      appleTouchIcon: 'icon-apple.png',
      msTileImage: 'icon-512x512.png'
    },
    manifestOptions: {
      display: 'standalone',
      background_color: '#ffffff',
      icons: [
        {
          "src": "favicon.ico",
          "sizes": "48x48"
        },
        {
          "src": "icon-192x192.png",
          "sizes": "192x192",
          "type": "image/png"
        }, 
        {
          "src": "icon-apple.png",
          "sizes": "142x142",
          "type": "image/png"
        },
        {
          "src": "icon-256x256.png",
          "sizes": "256x256",
          "type": "image/png"
        },
        {
          "src": "icon-384x384.png",
          "sizes": "384x384",
          "type": "image/png"
        },
        {
          "src": "icon-512x512.png",
          "sizes": "512x512",
          "type": "image/png"
        },
      ],
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
