#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 path/to/app.aab" >&2; exit 2; fi
AAB="$1"
: "${BUNDLETOOL_JAR:?Set BUNDLETOOL_JAR to bundletool-all.jar}"
config=$(java -jar "$BUNDLETOOL_JAR" dump config --bundle="$AAB")
echo "$config"
grep -q "PAGE_ALIGNMENT_16K" <<<"$config" || { echo "AAB is not 16 KB page aligned" >&2; exit 1; }
echo "AAB reports PAGE_ALIGNMENT_16K. Native .so files must also be checked on the generated APK/device."
