
# Create project

```
docker run -it --rm -v ${PWD}:/app  node:18.16 bash
npx nuxi init hinav-nuxt
exit
```


```
cd hinav-nuxt
cat << EOF > Dockerfile.dev
FROM node:18.16
EOF
```

```
mkdir .devcontainer
cat << EOF > ./.devcontainer/devcontainer.json
{
	"name": "hinav-nuxt",
	"context": "..",
	"dockerFile": "../Dockerfile.dev",
	"forwardPorts": [
		8080
	],
	"mounts": [
		"source=try-hinav_node_modules,target=${containerWorkspaceFolder}/node_modules,type=volume"
	]
}
EOF
```

# Settings

```
yarn install 
yarn add vuetify@next @mdi/font
yarn add sass vite-plugin-vuetify
```

```
 yarn dev
 yarn build
 node .output/server/index.mjs
```

## 参考

- Axios
  - https://www.memory-lovers.blog/entry/2022/06/02/170000
- Auth middle
  - https://debug-life.net/entry/4169
- Nuxt3 Vuetify
  - https://zenn.dev/coedo/articles/nuxt3-vuetify3