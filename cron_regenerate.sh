#!/usr/bin/env bash

MYDIR=$(dirname $0)
#FIDOCDIR=/var/www/fidoc

#rm $MYDIR/_generated/*.*
#cd $MYDIR && python3 run-jobs.py docxgeneration.json
#cp $MYDIR/_generated/d*-generated.docx $FIDOCDIR/docx/

rm $MYDIR/_catalog/*.*
cd $MYDIR && python3 run-jobs.py update-catalog.json
#cd $MYDIR/_catalog && tar cf catalog-thumb.tar *.png *.jpg
#cd $MYDIR/_catalog && tar cf catalog-json.tar catalog.*.json

#rm $FIDOCDIR/catalog/*.*
#cp $MYDIR/_catalog/*.* $FIDOCDIR/catalog/

./cron_postprocessing.sh


