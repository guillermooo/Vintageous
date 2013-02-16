param([switch]$Release, [switch]$DontUpload)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent
$script:distDir = resolve-path((join-path $thisDir "../dist"))

& (join-path $script:thisDir ".\MakeRelease.ps1") -Release:$Release

$targetDir = resolve-path "~\Utilities\Sublime Text 3\Data\Installed Packages"

copy-item (join-path $distDir "Vintageous.sublime-package") $targetDir -force

# clean up so that we don't clutter ST's files and folders.
remove-item "$distDir/*" -exclude "*.sublime-package" -recurse

if ($Release -and (! $DontUpload)) {
	start-process "https://bitbucket.org/guillermooo/vintageous/downloads"
	($distDir).path | clip.exe
}
