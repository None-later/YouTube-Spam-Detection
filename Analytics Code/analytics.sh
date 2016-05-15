echo "Total Number of comments:"
grep -roe "\"z.*\"" ./ | tr ',' '\n' | sort | uniq | wc -l
echo "Total Number of Videos:"
ls -l | wc -l
