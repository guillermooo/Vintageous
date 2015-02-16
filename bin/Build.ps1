param([switch]$Release, [switch]$NoRestartEditor=$False)

push-location $PSScriptRoot
    . '.\Config.ps1'
    if(!$?){
        write-error "Could not read config."
        exit 1
    }
pop-location

push-location "$PSScriptRoot\.."
& (join-path $PSScriptRoot '.\Publish.ps1') @PSBoundParameters
if ($LASTEXITCODE -ne 0) {
    write-error "Could not publish package."
    pop-location
    exit 1
}
pop-location

if ($NoRestartEditor) { exit 0 }

get-process "sublime_text" -ea silentlycontinue | stop-process
write-output "Trying to restart Sublime Text..."
start-sleep -milliseconds 250

$editor = (GetConfigValue 'global-win' 'editor')
if(!$?){
    write-error "Could not locate editor command."
    exit 1
}

&$editor
