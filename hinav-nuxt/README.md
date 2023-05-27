
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




# Nuxt 3 Minimal Starter

Look at the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install the dependencies:

```bash
# yarn
yarn install

# npm
npm install

# pnpm
pnpm install
```

## Development Server

Start the development server on `http://localhost:3000`

```bash
npm run dev
```

## Production

Build the application for production:

```bash
npm run build
```

Locally preview production build:

```bash
npm run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.

