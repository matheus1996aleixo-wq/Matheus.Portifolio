#!/bin/bash
echo "🚀 Sincronizando com o GitHub..."
git add .
read -p "Digite a mensagem do commit: " msg
if [ -z "$msg" ]; then
    msg="Atualização e otimização do portfólio para GitHub"
fi
git commit -m "$msg"
git push origin main
echo "✨ Atualizado com sucesso!"