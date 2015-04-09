# Gather some metrics about this project.

push-location $PSSCriptRoot\..
	$code = get-content (
		get-childitem . *.py -recurse |
			select-object -expandproperty fullname) |
				select-string -notmatch "^\s*#" |
					measure-object -line


	$comments = get-content (
		get-childitem . *.py -recurse |
			select-object -expandproperty fullname) |
				select-string "^\s*#" |
					measure-object -line


	$tests = get-content (
		get-childitem .\tests *.py -recurse |
			select-object -expandproperty fullname) |
				select-string -notmatch "^\s*#" |
					measure-object -line

pop-location

write-output "-----------------------------------------------"
write-output "SLOC (Application): $($code.lines - $tests.lines)"
write-output "SLOC (Tests): $($tests.lines)"
write-output "SLOC (Comments): $($comments.lines)"
write-output "SLOC (Total): $($code.lines + $comments.lines)"
