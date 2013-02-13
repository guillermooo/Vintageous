param([switch]$IncludeTests)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent

$mainDir = resolve-path (join-path $thisDir "..")
$distDir = join-path $mainDir "dist"


$includeFiles = @(
        "*.py",
        "*.sublime-keymap"
    )


$includeDirs = @(
        "vi"
    )


if ($IncludeTests) {
    $includeDirs += @("tests")    
}


if (test-path $distDir) {remove-item $distDir -recurse -force}

push-location $mainDir
    if (-not (test-path $distDir)) {[void] (new-item -itemtype 'd' $distDir)}

    $includeFiles | foreach-object { get-childitem $_ } | foreach-object { copy-item $_ $distDir }
    copy-item $includeDirs $distDir -recurse

    push-location $distDir
        & "7z.exe" "a" "-r" "-tzip" "Vintageous.sublime-package" "."
    pop-location
pop-location
