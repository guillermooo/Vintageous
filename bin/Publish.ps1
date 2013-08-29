param([switch]$Release, [switch]$DontUpload)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent
$script:distDir = resolve-path((join-path $thisDir "../dist"))

$typeOfBuild = if ($Release) {"release"} else {"dev"}
# Run with the required Python version.
& "py.exe" "-3.3" (join-path $script:thisDir "..\builder.py") "--release" $typeOfBuild

if ($LASTEXITCODE -ne 0) {
   write-error "Could not run py.exe."
   exit 1
}

$targetDir = resolve-path "~\Utilities\Sublime Text 3\Data\Installed Packages"

copy-item (join-path $distDir "Vintageous.sublime-package") $targetDir -force

if ($Release -and (!$DontUpload)) {
	start-process "https://bitbucket.org/guillermooo/vintageous/downloads"
	($distDir).path | clip.exe
}
