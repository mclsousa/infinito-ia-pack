# Pronto para vender

## Material entregue — visual editorial premium

Tudo em `entrega/` (gerado em 19/06/2026):

| Arquivo | Uso |
|---------|-----|
| **Conteudo-Infinito-IA.pdf** | Produto principal — enviar ao cliente |
| **Conteudo-Infinito-IA.html** | Mesma versão no navegador |
| **Order-Bump-Datas.pdf** | Extra sazonal (R$ 17 no checkout) |
| **Conteudo-Infinito-IA-PACK.zip** | Upload no Google Drive |
| **LEIA-ME.txt** | Instruções para o cliente |

Landing: `marketing/landing-page.html` (posicionamento: sistema, não "45 prompts")

---

## O que está pronto

- [x] 45 comandos + 2 anexos (calendário + checklist)
- [x] PDF com espaçamento ajustado
- [x] Nota anti-confusão no Anexo A (dia vs comando)
- [x] Landing, copy Cakto e roteiros TikTok alinhados (30 dias · 1 checklist · 6 situações)
- [x] Auditoria de redundância (`produto/auditoria-redundancia.md`)

---

## 3 passos manuais (você ainda precisa fazer)

### 1. Google Drive (~5 min)
Upload de `entrega/Conteudo-Infinito-IA-PACK.zip` → link compartilhável (qualquer pessoa com o link)

### 2. Cakto (~10 min)
- Textos prontos: `marketing/cakto-textos-prontos.md`
- Preço principal: **R$ 27**
- Order bump: **R$ 17** (Anexo Sazonal)
- Colar link do Drive no e-mail de entrega automática
- [x] Link checkout na landing: https://pay.cakto.com.br/37c4vf7_933986

### 3. TikTok
- Bio e roteiros: `marketing/roteiros-tiktok.md`
- Legendas: `marketing/legendas-hashtags.md`
- Demo: mostrar PDF aberto + um comando no ChatGPT

---

## Regenerar após edições no produto

```powershell
python scripts\gerar-pdf.py
```

Atualiza PDF, HTML e ZIP automaticamente.
