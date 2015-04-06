DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

python $DIR/builder.py

if [ "$(uname)" == "Linux" ]
    then
    cp -f $DIR/../dist/Vintageous.sublime-package ~/.config/sublime-text-3/Installed\ Packages
else
    echo "Vintageous: no build script for $(uname) :_("
fi
