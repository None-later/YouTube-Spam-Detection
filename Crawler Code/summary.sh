echo "Running Processes:"
ps aux | grep 508 | grep python
echo "Number of distinct youtube videos:"
echo `cat videoIds_per6hrs.txt | sort | uniq | wc -l`
echo -e "\nNumber of Videos whose CommentIds have been crawled:"
echo `ls -l CommentIds/ | wc -l`
echo -e "Last VideoId whose commentIds was crawled:"
echo `ls -l CommentIds/ | tail -n1`
echo -e "\nNumber of Videos whosr Comments and Replies have been crawled:"
echo `ls -l CommentsandReplies/ | wc -l`
echo -e "Last VideoId whose Comments and Replies was crawled:"
echo `ls -l CommentsandReplies/ | tail -n1`
echo 
