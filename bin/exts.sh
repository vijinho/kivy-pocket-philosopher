# find file extension used in project
find . -type f | grep -v egg| grep -v 'aforgizmo/' | cut -d '.' -f 3 | sort |
uniq  | sort
