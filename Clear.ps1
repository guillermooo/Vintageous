$targetDir = resolve-path "~\Utilities\Sublime Text 3\Data\Installed Packages"

gci . "*.pyc" -recurse | remove-item
gci . "*.orig" -recurse | remove-item


remove-item "dist" -recurse
remove-item (join-path $targetDir "Vintageous.sublime-package")
