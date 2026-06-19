# Anexo B — Protocolo de Revisão de Textos

Diretrizes para adequação de conteúdo gerado por ferramentas de linguagem natural ao padrão da marca.

---

## Diagnóstico: por que o texto parece genérico

Ferramentas de IA produzem saídas amplas quando o contexto de entrada é insuficiente. Campos como `[NICHO]`, `[PÚBLICO]` e `[PRODUTO]` devem ser preenchidos com dados específicos antes da execução.

**Requisito mínimo:** incluir três elementos de contexto — posicionamento da marca, exemplo real do negócio e restrições editoriais (tom, termos proibidos, limites de promessa).

---

## Protocolo de revisão em 5 etapas

### 1. Validação de entrada
Confirmar que todos os campos entre colchetes foram substituídos por dados reais. Entradas incompletas geram saídas padronizadas.

### 2. Reescrita de tom
Aplicar o comando de revisão abaixo para alinhar o texto ao padrão comunicacional da marca.

### 3. Edição de redundância
Eliminar repetições e frases de preenchimento. Redução de 15–20% no volume textual é recomendada.

### 4. Inclusão de evidência
Inserir um dado concreto: métrica, caso, prazo ou especificação do serviço. Conteúdo com evidência apresenta maior taxa de conversão.

### 5. Leitura em voz alta
Textos que apresentam hesitação na leitura oral devem ser simplificados antes da publicação.

---

## Expressões a evitar

| Evitar | Substituir por |
|--------|----------------|
| "No mundo digital de hoje..." | Entrada direta no assunto |
| "Oportunidade única" | Prazo ou condição específica |
| "Transforme sua vida" | Benefício mensurável |
| Excesso de emojis | Máximo 1–2 por peça, se aplicável ao canal |

---

## Comando auxiliar — revisão de tom

```
Atue como editor sênior de conteúdo corporativo.

Reescreva o texto abaixo conforme:
- Tom: [formal / consultivo / direto]
- Máximo: [X] palavras
- Remover clichês de marketing digital
- Manter CTA e hashtags

Texto:
[COLE AQUI]
```

---

## Checklist pré-publicação

- [ ] Campos do comando preenchidos integralmente
- [ ] Leitura em voz alta realizada
- [ ] Clichês removidos
- [ ] Dado concreto do negócio incluído
- [ ] CTA verificado
- [ ] Promessas compatíveis com a realidade da oferta

---

**Nota:** A ferramenta de IA é etapa de rascunho. A revisão editorial é responsabilidade do operador do manual.
