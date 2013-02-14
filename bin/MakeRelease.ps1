param([switch]$Release)

$script:thisDir = split-path $MyInvocation.MyCommand.Path -parent

$mainDir = resolve-path (join-path $thisDir "..")
$distDir = join-path $mainDir "dist"


$includeFiles = @(
        "*.py",
        "*.sublime-keymap",
        "LICENSE.txt",
        "README.md"
    )

$excludeFiles = @(
        "test_runner.py"
    )

$includeDirs = @(
        "vi",
        "tests"
    )

$excludeDirs = @(
        "tests"
    )


if (test-path $distDir) {remove-item $distDir -recurse -force}

push-location $mainDir
    if (-not (test-path $distDir)) {[void] (new-item -itemtype 'd' $distDir)}

    $includeFiles | foreach-object { get-childitem $_ } | foreach-object { copy-item $_ $distDir }
    copy-item $includeDirs $distDir -recurse

    if ($Release) {
        get-childitem "$distDir/*" -include $excludeFiles -recurse | remove-item
        $excludeDirs | foreach-object { get-childitem $distDir -Attribute Directory -filter $_ } | remove-item -recurse
    }

    push-location $distDir
        & "7z.exe" "a" "-r" "-tzip" "Vintageous.sublime-package" "."
    pop-location
pop-location
