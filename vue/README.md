

## 起動

```
yarn install
yarn run dev
```

## openapi-ts

```
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
npx openapi-typescript http://172.21.0.3:8000/api/openapi.json -o ./src/api.d.ts
npx openapi-typescript ../api/openapi.json -o ./src/api.d.ts
```


## プロジェクトの立ち上げ

WSL2にVoltaをインストール

```
curl https://get.volta.sh | bash
volta install node
```

プロジェクトの作成

```
akane@DESKTOP-KOTONE:~/hinagiku-viewer$ npm create vuetify@latest
Need to install the following packages:
create-vuetify@2.3.1
Ok to proceed? (y) y


> npx
> create-vuetify


Vuetify.js - Material Component Framework for Vue

✔ Project name: … vue
✔ Which preset would you like to install? › Recommended (Everything from Default. Adds auto importing, layouts & pinia)
✔ Use TypeScript? … No / Yes
✔ Would you like to install dependencies with yarn, npm, pnpm, or bun? › yarn
✔ Install Dependencies? … No / Yes
```

```
yarn add @kyvg/vue3-notification
yarn add axios
yarn add js-cookie
yarn add -D @types/js-cookie
```