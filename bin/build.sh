#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

e=1
if python "$DIR/builder.py"; then
    case "$(uname)" in
        Linux)
            cp -f "$DIR/../dist/Vintageous.sublime-package"\
                "${HOME}/.config/sublime-text-3/Installed Packages"
            e=$?
        ;;
        Darwin)
            cp -f "$DIR/../dist/Vintageous.sublime-package"\
                "${HOME}/Library/Application Support/Sublime Text 3/Installed Packages/"
            e=$?
        ;;
        *)
            echo "Vintageous: no build script for $(uname) :_("
        ;;
    esac
else
    echo "Failed to execute $DIR/builder.py"
    e=2
fi

exit $e
