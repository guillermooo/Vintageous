# Helpers to read files in this format:
#
#	global-win editor path/to/some/bin
#	project-foo deploy-url http://some/url/here
#	...

function GetConfig {
	$path = "~/.sublime-package-dev"

	if(!(test-path $path)){
		write-error "Could not find personal configuration in $path."
		exit 1
	}
	get-content $path
}

$script:configData = GetConfig

function GetConfigValue {
	param($section, $key)
	$section = $section.ToLower()
	$key = $key.ToLower()
	foreach($item in $configData){
		if(!$item.Trim()){
			continue
		}
		$s, $k, $v = $item.ToLower() -split ' ',3
		if(($s -eq $section) -and ($k -eq $key)){
			if(!$v){
				throw "No value found for '${section}:$key'."
			}
			return $v
		}
	}
}
