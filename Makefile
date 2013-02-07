SCRIPTS = bin/create_csv.py bin/ocr_pdf.py

csv/hs.csv: config/hs.ini $(SCRIPTS)
	cd 2011-12/hs/; ../../bin/ocr_pdf.py -c ../../config/hs.ini
	./bin/create_csv.py -t High -c config/hs.ini -o csv/hs.csv

csv/ms.csv: config/ms.ini
	cd 2011-12/ms/; ../../bin/ocr_pdf.py -c ../../config/ms.ini
	./bin/create_csv.py -t Middle -c config/ms.ini -o csv/ms.csv

csv/es.csv: config/es.ini
	cd 2011-12/es/; ../../bin/ocr_pdf.py -c ../../config/es.ini
	./bin/create_csv.py -t Elementary -c config/es.ini -o csv/es.csv
