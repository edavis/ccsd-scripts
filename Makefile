all: 2010-11 2011-12

2010-11: 2010-11/es.csv 2010-11/ms.csv 2010-11/hs.csv
2011-12: 2011-12/es.csv 2011-12/ms.csv 2011-12/hs.csv

###########################################################################

2010-11/es.csv: config/es.2010-11.ini
	cd 2010-11/es; ../../bin/ocr_pdf.py -c ../../config/es.2010-11.ini
	cd 2010-11; ../bin/create_csv.py -t Elementary -c ../config/es.2010-11.ini -o es.csv

2010-11/ms.csv: config/ms.2010-11.ini
	cd 2010-11/ms; ../../bin/ocr_pdf.py -c ../../config/ms.2010-11.ini
	cd 2010-11; ../bin/create_csv.py -t Middle -c ../config/ms.2010-11.ini -o ms.csv

2010-11/hs.csv: config/hs.2010-11.ini
	cd 2010-11/hs; ../../bin/ocr_pdf.py -c ../../config/hs.2010-11.ini
	cd 2010-11; ../bin/create_csv.py -t High -c ../config/hs.2010-11.ini -o hs.csv

###########################################################################

2011-12/es.csv: config/es.2011-12.ini
	cd 2011-12/es; ../../bin/ocr_pdf.py -c ../../config/es.2011-12.ini
	cd 2011-12; ../bin/create_csv.py -t Elementary -c ../config/es.2011-12.ini -o es.csv

2011-12/ms.csv: config/ms.2011-12.ini
	cd 2011-12/ms; ../../bin/ocr_pdf.py -c ../../config/ms.2011-12.ini
	cd 2011-12; ../bin/create_csv.py -t Middle -c ../config/ms.2011-12.ini -o ms.csv

2011-12/hs.csv: config/hs.2011-12.ini
	cd 2011-12/hs; ../../bin/ocr_pdf.py -c ../../config/hs.2011-12.ini
	cd 2011-12; ../bin/create_csv.py -t High -c ../config/hs.2011-12.ini -o hs.csv

###########################################################################

.PHONY: clean
clean:
	rm -f 2010-11/*.csv
	rm -f 2011-12/*.csv
