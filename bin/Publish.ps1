param([switch]$Release, [switch]$DontUpload)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent
# Don't resolve-path because it may not exist yet.
$script:distDir = join-path $thisDir "../dist"

. (join-path $script:thisDir "Config.ps1")

if(!$?){
	write-error "Could not read config."
	exit 1
}

& "py.exe" "-3.3" (join-path $script:thisDir "check.py") $typeOfBuild
if ($LASTEXITCODE -ne 0) {
	"publish aborted"
	exit 1
}

$typeOfBuild = if ($Release) {"release"} else {"dev"}
# Run with the required Python version.
& "py.exe" "-3.3" (join-path $script:thisDir "builder.py") "--release" $typeOfBuild

if ($LASTEXITCODE -ne 0) {
   write-error "could not run builder.py"
   exit 1
}

$installedPackages = (GetConfigValue 'global-win' 'installed-packages')
if(!$?){
	throw "Could not retrieve Installed Packages location from confige"
	exit 1
}
$targetDir = resolve-path ($installedPackages)

copy-item (join-path $distDir "Vintageous.sublime-package") $targetDir -force

if ($Release -and (!$DontUpload)) {
	$deployUrl = (GetConfigValue 'project-vintageous' 'deploy-url')
	if(!$?){
		throw "Could not retrieve deploy url from config."
		exit 1
	}
	start-process $deployUrl
	(resolve-path $distDir).path | clip.exe
}
