python builder.py
case `uname` in
  'Linux')
    cp -f ./dist/Vintageous.sublime-package ~/.config/sublime-text-3/Installed\ Packages
    ;;
  'Darwin')
    cp -f ./dist/Vintageous.sublime-package ~/Library/Application\ Support/Sublime\ Text\ 3/Installed\ Packages
    ;;
esac
