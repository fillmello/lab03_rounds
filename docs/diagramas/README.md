# Diagramas UML (PlantUML)

| Arquivo | Descrição |
|---------|-----------|
| `casos-de-uso.puml` | Diagrama de Casos de Uso |
| `diagrama-de-classes.puml` | Diagrama de Classes |
| `diagrama-de-componentes.puml` | Diagrama de Componentes |
| `modelo-er.puml` | Modelo Entidade-Relacionamento |
| `sequencia-enviar-moedas.puml` | Sequência do envio de moedas (apoio, Sprint 2/3) |
| `sequencia-trocar-vantagem.puml` | Sequência da troca por vantagem (apoio, Sprint 2/3) |

## Como visualizar

**Online (sem instalar nada):** copie o conteúdo de um `.puml` em <https://plantuml.online/> ou <https://www.planttext.com/>.

**VS Code:** extensão *PlantUML* (jebbs) e `Alt+D` para pré-visualizar.

**Linha de comando (gera PNGs em `img/`):**

```bash
# requer Java. Baixe o plantuml.jar em https://plantuml.com/download
java -jar plantuml.jar -tpng -o img *.puml
# ou SVG:
java -jar plantuml.jar -tsvg -o img *.puml
```

Ou use o script da raiz: `./scripts/gerar-diagramas.sh`

## Fluxo recomendado de versionamento

Sempre que um modelo for atualizado, commite **o `.puml` e a imagem gerada** para manter o histórico de versões exigido no enunciado.
