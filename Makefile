FILE_LIST = ./.installed_files.txt
ECHO = /bin/echo -e

install:
	@ ./setup.py install --record $(FILE_LIST)

uninstall:
	@ while read FILE; do
		rm "${FILE}"
	done < ${FILE_LIST}
	
clean:
	@ rm -R ./build 

all:
	@ $(ECHO) "Nothing to do here.\nTry 'make install'"