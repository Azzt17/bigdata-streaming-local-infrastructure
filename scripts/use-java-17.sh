#!/usr/bin/env bash
set -euo pipefail

JAVA_17_HOME="$(find /usr/lib/jvm -maxdepth 1 -type d -iname '*17*' | head -n 1)"

if [[ -z "$JAVA_17_HOME" ]]; then
  echo "Java 17 installation not found under /usr/lib/jvm"
  exit 1
fi

export JAVA_HOME="$JAVA_17_HOME"
export PATH="$JAVA_HOME/bin:$PATH"

java -version
echo "JAVA_HOME=$JAVA_HOME"
