install:
	# install -m 644 plugin/audit.vim ~/.vim/plugin/
	mkdir -p ~/.vim/plugin
	ln -sf ${PWD}/plugin/audit.vim ~/.vim/plugin/
	mkdir -p ~/.local/bin
	ln -sf ${PWD}/avim.py ~/.local/bin/
