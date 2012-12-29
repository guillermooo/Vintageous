& ".\bin\MakeRelease.ps1"

$targetDir = resolve-path "~\Utilities\Sublime Text 3\Data\Installed Packages"

copy-item ".\dist\Vintageous.sublime-package" $targetDir -force

# clean up so that we don't clutter ST's files and folders.
remove-item "dist/*" -exclude "*.sublime-package" -recurse
