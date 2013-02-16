param([switch]$Release)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent

$publishRelease = join-path $script:thisDir "Publish.ps1"

get-process "sublime_text" | stop-process

# XXX: Use @boundparams instead?
& $publishRelease -Release:$Release

sss
