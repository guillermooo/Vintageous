param([switch]$Force)

# This script ensures that we abort pushing if we have unfinzalied Mercurial patches.
#
# hg-git has bug that will break the local repository if we do all the following things:
#	1. we push changes in A.patch to Github without finalizing the patch first
#	2. we make further changes to the patch locally and refresh
#	3. we finalize and push A.patch to Github again
#
# Other requirements so that this script work:
#
# 	1. bb must be defined under [paths] in .hg/hgrc
# 	2. git must be defined under [paths] in .hg/hgrc
# 	3. 'push' must be disabled under [alias] in .hg/hgrc


$patches = (& hg qseries -s -v)
if ($patches) {
    foreach($line in $patches) {
        if ($line -match '^\d+ A ') {
            write-host "Cannot push: unfinalized applied patches:" -foregroundcolor RED
            $line
            exit 1
        }
    }

    if (!$Force) {
        write-host "Cannot push: unfinalized patches (force with -Force):" -foregroundcolor DARKRED
        $patches
        exit 1
    }
}

if (@(& hg bookmarks).length -gt 1) {
	# Normally we just want to have a single branch in this repo before pushing.
	write-host "Cannot push: too many bookmarks" -foregroundcolor RED
	exit
}

# Override .hg/hgrc
"pushing..."
# & hg --config "alias.push=push" push bb
# & hg --config "alias.push=push" push git
