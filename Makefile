FILE_LIST = ./.installed_files.txt

.PHONY: pull push clean check install uninstall

default: | pull clean check install

install:
	@ ./setup.py install --record $(FILE_LIST)

uninstall:
	@ while read FILE; do echo "Removing: $$FILE"; rm "$$FILE"; done < $(FILE_LIST)

clean:
	@ rm -Rf ./build

check:
	@ RESULT=true; for FILE in $$(find . -type f -name "*.py" -not -path "./build/*"); do pep8 --hang-closing "$$FILE" || RESULT=false; done; $$RESULT

pull:
	@ git pull

push:
	@ git push
