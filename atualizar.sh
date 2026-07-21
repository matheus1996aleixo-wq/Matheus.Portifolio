#!/bin/bash
echo "🚀 Sincronizando com o GitHub..."
git add .
read -p "Digite a mensagem do commit: " msg
git commit -m "$msg"
git push origin main
echo "✨ Atualizado com sucesso!"
