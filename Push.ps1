# This script ensures that we abort pushing if we have unfinzalied Mercurial patches.
#
# hg-git has bug that will break the local repository if we do all the following things:
#	1. we push changes in A.patch to Github without finalizing the patch first
#	2. we make further changes to the patch locally and refresh
#	3. we finalize and push A.patch to Github again

if (& hg qseries) {
	write-host "Cannot push: unfinalized patches!" -foregroundcolor RED
	exit
}

# Override .hg/hgrc
& hg --config "alias.push=push" push bb
& hg --config "alias.push=push" push git
