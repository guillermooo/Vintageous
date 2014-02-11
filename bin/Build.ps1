param([switch]$Release)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent

. (join-path $script:thisDir "Config.ps1")

if(!$?){
	write-error "Could not read config."
	exit 1
}

$publishRelease = join-path $script:thisDir "Publish.ps1"


# XXX: Use @boundparams instead?
& $publishRelease -Release:$Release

if ($LASTEXITCODE -ne 0) {
    write-error "Could not publish package."
    exit 1
}

get-process "sublime_text" | stop-process
start-sleep -milliseconds 250
# sss
$editor = (GetConfigValue 'global-win' 'editor')
if(!$?){
	write-error "Could not locate editor command."
	exit 1
}

&$editor
