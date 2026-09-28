#!/usr/bin/env bash
# Gera PNGs dos diagramas PlantUML em docs/diagramas/img
# Uso: ./scripts/gerar-diagramas.sh   (requer Java; baixa o plantuml.jar se necessario)
set -e
cd "$(dirname "$0")/.."
JAR="plantuml.jar"
if [ ! -f "$JAR" ]; then
  echo "Baixando plantuml.jar..."
  curl -L -o "$JAR" https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar
fi
java -jar "$JAR" -tpng -o img docs/diagramas/*.puml
echo "Imagens geradas em docs/diagramas/img/"
