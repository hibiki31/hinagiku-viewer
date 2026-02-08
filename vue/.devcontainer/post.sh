#!/bin/bash

pnpm install
echo alias ppp='pnpm' >> /root/.bashrc 

curl -fsSL https://claude.ai/install.sh | bash

echo 'export PATH="$HOME/.local/bin:$PATH"' >> /root/.bashrc && source /root/.bashrc