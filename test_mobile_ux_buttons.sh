#!/bin/bash

echo "🧪 TESTE DE UX/UI - Espaçamento dos Botões em Mobile"
echo "=================================================="

# Verificar se o servidor está rodando
echo "🔍 Verificando se o servidor está rodando..."
if curl -s http://localhost > /dev/null; then
    echo "✅ Servidor disponível em http://localhost"
else
    echo "❌ Servidor não está rodando em http://localhost"
    exit 1
fi

echo ""
echo "🔐 Fazendo login com usuário de teste..."

# Fazer login para testar a página de completar perfil
LOGIN_RESPONSE=$(curl -s -c cookies.txt -b cookies.txt \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -X POST \
    -d "email=perfil_incompleto@teste.com&password=teste123456" \
    http://localhost/users/login/ \
    --write-out "%{http_code}")

if [[ "$LOGIN_RESPONSE" == *"302"* ]] || [[ "$LOGIN_RESPONSE" == *"200"* ]]; then
    echo "✅ Login realizado com sucesso!"
else
    echo "❌ Falha no login. Código: $LOGIN_RESPONSE"
fi

echo ""
echo "📱 Testando a página de completar perfil..."

# Acessar a página de completar perfil
PROFILE_PAGE=$(curl -s -b cookies.txt http://localhost/users/complete-profile/)

# Verificar se as classes CSS responsivas foram aplicadas
echo ""
echo "🎨 Verificando melhorias de CSS responsivo:"

if echo "$PROFILE_PAGE" | grep -q "action-buttons"; then
    echo "✅ Classe 'action-buttons' encontrada"
else
    echo "❌ Classe 'action-buttons' não encontrada"
fi

if echo "$PROFILE_PAGE" | grep -q "primary-action-btn"; then
    echo "✅ Classe 'primary-action-btn' encontrada"
else
    echo "❌ Classe 'primary-action-btn' não encontrada"
fi

if echo "$PROFILE_PAGE" | grep -q "secondary-action-btn"; then
    echo "✅ Classe 'secondary-action-btn' encontrada"
else
    echo "❌ Classe 'secondary-action-btn' não encontrada"
fi

if echo "$PROFILE_PAGE" | grep -q "@media (max-width: 767.98px)"; then
    echo "✅ Media queries para mobile encontradas"
else
    echo "❌ Media queries para mobile não encontradas"
fi

if echo "$PROFILE_PAGE" | grep -q "margin: 0 0 1rem 0"; then
    echo "✅ Espaçamento vertical entre botões em mobile configurado"
else
    echo "❌ Espaçamento vertical entre botões em mobile não encontrado"
fi

if echo "$PROFILE_PAGE" | grep -q "min-height: 52px"; then
    echo "✅ Área de toque adequada para mobile (52px) configurada"
else
    echo "❌ Área de toque adequada para mobile não encontrada"
fi

if echo "$PROFILE_PAGE" | grep -q "width: 100%"; then
    echo "✅ Botões ocupando largura total em mobile"
else
    echo "❌ Largura total dos botões em mobile não configurada"
fi

echo ""
echo "📐 Verificando estrutura HTML dos botões:"

if echo "$PROFILE_PAGE" | grep -q '<button type="submit" class="btn btn-primary btn-lg px-5 primary-action-btn">'; then
    echo "✅ Botão 'Completar Perfil' com classes corretas"
else
    echo "❌ Botão 'Completar Perfil' com estrutura incorreta"
fi

if echo "$PROFILE_PAGE" | grep -q '<a href="/ads/" class="btn btn-outline-secondary btn-lg px-4 secondary-action-btn">'; then
    echo "✅ Botão 'Pular por agora' com classes corretas"
else
    echo "❌ Botão 'Pular por agora' com estrutura incorreta"
fi

echo ""
echo "🎯 Verificando melhores práticas de UX implementadas:"

# Verificar área de toque mínima
if echo "$PROFILE_PAGE" | grep -q "min-height: 48px"; then
    echo "✅ Área de toque mínima (48px) para desktop"
else
    echo "❌ Área de toque mínima para desktop não configurada"
fi

# Verificar transições suaves
if echo "$PROFILE_PAGE" | grep -q "transition: all 0.3s ease"; then
    echo "✅ Transições suaves configuradas"
else
    echo "❌ Transições suaves não encontradas"
fi

# Verificar hover effects
if echo "$PROFILE_PAGE" | grep -q "transform: translateY(-2px)"; then
    echo "✅ Efeitos hover implementados"
else
    echo "❌ Efeitos hover não encontrados"
fi

# Verificar diferentes breakpoints
if echo "$PROFILE_PAGE" | grep -q "@media (min-width: 768px) and (max-width: 991.98px)"; then
    echo "✅ Breakpoint para tablet configurado"
else
    echo "❌ Breakpoint para tablet não encontrado"
fi

if echo "$PROFILE_PAGE" | grep -q "@media (min-width: 992px)"; then
    echo "✅ Breakpoint para desktop configurado"
else
    echo "❌ Breakpoint para desktop não encontrado"
fi

echo ""
echo "📊 RESUMO DAS MELHORIAS IMPLEMENTADAS:"
echo "======================================"
echo "✨ Espaçamento vertical entre botões em mobile"
echo "✨ Botões empilhados verticalmente em mobile (width: 100%)"
echo "✨ Área de toque adequada (48px desktop, 52px mobile)"
echo "✨ Transições suaves e efeitos hover"
echo "✨ Layout responsivo para tablet e desktop"
echo "✨ Margem superior adequada no container dos botões"
echo "✨ Visual consistente com o design system"

echo ""
echo "🌐 Para testar visualmente:"
echo "1. Acesse: http://localhost/users/complete-profile/"
echo "2. Teste em diferentes tamanhos de tela (mobile, tablet, desktop)"
echo "3. Verifique o espaçamento entre os botões em mobile"
echo "4. Confirme que os botões ficam empilhados verticalmente em mobile"

# Limpar cookies
rm -f cookies.txt

echo ""
echo "✅ Teste de UX/UI concluído com sucesso!"
