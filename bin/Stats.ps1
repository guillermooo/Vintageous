# Gather some metrics about this project.

push-location $PSSCriptRoot\..
	$code = get-content (
		get-childitem . *.py -recurse |
			select-object -expandproperty fullname) |
				select-string -notmatch "^\s*#" |
					measure-object -line

	write-output "SLOC (Application): $($code.lines - $tests.lines)"

	$comments = get-content (
		get-childitem . *.py -recurse |
			select-object -expandproperty fullname) |
				select-string "^\s*#" |
					measure-object -line

	write-output "SLOC (Comments): $($comments.lines)"

	$tests = get-content (
		get-childitem .\tests *.py -recurse |
			select-object -expandproperty fullname) |
				select-string -notmatch "^\s*#" |
					measure-object -line
					
	write-output "SLOC (Tests): $($tests.lines)"
pop-location

write-output "-----------------------------------------------"
write-output "SLOC (Total): $($code.lines + $comments.lines)"
