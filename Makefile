install:
	install -m 644 plugin/audit.vim ~/.vim/plugin/
	ln -sf ${PWD}/avim.py ~/bin/
